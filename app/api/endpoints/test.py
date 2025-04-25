# backend/app/api/v1/endpoints/chat.py


import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi import Request as ServerRequest
from fastapi.responses import FileResponse

from app.utils.auth import verify_jwt
from app.utils.logger import logger
from app.utils.response import success_response

PDF_STORAGE_DIR = Path("pdf_storage")
PDF_STORAGE_DIR.mkdir(exist_ok=True)

router = APIRouter()


@router.get("/test")
async def chat(
    request: ServerRequest, response: Response, user: dict = Depends(verify_jwt)
):
    logger.info("Test endpoint")
    logger.debug(user)
    return success_response(message="Test endpoint")


@router.post("/compile")
async def compile(request: ServerRequest, response: Response):
    body = await request.json()
    latex_code = body["latex_code"]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    persisted_pdf_path = PDF_STORAGE_DIR / f"document_{timestamp}.pdf"

    with tempfile.TemporaryDirectory() as tmpdir:
        host_tex_path = os.path.join(tmpdir, "document.tex")
        host_pdf_path = os.path.join(tmpdir, "document.pdf")

        with open(host_tex_path, "w") as f:
            f.write(latex_code)

        try:
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--platform",
                    "linux/amd64",
                    "-v",
                    f"{tmpdir}:/data",
                    "-w",
                    "/data",
                    "blang/latex:ctanfull",
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "document.tex",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            logger.info(f"LaTeX compilation output: {result.stdout}")
            if result.stderr:
                logger.warning(f"LaTeX compilation warnings: {result.stderr}")

            if not os.path.exists(host_pdf_path):
                raise HTTPException(
                    status_code=400,
                    detail="PDF file was not generated after LaTeX compilation.",
                )

            shutil.copy2(host_pdf_path, persisted_pdf_path)
            logger.info(f"PDF saved to: {persisted_pdf_path}")

            # Return the PDF
            return FileResponse(
                str(persisted_pdf_path),
                media_type="application/pdf",
                filename="document.pdf",
            )

        except subprocess.CalledProcessError as e:
            error_message = f"LaTeX compilation failed: {str(e)}\nOutput: {e.stdout}\nError: {e.stderr}"
            logger.error(error_message)
            raise HTTPException(status_code=400, detail=error_message)
