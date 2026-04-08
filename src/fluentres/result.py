"""Generic Result type, inspired by Rust's Result type."""

from collections.abc import Awaitable, Callable, Coroutine, Generator
from dataclasses import dataclass
from typing import Any, Never, TypeVar

T = TypeVar("T")  # Success type
E = TypeVar("E", bound=Exception)  # Error type
U = TypeVar("U")  # Success type for map/and_then


@dataclass(frozen=True)
class Ok[T]:
    """Represents a successful result."""

    value: T

    def map[V](self, f: Callable[[T], V]) -> "Ok[V]":
        """
        Transform the Ok value using the provided function.

        Args:
            f: Function to apply to the Ok value (T -> V)

        Returns:
            Ok[V] containing the transformed value

        Example:
            Ok(5).map(lambda x: x * 2)  # Returns Ok(10)
        """
        return Ok(f(self.value))

    def and_then[V, F: Exception](
        self, f: Callable[[T], "Result[V, F]"]
    ) -> "Result[V, F]":
        """
        Apply a function that returns a Result, flattening the nested Result.

        This is the monadic bind operation (flatMap in some languages).
        Enables chaining operations that may fail.

        Args:
            f: Function that takes the Ok value and returns a new Result (T -> Result[V, F])

        Returns:
            Result[V, F] - The result of applying the function

        Example:
            Ok(5).and_then(lambda x: Ok(x * 2))  # Returns Ok(10)
            Ok(5).and_then(lambda x: Err(Exception("failed")))  # Returns Err(Exception("failed"))
        """
        return f(self.value)

    def unwrap(self) -> T:
        """
        Return the Ok value.

        Returns:
            The wrapped value
        """
        return self.value

    def expect(self, msg: str) -> T:
        """
        Return the value.

        Compatible with Err.expect signature to allow usage without type guards,
        but requires a message explaining why success is expected.

        Args:
            msg: Message explaining why this Result is expected to be Ok (for consistency)

        Returns:
            The wrapped value
        """
        return self.value

    def map_err[F: Exception](self, f: Callable[[Any], F]) -> "Ok[T]":
        """
        Pass through the Ok value unchanged.

        Args:
            f: Function to map error (ignored for Ok).

        Returns:
            Self (unchanged Ok value).
        """
        return self


@dataclass(frozen=True)
class Err[E: Exception]:
    """Represents a failure result."""

    error: E

    def map[V](self, f: Callable[[Any], Any]) -> "Err[E]":
        """
        Pass through the error unchanged (Railway-oriented programming pattern).

        Args:
            f: Function that would be applied (ignored for Err)

        Returns:
            Self (unchanged Err)
        """
        return self

    def and_then[V, F: Exception](self, f: Callable[[Any], "Result[V, F]"]) -> "Err[E]":
        """
        Pass through the error unchanged (Railway-oriented programming pattern).

        Since this is an Err, the function is not called and the error propagates.

        Args:
            f: Function that would be applied (ignored for Err)

        Returns:
            Self (unchanged Err)

        Example:
            Err(Exception("error")).and_then(lambda x: Ok(x * 2))  # Returns Err(Exception("error"))
        """
        return self

    def expect(self, msg: str) -> Never:
        """
        Raise an exception with the provided message.

        Used when you want to assert that this Result should be Ok.
        Requires a message explaining why the Result was expected to be Ok.

        Args:
            msg: Message explaining why this was expected to be Ok

        Raises:
            RuntimeError: Always raised with the provided message and underlying error

        Example:
            result.expect("User should exist in database")
        """
        raise RuntimeError(f"{msg}: {self.error}") from self.error

    def map_err[F: Exception](self, f: Callable[[E], F]) -> "Err[F]":
        """
        Transform the Err value using the provided function.

        Args:
            f: Function to apply to the Err value (E -> F).

        Returns:
            Err[F] containing the transformed error.
        """
        return Err(f(self.error))

    def unwrap(self) -> Never:
        """
        Raise the underlying error.

        This ensures that unwrap() can be called on Result (Ok | Err).
        """
        raise self.error

    def unwrap_or[T](self, default: T) -> T:
        """
        Return the default value.

        Args:
            default: Value to return.

        Returns:
            The default value.
        """
        return default


Result = Ok[T] | Err[E]


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

    def map(self, f: Callable[[T], U]) -> "AwaitableResult[U, E]":
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

    def and_then(
        self, f: Callable[[T], Awaitable[Result[U, E]]]
    ) -> "AwaitableResult[U, E]":
        """
        Apply an async function that returns a Result, flattening the nested Result.

        This enables chaining async operations that may fail.

        Args:
            f: Async function that takes the Ok value and returns a new Result
               (T -> Awaitable[Result[U, E]])

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
                    return await f(value)
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
            _result: Result[T, E] = await self
            return _result.map_err(f)

        return AwaitableResult(mapped())
