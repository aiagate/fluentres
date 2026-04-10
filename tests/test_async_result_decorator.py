"""Tests for the @async_result decorator."""

import asyncio

import pytest

from flow_res import Err, Ok, Result, async_result


@async_result
async def successful_operation(value: int) -> Result[int, ValueError]:
    """An async operation that succeeds."""
    await asyncio.sleep(0.001)
    return Ok(value * 2)


@async_result
async def failing_operation(value: int) -> Result[int, ValueError]:
    """An async operation that fails."""
    await asyncio.sleep(0.001)
    if value < 0:
        return Err(ValueError("Value cannot be negative"))
    return Ok(value)


@pytest.mark.asyncio
async def test_async_result_decorator_returns_awaitable_result():
    """Test that @async_result decorator returns AwaitableResult."""
    result = successful_operation(5)
    # The decorated function returns AwaitableResult, which has .map() method
    assert hasattr(result, "map")
    assert hasattr(result, "and_then")


@pytest.mark.asyncio
async def test_async_result_decorator_map_success():
    """Test that .map() works on successful async operation."""
    result = await successful_operation(5).map(lambda x: x + 1)
    assert result.unwrap() == 11


@pytest.mark.asyncio
async def test_async_result_decorator_map_error():
    """Test that .map() passes through errors."""
    result = await failing_operation(-1).map(lambda x: x + 1)
    assert isinstance(result, Err)
    assert "cannot be negative" in str(result.error)


@pytest.mark.asyncio
async def test_async_result_decorator_map_chain():
    """Test chaining multiple .map() calls."""
    result = await (
        successful_operation(3)
        .map(lambda x: x + 1)
        .map(lambda x: x * 2)
        .map(lambda x: str(x))
    )
    assert result.unwrap() == "14"


@pytest.mark.asyncio
async def test_async_result_decorator_and_then_success():
    """Test that .and_then() works with async operations."""

    @async_result
    async def chain_operation(x: int) -> Result[int, ValueError]:
        await asyncio.sleep(0.001)
        return Ok(x * 10)

    result = await successful_operation(5).and_then(lambda x: chain_operation(x))
    assert result.unwrap() == 100


@pytest.mark.asyncio
async def test_async_result_decorator_and_then_error_propagation():
    """Test that .and_then() propagates errors."""

    @async_result
    async def chain_operation(x: int) -> Result[int, ValueError]:
        await asyncio.sleep(0.001)
        return Ok(x * 10)

    result = await failing_operation(-1).and_then(lambda x: chain_operation(x))
    assert isinstance(result, Err)


@pytest.mark.asyncio
async def test_async_result_decorator_map_err():
    """Test that .map_err() works for error transformation."""
    result = await failing_operation(-1).map_err(
        lambda e: RuntimeError(f"Transformed: {e}")
    )
    assert isinstance(result, Err)
    assert "Transformed" in str(result.error)


@pytest.mark.asyncio
async def test_async_result_decorator_complex_chain():
    """Test complex chaining of multiple operations."""

    @async_result
    async def fetch_user(user_id: int) -> Result[dict, ValueError]:
        await asyncio.sleep(0.001)
        if user_id <= 0:
            return Err(ValueError("Invalid user ID"))
        return Ok({"id": user_id, "name": f"User{user_id}"})

    @async_result
    async def fetch_posts(user_id: int) -> Result[list[str], ValueError]:
        await asyncio.sleep(0.001)
        return Ok([f"Post {i}" for i in range(user_id)])

    result = await (
        fetch_user(3)
        .map(lambda u: u["id"])
        .and_then(lambda uid: fetch_posts(uid))
        .map(lambda posts: len(posts))
    )
    assert result.unwrap() == 3


@pytest.mark.asyncio
async def test_async_result_decorator_with_match_expression():
    """Test that decorated functions work with pattern matching."""
    from flow_res import Ok as OkType

    result = await successful_operation(5)
    match result:
        case OkType(value):
            assert value == 10
        case _:
            pytest.fail("Expected Ok result")
