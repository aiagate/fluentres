"""Tests for Result type functional methods."""

import pytest
from flow_res import Err, Ok, Result

from tests.testutils.error import ErrType, TestErr


def test_ok_map_transforms_value() -> None:
    """Test that Ok.map transforms the value."""
    result = Ok(5)
    mapped = result.map(lambda x: x * 2)

    assert isinstance(mapped, Ok)
    assert mapped.value == 10


def test_ok_map_changes_type() -> None:
    """Test that Ok.map can change the type of the value."""
    result = Ok(42)
    mapped = result.map(lambda x: f"Number: {x}")

    assert isinstance(mapped, Ok)
    assert mapped.value == "Number: 42"


def test_err_map_passes_through() -> None:
    """Test that Err.map passes through unchanged."""
    error = TestErr(type=ErrType.NOT_FOUND, message="User not found")
    result: Err[TestErr] = Err(error)
    mapped = result.map(lambda x: x * 2)

    assert isinstance(mapped, Err)
    assert mapped.error is error
    assert mapped.error.message == "User not found"


def test_ok_unwrap_returns_value() -> None:
    """Test that Ok.unwrap returns the value."""
    result = Ok(42)
    value = result.unwrap()

    assert value == 42


def test_err_unwrap_raises_exception() -> None:
    """Test that Err.unwrap raises an exception."""
    error = TestErr(type=ErrType.NOT_FOUND, message="User not found")
    result: Err[TestErr] = Err(error)

    with pytest.raises(TestErr) as exc_info:
        result.unwrap()

    assert "User not found" in str(exc_info.value)
    assert exc_info.value.type is ErrType.NOT_FOUND


def test_err_unwrap_or_returns_default() -> None:
    """Test that Err.unwrap_or returns the default value."""
    error = TestErr(type=ErrType.VALIDATION_ERROR, message="Invalid input")
    result: Err[TestErr] = Err(error)
    default = "Default value"
    value = result.unwrap_or(default)

    assert value == default


def test_err_expect_raises_exception() -> None:
    """Test that Err.expect raises with the provided message."""
    error = TestErr(type=ErrType.NOT_FOUND, message="User not found")
    result: Err[TestErr] = Err(error)

    with pytest.raises(RuntimeError) as exc_info:
        result.expect("Expected user to exist")

    assert "Expected user to exist" in str(exc_info.value)
    assert exc_info.value.__cause__ is error


def test_map_chain() -> None:
    """Test that multiple map calls can be chained."""
    result = Ok(5)
    final = (
        result.map(lambda x: x * 2).map(lambda x: x + 3).map(lambda x: f"Result: {x}")
    )

    assert isinstance(final, Ok)
    assert final.value == "Result: 13"


def test_map_chain_with_err() -> None:
    """Test that map chain with Err passes through unchanged."""
    error = TestErr(type=ErrType.VALIDATION_ERROR, message="Invalid input")
    result: Err[TestErr] = Err(error)
    final = (
        result.map(lambda x: x * 2).map(lambda x: x + 3).map(lambda x: f"Result: {x}")
    )

    assert isinstance(final, Err)
    assert final.error is error


def test_map_unwrap_chain() -> None:
    """Test that map and unwrap can be chained together."""
    result = Ok(10)
    value = result.map(lambda x: x * 5).map(lambda x: x + 10).unwrap()

    assert value == 60


def test_map_expect_chain_with_err() -> None:
    """Test that map and expect chain raises on Err."""
    error = TestErr(type=ErrType.UNEXPECTED, message="Something went wrong")
    result: Err[TestErr] = Err(error)

    with pytest.raises(RuntimeError) as exc_info:
        result.map(lambda x: x * 2).expect("Should not be an error")

    assert "Should not be an error" in str(exc_info.value)


def test_err_expect_with_exception() -> None:
    """Test that Err.expect raises RuntimeError for Exception errors."""
    result: Err[Exception] = Err(Exception("Not an exception"))

    with pytest.raises(RuntimeError) as exc_info:
        result.expect("Expected success")

    assert "Expected success: Not an exception" in str(exc_info.value)


def test_usecase_error_str() -> None:
    """Test that UseCaseError.__str__ returns the message."""
    error = TestErr(type=ErrType.NOT_FOUND, message="Resource not found")

    assert str(error) == "Resource not found"


def test_ok_and_then_returns_new_result() -> None:
    """Test that Ok.and_then applies the function and returns the new Result."""
    result = Ok(5)
    new_result = result.and_then(lambda x: Ok(x * 2))

    assert isinstance(new_result, Ok)
    assert new_result.value == 10


def test_ok_and_then_propagates_error() -> None:
    """Test that Ok.and_then propagates error if function returns Err."""
    result: Ok[int] = Ok(5)
    error = TestErr(type=ErrType.VALIDATION_ERROR, message="Failed")
    new_result = result.and_then(lambda x: Err(error))

    assert isinstance(new_result, Err)
    assert new_result.error is error


