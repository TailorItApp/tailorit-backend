# app/utils/decorators.py

from functools import wraps
from typing import Any, Callable, TypeVar

from app.utils.exceptions import DatabaseError, NotFoundError
from app.utils.logger import logger

T = TypeVar("T")


def db_error_handler(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    # Call the original function with all its arguments,
    # If it works, then return the result
    # If it doesn't, then raise an error
    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
        except (DatabaseError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise DatabaseError(
                f"Database operation failed in {func.__name__}",
                details={"error": str(e)},
            )

    return wrapper
