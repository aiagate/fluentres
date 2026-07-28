import re
from pathlib import Path

import pytest

README_PATH = Path(__file__).parents[1] / "README.md"


def _python_examples() -> list[tuple[int, str]]:
    readme = README_PATH.read_text(encoding="utf-8")
    examples: list[tuple[int, str]] = []
    for match in re.finditer(r"```python\s*\n(.*?)```", readme, re.DOTALL):
        line_number = readme.count("\n", 0, match.start(1)) + 1
        examples.append((line_number, match.group(1)))
    return examples


PYTHON_EXAMPLES = _python_examples()


def test_readme_contains_python_examples() -> None:
    """Fail explicitly if extraction stops finding the documented examples."""

    assert PYTHON_EXAMPLES


@pytest.mark.parametrize(
    ("line_number", "source"),
    [pytest.param(line, source, id=f"line-{line}") for line, source in PYTHON_EXAMPLES],
)
def test_python_example_runs_independently(line_number: int, source: str) -> None:
    """Keep every Python README example self-contained and executable."""

    padded_source = "\n" * (line_number - 1) + source
    exec(compile(padded_source, str(README_PATH), "exec"), {})
