"""Generic Result type, inspired by Rust's Result type."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AggregateErr[E](Exception):
    """
    Represents multiple errors collected during a validation process.

    Used primarily with combine_all to collect all validation errors
    so users can see all issues at once, rather than one at a time.
    """

    exceptions: list[E]

    def __str__(self) -> str:
        """Return a string representation of the aggregate error."""
        return f"Multiple errors occurred ({len(self.exceptions)}): {self.exceptions}"
