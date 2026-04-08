from dataclasses import dataclass
from enum import Enum, auto


class ErrType(Enum):
    """Enum for use case error types."""

    NOT_FOUND = auto()
    VALIDATION_ERROR = auto()
    UNEXPECTED = auto()
    CONCURRENCY_CONFLICT = auto()


@dataclass(frozen=True)
class TestErr(Exception):
    """Represents a specific error from a use case."""

    type: ErrType
    message: str

    def __str__(self) -> str:
        """Return message for exception representation."""
        return self.message
