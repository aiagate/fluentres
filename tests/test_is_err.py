from flow_res import Result, Ok, Err, is_err

from tests.testutils.error import ErrType, TestErr


def test_is_err_returns_true_for_err() -> None:
    """Test that is_err returns True  for Err result."""

    error = TestErr(type=ErrType.NOT_FOUND, message="Not found")
    result: Result[int, TestErr] = Err(error)
    assert is_err(result) is True


def test_is_err_returns_false_for_ok() -> None:
    """Test that is_err returns False for Ok result."""

    result = Ok(42)
    assert is_err(result) is False
