import inspect
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, Protocol, overload

from .result import Err, Ok, Result


class _SafeDecorator(Protocol):
    """Type-preserving decorator returned by ``safe(...)``."""

    @overload
    def __call__[**P, T](  # pyright: ignore[reportOverlappingOverload]
        self, func: Callable[P, Coroutine[Any, Any, T]], /
    ) -> Callable[P, Coroutine[Any, Any, Result[T, Exception]]]: ...

    @overload
    def __call__[**P, T](
        self, func: Callable[P, T], /
    ) -> Callable[P, Result[T, Exception]]: ...


@overload
def safe(*exceptions: type[Exception]) -> _SafeDecorator: ...


@overload
def safe[**P, T](  # pyright: ignore[reportOverlappingOverload]
    __func: Callable[P, Coroutine[Any, Any, T]], /
) -> Callable[P, Coroutine[Any, Any, Result[T, Exception]]]: ...


@overload
def safe[**P, T](__func: Callable[P, T], /) -> Callable[P, Result[T, Exception]]: ...


def safe(*args: Any) -> Any:
    """Convert exceptions raised by a function into ``Result`` values.

    The decorator preserves the decorated function's parameter signature. It may be
    used as ``@safe`` to catch every ``Exception``, or with exception classes such as
    ``@safe(ValueError, TypeError)``. Async functions remain async; their body is
    awaited inside the exception handler before an ``Ok`` or ``Err`` is returned.
    """
    if (
        len(args) == 1
        and callable(args[0])
        and not (isinstance(args[0], type) and issubclass(args[0], Exception))
    ):
        return _wrap(args[0], (Exception,))

    exceptions = args if args else (Exception,)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return _wrap(func, exceptions)

    return decorator


def _wrap(
    func: Callable[..., Any], exceptions: tuple[type[Exception], ...]
) -> Callable[..., Any]:
    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Result[Any, Exception]:
            try:
                return Ok(await func(*args, **kwargs))
            except exceptions as error:
                return Err(error)

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Result[Any, Exception]:
        try:
            return Ok(func(*args, **kwargs))
        except exceptions as error:
            return Err(error)

    return sync_wrapper
