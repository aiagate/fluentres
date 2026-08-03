import asyncio
from collections.abc import Coroutine
from typing import Any, assert_type

import pytest

from flow_res import Err, Ok, Result, safe


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


def test_bare_safe_catches_any_exception_subclass() -> None:
    """Bare @safe intentionally preserves its Exception catch-all behavior."""

    @safe
    def unexpected_failure() -> None:
        raise RuntimeError("unexpected programming failure")

    result = unexpected_failure()

    assert isinstance(result, Err)
    assert isinstance(result.error, RuntimeError)
    assert str(result.error) == "unexpected programming failure"


def test_safe_decorator_returns_ok() -> None:
    """Test that @safe decorator returns Ok for successful execution."""

    @safe
    def safe_function(x: int) -> int:
        return x * 2

    result = assert_type(safe_function(5), Result[int, Exception])
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

    success = assert_type(risky_function(2), Result[int, ValueError])
    assert success == Ok(4)

    # Should NOT catch TypeError
    with pytest.raises(TypeError):
        risky_function(0)


def test_explicit_safe_filter_propagates_unlisted_exception() -> None:
    """An explicit filter must not convert exceptions outside its allowlist."""

    @safe(ValueError)
    def risky_function() -> None:
        raise RuntimeError("not in the filter")

    with pytest.raises(RuntimeError, match="not in the filter"):
        risky_function()


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

    assert_type(risky_function(2), Result[int, ValueError | TypeError])

    # Should catch ValueError
    assert isinstance(risky_function(-5), Err)
    # Should catch TypeError
    assert isinstance(risky_function(0), Err)
    # Should NOT catch RuntimeError
    with pytest.raises(RuntimeError):
        risky_function(1)


@pytest.mark.asyncio
async def test_safe_decorator_awaits_async_function_and_wraps_exception() -> None:
    @safe(ValueError)
    async def risky_function(value: int, *, fail: bool = False) -> int:
        if fail:
            raise ValueError("failed asynchronously")
        return value * 2

    pending = risky_function(value=5)
    pending = assert_type(
        pending,
        Coroutine[Any, Any, Result[int, ValueError]],
    )
    assert await pending == Ok(10)

    result = await risky_function(5, fail=True)
    assert isinstance(result, Err)
    assert isinstance(result.error, ValueError)


@pytest.mark.asyncio
async def test_safe_wraps_exception_raised_after_async_function_suspends() -> None:
    @safe(ValueError)
    async def risky_function() -> int:
        await asyncio.sleep(0)
        raise ValueError("failed after suspension")

    result = await risky_function()

    assert isinstance(result, Err)
    assert isinstance(result.error, ValueError)
    assert str(result.error) == "failed after suspension"


@pytest.mark.asyncio
async def test_safe_without_arguments_supports_async_function() -> None:
    @safe
    async def risky_function(value: int) -> int:
        if value < 0:
            raise RuntimeError("failed asynchronously")
        return value

    assert await risky_function(1) == Ok(1)
    assert isinstance(await risky_function(-1), Err)


@pytest.mark.asyncio
async def test_bare_safe_does_not_catch_cancelled_error() -> None:
    """Control-flow exceptions such as CancelledError must propagate."""

    @safe
    async def cancellable_operation() -> None:
        raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        await cancellable_operation()


@pytest.mark.asyncio
async def test_safe_empty_parentheses_supports_async_function() -> None:
    @safe()
    async def risky_function(value: int) -> int:
        if value < 0:
            raise ValueError("failed asynchronously")
        return value

    assert await risky_function(1) == Ok(1)
    assert isinstance(await risky_function(-1), Err)


@pytest.mark.asyncio
async def test_safe_async_function_does_not_catch_unlisted_exception() -> None:
    @safe(ValueError)
    async def risky_function() -> int:
        raise TypeError("not handled")

    with pytest.raises(TypeError, match="not handled"):
        await risky_function()


@pytest.mark.asyncio
async def test_safe_wraps_async_callable_object() -> None:
    class AsyncCallable:
        async def __call__(self, value: int, *, fail: bool = False) -> int:
            await asyncio.sleep(0)
            if fail:
                raise ValueError("failed from callable object")
            return value * 2

    safe_callable = safe(ValueError)(AsyncCallable())

    assert await safe_callable(5) == Ok(10)

    result = await safe_callable(5, fail=True)
    assert isinstance(result, Err)
    assert isinstance(result.error, ValueError)
    assert str(result.error) == "failed from callable object"
