from collections.abc import Sequence
from typing import Any, overload

from ..core.is_err import is_err
from ..error.aggregate_err import AggregateErr
from ..result import Err, Ok, Result


@overload
def combine_all[T1, E: Exception](
    results: tuple[Result[T1, E]],
) -> Result[tuple[T1], AggregateErr[E]]: ...


@overload
def combine_all[T1, T2, E: Exception](
    results: tuple[Result[T1, E], Result[T2, E]],
) -> Result[tuple[T1, T2], AggregateErr[E]]: ...


@overload
def combine_all[T1, T2, T3, E: Exception](
    results: tuple[Result[T1, E], Result[T2, E], Result[T3, E]],
) -> Result[tuple[T1, T2, T3], AggregateErr[E]]: ...


@overload
def combine_all[T1, T2, T3, T4, E: Exception](
    results: tuple[Result[T1, E], Result[T2, E], Result[T3, E], Result[T4, E]],
) -> Result[tuple[T1, T2, T3, T4], AggregateErr[E]]: ...


@overload
def combine_all[T1, T2, T3, T4, T5, E: Exception](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5], AggregateErr[E]]: ...


@overload
def combine_all[T1, T2, T3, T4, T5, T6, E: Exception](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6], AggregateErr[E]]: ...


@overload
def combine_all[T1, T2, T3, T4, T5, T6, T7, E: Exception](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
        Result[T7, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7], AggregateErr[E]]: ...


@overload
def combine_all[T1, T2, T3, T4, T5, T6, T7, T8, E: Exception](
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
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7, T8], AggregateErr[E]]: ...


@overload
def combine_all[T1, T2, T3, T4, T5, T6, T7, T8, T9, E: Exception](
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
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9], AggregateErr[E]]: ...


@overload
def combine_all[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, E: Exception](
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
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], AggregateErr[E]]: ...


def combine_all[E: Exception](
    results: Sequence[Result[Any, E]],
) -> Result[tuple[Any, ...], AggregateErr[E]]:
    """
    Aggregates a tuple of Results, collecting all errors.

    If all results are Ok, returns an Ok containing a tuple of all success values.
    If any result is an Err, returns an Err containing an AggregateErr with all errors.

    This is a "fail complete" strategy - useful for validation where you want to show
    all errors to the user at once, rather than one at a time.

    Args:
        results: A tuple of Result objects.

    Returns:
        Ok(tuple of success values) if all succeed,
        or Err(AggregateErr(list of errors)) if any fail.

    Example:
        >>> from app.core.result import combine_all, Ok, Err
        >>> results = (Ok(1), Err(Exception("error1")), Ok(3), Err(Exception("error2")))
        >>> combined = combine_all(results)
        >>> # Returns Err(AggregateErr([Exception("error1"), Exception("error2")]))
    """
    values: list[Any] = []
    errors: list[E] = []

    for r in results:
        if is_err(r):
            errors.append(r.error)
        else:
            values.append(r.unwrap())

    if errors:
        return Err(AggregateErr(errors))

    return Ok(tuple(values))
