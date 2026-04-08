from fluentres import Err, Ok, safe


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
