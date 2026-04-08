from typing_extensions import TypeIs

from ..result import Err, Result


def is_err[T, E: Exception](result: Result[T, E]) -> TypeIs[Err[E]]:
    """
    Return true if the result is an error.

    Uses TypeIs for bidirectional type narrowing - when this returns False,
    the type checker knows the result must be Ok.
    """
    return isinstance(result, Err)
