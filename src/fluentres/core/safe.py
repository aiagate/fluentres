from collections.abc import Callable
from functools import wraps
from typing import Any

from ..result import Err, Ok, Result


def safe[T](func: Callable[..., T]) -> Callable[..., Result[T, Exception]]:
    """
    Decorator to convert a function that raises exceptions into one that returns a Result.

    This is inspired by the @safe decorator from dry-python/returns.
    It wraps any exceptions raised by the decorated function into an Err.

    Args:
        func: Function that may raise exceptions

    Returns:
        A wrapped function that returns Result[T, Exception] instead of raising

    Example:
        @safe
        def risky_operation(x: int) -> int:
            if x < 0:
                raise ValueError("Negative number")
            return x * 2

        result = risky_operation(-5)  # Returns Err(ValueError("Negative number"))
        result = risky_operation(5)   # Returns Ok(10)
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Result[T, Exception]:
        try:
            return Ok(func(*args, **kwargs))
        except Exception as e:
            return Err(e)

    return wrapper
