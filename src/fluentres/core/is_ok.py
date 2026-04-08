from typing_extensions import TypeIs

from ..result import Ok, Result


def is_ok[T, E: Exception](result: Result[T, E]) -> TypeIs[Ok[T]]:
    """
    Return true if the result is ok.

    Uses TypeIs for bidirectional type narrowing - when this returns False,
    the type checker knows the result must be Err.
    """
    return isinstance(result, Ok)