def test_err_and_then_passes_through() -> None:
    """Test that Err.and_then passes through unchanged."""
    error = TestErr(type=ErrType.NOT_FOUND, message="Not found")
    result: Err[TestErr] = Err(error)
    new_result = result.and_then(lambda x: Ok(x * 2))

    assert isinstance(new_result, Err)
    assert new_result.error is error


def test_and_then_chain() -> None:
    """Test that multiple and_then calls can be chained."""
    result = Ok(2)
    final = (
        result.and_then(lambda x: Ok(x * 3))
        .and_then(lambda x: Ok(x + 10))
        .and_then(lambda x: Ok(f"Result: {x}"))
    )

    assert isinstance(final, Ok)
    assert final.value == "Result: 16"


def test_and_then_chain_with_error() -> None:
    """Test that error in and_then chain stops further processing."""
    result = Ok(2)
    error = TestErr(type=ErrType.UNEXPECTED, message="Error occurred")
    final = (
        result.and_then(lambda x: Ok(x * 3))
        .and_then(lambda x: Err(error))
        .and_then(lambda x: Ok(x + 10))  # type: ignore[arg-type]
    )

    assert isinstance(final, Err)
    assert final.error is error


def test_and_then_with_map() -> None:
    """Test that and_then and map can be combined."""
    result: Ok[int] = Ok(5)
    final = (
        result.and_then(lambda x: Ok(x * 2))
        .map(lambda x: x + 5)
        .and_then(lambda x: Ok(f"Final: {x}"))
    )

    assert isinstance(final, Ok)
    assert final.value == "Final: 15"


def test_ok_expect_returns_value() -> None:
    """Test that Ok.expect returns the value."""
    result: Ok[int] = Ok(42)
    value = result.expect("Should have value")

    assert value == 42


def test_ok_map_err_passes_through() -> None:
    """Test that Ok.map_err passes through unchanged without calling function."""
    result: Ok[int] = Ok(42)
    call_count = 0

    def transform_error(e: Exception) -> TestErr:
        nonlocal call_count
        call_count += 1
        return TestErr(type=ErrType.UNEXPECTED, message=f"Wrapped: {e}")

    mapped = result.map_err(transform_error)

    assert isinstance(mapped, Ok)
    assert mapped.value == 42
    assert call_count == 0  # Function should not be called for Ok


def test_err_map_err_transforms_error() -> None:
    """Test that Err.map_err transforms the error value."""
    result: Err[Exception] = Err(Exception("original error"))
    mapped = result.map_err(
        lambda e: TestErr(type=ErrType.VALIDATION_ERROR, message=f"Wrapped: {e}")
    )

    assert isinstance(mapped, Err)
    assert isinstance(mapped.error, TestErr)
    assert mapped.error.type == ErrType.VALIDATION_ERROR
    assert mapped.error.message == "Wrapped: original error"


def test_map_err_changes_error_type() -> None:
    """Test that map_err can change error type from str to UseCaseError."""
    result: Err[Exception] = Err(Exception("Not found"))
    mapped = result.map_err(lambda e: TestErr(type=ErrType.NOT_FOUND, message=str(e)))

    assert isinstance(mapped, Err)
    assert isinstance(mapped.error, TestErr)
    assert mapped.error.type == ErrType.NOT_FOUND
    assert mapped.error.message == "Not found"


def test_map_err_chain() -> None:
    """Test that multiple map_err calls can be chained."""
    result: Err[Exception] = Err(Exception("base error"))
    final = (
        result.map_err(lambda e: Exception(f"Level 1: {e}"))
        .map_err(lambda e: Exception(f"Level 2: {e}"))
        .map_err(lambda e: Exception(f"Level 3: {e}"))
    )

    assert isinstance(final, Err)
    assert str(final.error) == "Level 3: Level 2: Level 1: base error"


def test_map_err_with_map_chain() -> None:
    """Test that map and map_err can be mixed in a chain."""

    # Test with Ok - map applies, map_err passes through
    ok_result: Result[int, Exception] = Ok(5)
    ok_final = ok_result.map(lambda x: x * 2).map_err(
        lambda e: Exception(f"Error: {e}")
    )

    assert isinstance(ok_final, Ok)
    assert ok_final.value == 10

    # Test with Err - map passes through, map_err applies
    err_result: Result[int, Exception] = Err(Exception("failure"))
    err_final = err_result.map(lambda x: x * 2).map_err(
        lambda e: Exception(f"Error: {e}")
    )

    assert isinstance(err_final, Err)
    assert str(err_final.error) == "Error: failure"


def test_map_err_error_wrapping() -> None:
    """Test map_err for wrapping exceptions (use case from spec)."""

    def find_record(record_id: int) -> Result[str, KeyError]:
        """Simulate a function that returns KeyError."""
        return Err(KeyError(f"ID {record_id}"))

    result = find_record(999).map_err(
        lambda e: TestErr(type=ErrType.NOT_FOUND, message=f"Record missing: {e}")
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, TestErr)
    assert result.error.type == ErrType.NOT_FOUND
    assert "Record missing" in result.error.message
    assert "ID 999" in result.error.message
