from collections.abc import Sequence
from typing import Any, overload

from ..core.is_err import is_err
from ..result import Ok, Result


@overload
def combine[E: Exception](results: tuple[()]) -> Result[tuple[()], E]: ...


@overload
def combine[T1, E: Exception](
    results: tuple[Result[T1, E]],
) -> Result[tuple[T1], E]: ...


@overload
def combine[T1, T2, E: Exception](
    results: tuple[Result[T1, E], Result[T2, E]],
) -> Result[tuple[T1, T2], E]: ...


@overload
def combine[T1, T2, T3, E: Exception](
    results: tuple[Result[T1, E], Result[T2, E], Result[T3, E]],
) -> Result[tuple[T1, T2, T3], E]: ...


@overload
def combine[T1, T2, T3, T4, E: Exception](
    results: tuple[Result[T1, E], Result[T2, E], Result[T3, E], Result[T4, E]],
) -> Result[tuple[T1, T2, T3, T4], E]: ...


@overload
def combine[T1, T2, T3, T4, T5, E: Exception](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5], E]: ...


@overload
def combine[T1, T2, T3, T4, T5, T6, E: Exception](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6], E]: ...


@overload
def combine[T1, T2, T3, T4, T5, T6, T7, E: Exception](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
        Result[T7, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7], E]: ...


@overload
def combine[T1, T2, T3, T4, T5, T6, T7, T8, E: Exception](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
        Result[T7, E],
        Result[T8, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7, T8], E]: ...


@overload
def combine[T1, T2, T3, T4, T5, T6, T7, T8, T9, E: Exception](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
        Result[T7, E],
        Result[T8, E],
        Result[T9, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9], E]: ...


@overload
def combine[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, E: Exception](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
        Result[T7, E],
        Result[T8, E],
        Result[T9, E],
        Result[T10, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], E]: ...


def combine[E: Exception](
    results: Sequence[Result[Any, E]],
) -> Result[tuple[Any, ...], E]:
    """
    Aggregates a sequence of Result objects.

    If all results are Ok, returns an Ok containing a tuple of all success values.
    If any result is an Err, returns the first Err encountered.

    Args:
        results: A sequence of Result objects.

    Returns:
        A single Result object. Ok(tuple of success values) or the first Err.

    Examples:
        Heterogeneous types (use tuple):
        >>> user_id: Result[int, Exception] = Ok(123)
        >>> email: Result[str, Exception] = Ok("user@example.com")
        >>> combine((user_id, email))
        Ok((123, "user@example.com"))

        Homogeneous types (use list or tuple):
        >>> results = [Ok(1), Ok(2), Ok(3)]
        >>> combine(results)
        Ok((1, 2, 3))

        Error handling (first error returned):
        >>> results = [Ok(1), Err(Exception("error")), Ok(3)]
        >>> combine(results)
        Err(Exception("error"))
    """
    values: list[Any] = []
    for r in results:
        if is_err(r):
            return r  # Return the first error found
        values.append(r.unwrap())
    return Ok(tuple(values))
