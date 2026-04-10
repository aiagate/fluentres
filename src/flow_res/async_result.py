import inspect
from collections.abc import Awaitable, Callable, Coroutine, Generator
from functools import wraps
from typing import Any

from .result import Err, Ok, Result


class AwaitableResult[T, E: Exception]:
    """
    Awaitable wrapper for Result that enables method chaining before await.

    This allows elegant syntax like:
        message = await Mediator.send_async(query).map(...).unwrap()
    """

    def __init__(self, coro: Coroutine[Any, Any, Result[T, E]]) -> None:
        """
        Initialize with a coroutine that returns a Result.

        Args:
            coro: Coroutine that will return Result[T, E]
        """
        self._coro = coro

    def __repr__(self) -> str:
        """Return a helpful representation for debugging.

        Shows the wrapped coroutine's repr to aid debugging without awaiting.
        """
        try:
            coro_repr = repr(self._coro)
        except Exception:
            coro_repr = "<unreprable coroutine>"
        return f"ResultAwaitable(coro={coro_repr})"

    def __await__(self) -> Generator[Any, None, Result[T, E]]:
        """Make this object awaitable, returning the underlying Result."""
        return self._coro.__await__()

    def map[U](self, f: Callable[[T], U]) -> "AwaitableResult[U, E]":
        """
        Transform the Ok value using the provided function.

        This method chains onto the coroutine, creating a new coroutine that:
        1. Awaits the current Result
        2. Applies .map() to transform the value
        3. Returns the transformed Result

        Args:
            f: Function to apply to the Ok value (T -> U)

        Returns:
            ResultAwaitable[U, E] wrapping the transformed result

        Example:
            user_id = await Mediator.send_async(cmd).map(lambda v: v.user_id)
        """

        async def mapped() -> Result[U, E]:
            _result: Result[T, E] = await self
            return _result.map(f)

        return AwaitableResult(mapped())

    def and_then[U](
        self, f: Callable[[T], Awaitable[Result[U, E]] | Result[U, E]]
    ) -> "AwaitableResult[U, E]":
        """
        Apply a function (sync or async) that returns a Result, flattening the nested Result.

        This enables chaining operations that may fail.

        Args:
            f: Function that takes the Ok value and returns a new Result
               (T -> Awaitable[Result[U, E]] | Result[U, E])

        Returns:
            ResultAwaitable[U, E] wrapping the result of applying the function

        Example:
            await (
                Mediator.send_async(create_cmd)
                .and_then(lambda result: Mediator.send_async(GetQuery(result.id)))
                .map(lambda value: format_message(value))
                .unwrap()
            )
        """

        async def chained() -> Result[U, E]:
            _result: Result[T, E] = await self
            match _result:
                case Ok(value):
                    res = f(value)
                    if inspect.isawaitable(res):
                        return await res
                    return res
                case Err():
                    return _result

        return AwaitableResult(chained())

    def unwrap(self) -> Awaitable[T]:
        """
        Return the Ok value or raise the Err as an exception.

        This is a terminal operation that unwraps the Result.

        Returns:
            Awaitable[T] that will return the value or raise the error

        Example:
            message = await Mediator.send_async(query).map(...).unwrap()
        """

        async def unwrapped() -> T:
            _result: Result[T, E] = await self
            return _result.unwrap()

        return unwrapped()

    def map_err[F: Exception](self, f: Callable[[E], F]) -> "AwaitableResult[T, F]":
        """
        Transform the error value using the provided function asynchronously.

        Args:
            f: Function to apply to the error value (E -> F)

        Returns:
            ResultAwaitable[T, F] wrapping the result with transformed error type

        Example:
            await (
                Mediator.send_async(cmd)
                .map_err(lambda e: DatabaseError(f"DB error: {e}"))
                .unwrap()
            )
        """

        async def mapped() -> Result[T, F]:
            _result = await self
            return _result.map_err(f)

        return AwaitableResult(mapped())


def async_result[T, E: Exception](
    func: Callable[..., Coroutine[Any, Any, Result[T, E]]],
) -> Callable[..., AwaitableResult[T, E]]:
    """
    Decorator that wraps an async function returning Result in AwaitableResult.

    This allows async functions to return Result types while automatically
    wrapping them in AwaitableResult for method chaining (.map, .and_then, etc.)

    The decorated function must be async and return a Result. The decorator
    will wrap the coroutine in AwaitableResult, allowing method chaining without
    an explicit await.

    Args:
        func: An async function that returns Result[T, E]

    Returns:
        A wrapped function that returns AwaitableResult[T, E]

    Example:
        @async_result
        async def fetch_user(user_id: int) -> Result[dict, Exception]:
            if user_id < 0:
                return Err(ValueError("Invalid user ID"))
            return Ok({"id": user_id})

        # Can now use method chaining without await:
        result = fetch_user(1).map(lambda u: u["id"]).map(str.upper)
        print(await result)  # Ok({"id": 1})
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> AwaitableResult[T, E]:
        return AwaitableResult(
            coro=func(*args, **kwargs),
        )

    return wrapper
