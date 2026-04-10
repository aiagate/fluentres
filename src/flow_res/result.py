"""Generic Result type, inspired by Rust's Result type."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Never


@dataclass(frozen=True)
class Ok[T]:
    """Represents a successful result."""

    value: T
    __match_args__ = ("value",)

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

    def and_then[V, F_Exc: Exception](
        self, f: Callable[[T], "Result[V, F_Exc]"]
    ) -> "Result[V, F_Exc]":
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

    def map_err[F_Exc: Exception](self, f: Callable[[Any], F_Exc]) -> "Ok[T]":
        """
        Pass through the Ok value unchanged.

        Args:
            f: Function to map error (ignored for Ok).

        Returns:
            Self (unchanged Ok value).
        """
        return self

    def unwrap_or[T_Def](self, default: T_Def) -> T | T_Def:
        """
        Return the Ok value.

        Args:
            default: Value to return if Err. (Ignored for Ok)

        Returns:
            The wrapped value.
        """
        return self.value


@dataclass(frozen=True)
class Err[E: Exception = Exception]:
    """Represents a failure result."""

    error: E
    __match_args__ = ("error",)

    def map[V](self, f: Callable[[Any], Any]) -> "Err[E]":
        """
        Pass through the error unchanged (Railway-oriented programming pattern).

        Args:
            f: Function that would be applied (ignored for Err)

        Returns:
            Self (unchanged Err)
        """
        return self

    def and_then[V, F_Exc: Exception](
        self, f: Callable[[Any], "Result[V, F_Exc]"]
    ) -> "Err[E]":
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

    def map_err[F_Exc: Exception](self, f: Callable[[E], F_Exc]) -> "Err[F_Exc]":
        """
        Transform the Err value using the provided function.

        Args:
            f: Function to apply to the Err value (E -> F).

        Returns:
            Err[F] containing the transformed error.
        """
        new_error = f(self.error)
        return Err(new_error)

    def unwrap(self) -> Never:
        """
        Raise the underlying error.

        This ensures that unwrap() can be called on Result (Ok | Err).
        """
        raise self.error

    def unwrap_or[T_Def](self, default: T_Def) -> T_Def:
        """
        Return the default value.

        Args:
            default: Value to return.

        Returns:
            The default value.
        """
        return default


# The main Result type alias
type Result[T, E: Exception = Exception] = Ok[T] | Err[E]
