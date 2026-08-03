import inspect
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, Protocol, overload

from .result import Err, Ok, Result


class _SafeDecorator[E: Exception](Protocol):
    """Type-preserving decorator returned by ``safe(...)``."""

    @overload
    def __call__[**P, T](  # pyright: ignore[reportOverlappingOverload]
        self, func: Callable[P, Coroutine[Any, Any, T]], /
    ) -> Callable[P, Coroutine[Any, Any, Result[T, E]]]: ...

    @overload
    def __call__[**P, T](
        self, func: Callable[P, T], /
    ) -> Callable[P, Result[T, E]]: ...


@overload
def safe() -> _SafeDecorator[Exception]: ...


@overload
def safe[E: Exception](
    exception: type[E], /, *exceptions: type[E]
) -> _SafeDecorator[E]: ...


@overload
def safe[**P, T](  # pyright: ignore[reportOverlappingOverload]
    __func: Callable[P, Coroutine[Any, Any, T]], /
) -> Callable[P, Coroutine[Any, Any, Result[T, Exception]]]: ...


@overload
def safe[**P, T](__func: Callable[P, T], /) -> Callable[P, Result[T, Exception]]: ...


def safe(*args: Any) -> Any:
    """Convert exceptions raised by a function into ``Result`` values.

    The decorator preserves the decorated function's parameter signature. It may be
    used as ``@safe`` to intentionally catch every ``Exception`` for backwards
    compatibility, or with exception classes such as ``@safe(ValueError, TypeError)``
    to limit the conversion to known failures. The catch-all form can turn unexpected
    programming errors into ``Err`` values, so production code should generally use
    an explicit exception filter. Exceptions not listed by an explicit filter are
    propagated unchanged. Control-flow exceptions such as ``asyncio.CancelledError``
    are not ``Exception`` subclasses and are therefore never caught by the default.
    Async functions and callable objects with an async ``__call__`` remain async; their
    body is awaited inside the exception handler before an ``Ok`` or ``Err`` is
    returned.
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
    if inspect.iscoroutinefunction(func) or inspect.iscoroutinefunction(
        getattr(func, "__call__", None)
    ):

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
