from collections.abc import Callable
from typing import Any, assert_type

import pytest

from flow_res import Err, Ok, Result, combine, combine_async, combine_lazy

from tests.testutils.error import ErrType, TestErr


def _typed_ok[T](value: T) -> Result[T, ValueError]:
    return Ok(value)


def test_combine_all_ok() -> None:
    """Test that combine returns Ok with tuple of values when all are Ok."""
    from flow_res import combine

    results = (Ok(1), Ok(2), Ok(3))
    combined = combine(results)

    assert isinstance(combined, Ok)
    assert combined.value == (1, 2, 3)


def test_combine_with_err() -> None:
    """Test that combine returns first Err when any result is Err."""
    from flow_res import combine

    error1 = TestErr(type=ErrType.NOT_FOUND, message="First error")
    error2 = TestErr(type=ErrType.VALIDATION_ERROR, message="Second error")
    results = (
        Ok(1),
        Err(error1),
        Ok(3),
        Err(error2),
    )
    combined = combine(results)

    assert isinstance(combined, Err)
    assert combined.error is error1


def test_combine_empty_sequence() -> None:
    """Test that combine returns Ok with empty tuple for empty sequence."""
    from flow_res import combine

    results: tuple[Result[int, TestErr], ...] = ()
    combined = combine(results)

    assert isinstance(combined, Ok)
    assert combined.value == ()


def test_combine_single_ok() -> None:
    """Test that combine returns Ok with single-element tuple for one Ok."""
    from flow_res import combine

    results = (Ok(42),)
    combined = combine(results)

    assert isinstance(combined, Ok)
    assert combined.value == (42,)


def test_combine_single_err() -> None:
    """Test that combine returns the Err when given a single Err."""
    from flow_res import combine

    error = TestErr(type=ErrType.NOT_FOUND, message="Not found")
    results = (Err(error),)
    combined = combine(results)

    assert isinstance(combined, Err)
    assert combined.error is error


def test_combine_multiple_errors_returns_first() -> None:
    """Test that combine returns first Err when multiple errors exist."""
    from flow_res import combine

    error1 = TestErr(type=ErrType.NOT_FOUND, message="First")
    error2 = TestErr(type=ErrType.VALIDATION_ERROR, message="Second")
    error3 = TestErr(type=ErrType.UNEXPECTED, message="Third")
    results = (
        Err(error1),
        Err(error2),
        Err(error3),
    )
    combined = combine(results)

    assert isinstance(combined, Err)
    assert combined.error is error1
    assert combined.error.message == "First"


def test_combine_preserves_string_type() -> None:
    """Test that combine preserves type of Ok values (string example)."""
    from flow_res import combine

    results = (Ok("hello"), Ok("world"), Ok("test"))
    combined = combine(results)

    assert isinstance(combined, Ok)
    assert combined.value == ("hello", "world", "test")


def test_combine_error_after_ok_values() -> None:
    """Test that combine returns first Err even after Ok values."""
    from flow_res import combine

    error = TestErr(type=ErrType.VALIDATION_ERROR, message="Failed")
    results = (Ok(1), Ok(2), Err(error), Ok(4))
    combined = combine(results)

    assert isinstance(combined, Err)
    assert combined.error is error


def test_combine_heterogeneous_two_types() -> None:
    """Test that combine handles two different types correctly."""
    from flow_res import combine

    user_id = Ok(123)
    email = Ok("user@example.com")

    combined = combine((user_id, email))

    assert isinstance(combined, Ok)
    assert combined.value == (123, "user@example.com")
    user_id_val, email_val = combined.value
    assert isinstance(user_id_val, int)
    assert isinstance(email_val, str)


def test_combine_heterogeneous_three_types() -> None:
    """Test that combine handles three different types correctly."""
    from flow_res import combine

    name = Ok("Alice")
    age = Ok(30)
    active = Ok(True)

    combined = combine((name, age, active))

    assert isinstance(combined, Ok)
    assert combined.value == ("Alice", 30, True)
    name_val, age_val, active_val = combined.value
    assert name_val == "Alice"
    assert age_val == 30
    assert active_val is True


def test_combine_heterogeneous_with_error() -> None:
    """Test that combine returns first error with heterogeneous types."""
    from flow_res import combine

    error = TestErr(type=ErrType.VALIDATION_ERROR, message="Invalid age")
    name = Ok("Bob")
    age = Err(error)
    active = Ok(False)

    combined = combine((name, age, active))

    assert isinstance(combined, Err)
    assert combined.error is error


