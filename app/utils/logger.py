# app/utils/logger.py

import inspect
import logging

from colorama import Fore, Style, init

from app.config import settings

init(autoreset=True)

COLORS = {
    "debug": Fore.WHITE,
    "info": Fore.CYAN,
    "warning": Fore.YELLOW,
    "error": Fore.RED,
    "critical": Fore.MAGENTA,
}

RESET = Style.RESET_ALL

logger = logging.getLogger("uvicorn")
logger.setLevel(settings.LOG_LEVEL)


for level in ("debug", "info", "warning", "error", "critical"):
    orig = getattr(logger, level)
    level_color = COLORS[level]

    def _make_wrapper(orig_func, level_color):
        def wrapper(msg, *args, **kwargs):
            frame = inspect.currentframe().f_back
            filename = frame.f_globals.get("__file__", "<unknown>")
            app_idx = filename.find("app/")
            if app_idx != -1:
                filename = "/" + filename[app_idx:]

            colored_filename = f"{Style.BRIGHT}{Fore.MAGENTA}{filename}:{RESET}"
            colored_msg = f"{level_color}{msg}{RESET}"

            text = f"{colored_filename} {colored_msg}"
            return orig_func(text, *args, **kwargs)

        return wrapper

    setattr(logger, level, _make_wrapper(orig, level_color))
