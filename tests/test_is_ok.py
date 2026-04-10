from flow_res import Result, Ok, Err, is_ok

from tests.testutils.error import ErrType, TestErr


def test_is_ok_returns_true_for_ok() -> None:
    """Test that is_ok returns True for Ok result."""

    result = Ok(42)
    assert is_ok(result) is True


def test_is_ok_returns_false_for_err() -> None:
    """Test that is_ok returns False for Err result."""

    error = TestErr(type=ErrType.NOT_FOUND, message="Not found")
    result: Result[int, TestErr] = Err(error)
    assert is_ok(result) is False
