from collections.abc import Callable
from functools import wraps
from typing import Any, overload

from .result import Err, Ok, Result


@overload
def safe(
    *exceptions: type[Exception],
) -> Callable[[Callable[..., Any]], Callable[..., Result[Any, Exception]]]: ...


@overload
def safe[T](__func: Callable[..., T]) -> Callable[..., Result[T, Exception]]: ...


def safe(*args: Any) -> Any:
    """
    Decorator to convert a function that raises exceptions into one that returns a Result.

    Can be used without arguments to catch all Exceptions, or with specific exception types
    to only catch those.

    Args:
        *args: Either a single function (when used as @safe), or one or more Exception types
               (when used as @safe(ValueError, TypeError)).

    Returns:
        A wrapped function that returns Result[T, Exception] instead of raising

    Example:
        @safe
        def risky_operation(x: int) -> int:
            if x < 0:
                raise ValueError("Negative number")
            return x * 2

        @safe(ValueError, TypeError)
        def parse_data(data: dict) -> int:
            return int(data["value"])
    """
    if (
        len(args) == 1
        and callable(args[0])
        and not (isinstance(args[0], type) and issubclass(args[0], Exception))
    ):
        # Called as @safe without parentheses
        func = args[0]
        exceptions = (Exception,)

        @wraps(func)
        def wrapper(*w_args: Any, **w_kwargs: Any) -> Result[Any, Exception]:
            try:
                return Ok(func(*w_args, **w_kwargs))
            except exceptions as e:
                return Err(e)

        return wrapper

    # Called as @safe(ValueError, TypeError)
    exceptions = args if args else (Exception,)

    def decorator(func: Callable[..., Any]) -> Callable[..., Result[Any, Exception]]:
        @wraps(func)
        def wrapper(*w_args: Any, **w_kwargs: Any) -> Result[Any, Exception]:
            try:
                return Ok(func(*w_args, **w_kwargs))
            except exceptions as e:
                return Err(e)

        return wrapper

    return decorator
