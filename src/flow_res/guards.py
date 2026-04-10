from typing import TypeIs

from .result import Err, Ok, Result


def is_ok[T, E: Exception = Exception](result: Result[T, E]) -> TypeIs[Ok[T]]:
    """
    Return true if the result is ok.

    Uses TypeIs for bidirectional type narrowing - when this returns False,
    the type checker knows the result must be Err.
    """
    return isinstance(result, Ok)


def is_err[T, E: Exception = Exception](result: Result[T, E]) -> TypeIs[Err[E]]:
    """
    Return true if the result is an error.

    Uses TypeIs for bidirectional type narrowing - when this returns False,
    the type checker knows the result must be Ok.
    """
    return isinstance(result, Err)