def test_combine_homogeneous_list_still_works() -> None:
    """Test that combine still works for homogeneous lists (backward compat)."""
    from flow_res import combine

    results = (Ok(1), Ok(2), Ok(3), Ok(4))
    combined = combine(results)

    assert isinstance(combined, Ok)
    assert combined.value == (1, 2, 3, 4)


def test_combine_complex_heterogeneous_types() -> None:
    """Test combine with complex heterogeneous types."""
    from flow_res import combine

    user_id = Ok(456)
    email = Ok("test@example.com")
    age = Ok(25)
    is_active = Ok(True)

    combined = combine((user_id, email, age, is_active))

    assert isinstance(combined, Ok)
    uid, mail, user_age, active = combined.value
    assert uid == 456
    assert mail == "test@example.com"
    assert user_age == 25
    assert active is True


def test_combine_eleven_element_heterogeneous_tuple_uses_fallback_type() -> None:
    """Long heterogeneous tuples are accepted with the documented fallback type."""
    results = (
        _typed_ok(1),
        _typed_ok("two"),
        _typed_ok(3.0),
        _typed_ok(True),
        _typed_ok(b"five"),
        _typed_ok(6),
        _typed_ok("seven"),
        _typed_ok(8.0),
        _typed_ok(False),
        _typed_ok(b"ten"),
        _typed_ok(11),
    )

    combined = combine(results)

    assert_type(combined, Result[tuple[Any, ...], ValueError])
    assert combined == Ok(
        (1, "two", 3.0, True, b"five", 6, "seven", 8.0, False, b"ten", 11)
    )


def test_combine_eleven_element_homogeneous_tuple_uses_fallback_type() -> None:
    """Long homogeneous tuples are accepted with the documented fallback type."""
    results = (
        _typed_ok(1),
        _typed_ok(2),
        _typed_ok(3),
        _typed_ok(4),
        _typed_ok(5),
        _typed_ok(6),
        _typed_ok(7),
        _typed_ok(8),
        _typed_ok(9),
        _typed_ok(10),
        _typed_ok(11),
    )

    combined = combine(results)

    assert_type(combined, Result[tuple[Any, ...], ValueError])
    assert combined == Ok(tuple(range(1, 12)))


def test_combine_lazy_runs_factories_in_order_and_stops_after_err() -> None:
    """Only factories through the first Err are evaluated."""
    calls: list[str] = []
    first_error = TestErr(type=ErrType.VALIDATION_ERROR, message="Failed")

    def factory(
        name: str, result: Result[Any, TestErr]
    ) -> Callable[[], Result[Any, TestErr]]:
        def run() -> Result[Any, TestErr]:
            calls.append(name)
            return result

        return run

    combined = combine_lazy(
        (
            factory("first", Ok(1)),
            factory("second", Err(first_error)),
            factory("third", Ok(3)),
        )
    )

    assert combined == Err(first_error)
    assert calls == ["first", "second"]


def test_combine_lazy_returns_success_values_in_evaluation_order() -> None:
    """Successful factory values are collected in factory order."""
    calls: list[str] = []

    def factory(name: str, value: Any) -> Callable[[], Result[Any, TestErr]]:
        def run() -> Result[Any, TestErr]:
            calls.append(name)
            return Ok(value)

        return run

    combined = combine_lazy(
        (factory("first", 1), factory("second", "two"), factory("third", True))
    )

    assert combined == Ok((1, "two", True))
    assert calls == ["first", "second", "third"]


@pytest.mark.anyio
async def test_combine_async_runs_sync_and_async_factories_in_order() -> None:
    """Sync and async factories are evaluated sequentially."""
    calls: list[str] = []

    def sync_factory() -> Result[int, TestErr]:
        calls.append("sync")
        return Ok(1)

    async def async_factory() -> Result[int, TestErr]:
        calls.append("async")
        return Ok(2)

    combined = await combine_async((sync_factory, async_factory))

    assert combined == Ok((1, 2))
    assert calls == ["sync", "async"]


@pytest.mark.anyio
async def test_combine_async_stops_after_first_err_without_calling_later_factories() -> (
    None
):
    """An async Err is awaited before later factories are skipped."""
    calls: list[str] = []
    first_error = TestErr(type=ErrType.UNEXPECTED, message="Failed")

    async def error_factory() -> Result[int, TestErr]:
        calls.append("error")
        return Err(first_error)

    def later_factory() -> Result[int, TestErr]:
        calls.append("later")
        return Ok(3)

    combined = await combine_async((error_factory, later_factory))

    assert combined == Err(first_error)
    assert calls == ["error"]
