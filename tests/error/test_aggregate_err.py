from fluentres import AggregateErr
from tests.testutils.error import ErrType, TestErr


def test_aggregate_err_str() -> None:
    """Test AggregateErr string representation."""

    error1 = TestErr(type=ErrType.NOT_FOUND, message="First error")
    error2 = TestErr(type=ErrType.VALIDATION_ERROR, message="Second error")
    aggregate = AggregateErr([error1, error2])

    assert "Multiple errors occurred (2)" in str(aggregate)
