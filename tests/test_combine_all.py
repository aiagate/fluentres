from flow_res import Err, Ok, Result, combine_all
from tests.testutils.error import ErrType, TestErr


def test_combine_all_all_ok() -> None:
    """Test that combine_all returns Ok with tuple of values when all are Ok."""

    results = (Ok(1), Ok(2), Ok(3))
    combined = combine_all(results)

    assert isinstance(combined, Ok)
    assert combined.value == (1, 2, 3)


def test_combine_all_collects_all_errors() -> None:
    """Test that combine_all collects ALL errors."""

    error1 = TestErr(type=ErrType.NOT_FOUND, message="First")
    error2 = TestErr(type=ErrType.VALIDATION_ERROR, message="Second")
    error3 = TestErr(type=ErrType.UNEXPECTED, message="Third")
    results = (
        Err(error1),
        Ok(2),
        Err(error2),
        Ok(4),
        Err(error3),
    )
    combined = combine_all(results)

    assert isinstance(combined, Err)
    assert isinstance(combined.error, ExceptionGroup)
    assert len(combined.error.exceptions) == 3
    assert combined.error.exceptions[0] is error1
    assert combined.error.exceptions[1] is error2
    assert combined.error.exceptions[2] is error3


def test_combine_all_heterogeneous_types() -> None:
    """Test that combine_all handles heterogeneous types correctly."""

    user_id: Result[int, TestErr] = Ok(123)
    email: Result[str, TestErr] = Ok("test@example.com")
    age: Result[int, TestErr] = Ok(25)

    combined = combine_all((user_id, email, age))

    assert isinstance(combined, Ok)
    assert combined.value == (123, "test@example.com", 25)


def test_combine_all_heterogeneous_with_errors() -> None:
    """Test that combine_all collects all errors with heterogeneous types."""

    error1 = TestErr(type=ErrType.NOT_FOUND, message="Error 1")
    error2 = TestErr(type=ErrType.VALIDATION_ERROR, message="Error 2")

    user_id: Result[int, TestErr] = Ok(123)
    email: Result[str, TestErr] = Err(error1)
    age: Result[int, TestErr] = Err(error2)

    combined = combine_all((user_id, email, age))

    assert isinstance(combined, Err)
    assert isinstance(combined.error, ExceptionGroup)
    assert len(combined.error.exceptions) == 2
