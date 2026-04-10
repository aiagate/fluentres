from flow_res import Err, Ok, Result

from tests.testutils.error import ErrType, TestErr


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
