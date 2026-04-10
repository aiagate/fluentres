from flow_res import Err, Ok, safe
import pytest


def test_safe_decorator_wraps_exception() -> None:
    """Test that @safe decorator converts exceptions to Err."""

    @safe
    def risky_function(x: int) -> int:
        if x < 0:
            raise ValueError("Negative number")
        return x * 2

    result = risky_function(-5)
    assert isinstance(result, Err)
    assert isinstance(result.error, ValueError)
    assert "Negative number" in str(result.error)


def test_safe_decorator_returns_ok() -> None:
    """Test that @safe decorator returns Ok for successful execution."""

    @safe
    def safe_function(x: int) -> int:
        return x * 2

    result = safe_function(5)
    assert isinstance(result, Ok)
    assert result.value == 10


def test_safe_decorator_with_specific_exception() -> None:
    """Test that @safe decorator with specific exception only catches that exception."""

    @safe(ValueError)
    def risky_function(x: int) -> int:
        if x < 0:
            raise ValueError("Negative number")
        if x == 0:
            raise TypeError("Zero is not allowed here")
        return x * 2

    # Should catch ValueError
    result = risky_function(-5)
    assert isinstance(result, Err)
    assert isinstance(result.error, ValueError)

    # Should NOT catch TypeError
    with pytest.raises(TypeError):
        risky_function(0)


def test_safe_decorator_with_multiple_exceptions() -> None:
    """Test that @safe decorator with multiple exceptions catches any of them."""

    @safe(ValueError, TypeError)
    def risky_function(x: int) -> int:
        if x < 0:
            raise ValueError("Negative number")
        if x == 0:
            raise TypeError("Zero is not allowed here")
        if x == 1:
            raise RuntimeError("One is a runtime error")
        return x * 2

    # Should catch ValueError
    assert isinstance(risky_function(-5), Err)
    # Should catch TypeError
    assert isinstance(risky_function(0), Err)
    # Should NOT catch RuntimeError
    with pytest.raises(RuntimeError):
        risky_function(1)
