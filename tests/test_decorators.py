"""Tests for decorators."""

import asyncio
import pytest
from bruno_abilities.base.decorators import retry, timeout, rate_limit


@pytest.mark.asyncio
async def test_retry_success():
    """Test retry decorator with successful execution."""
    call_count = 0
    
    @retry(max_attempts=3, delay=0.01)
    async def flaky_function():
        nonlocal call_count
        call_count += 1
        return "success"
    
    result = await flaky_function()
    assert result == "success"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_eventual_success():
    """Test retry decorator with eventual success."""
    call_count = 0
    
    @retry(max_attempts=3, delay=0.01, backoff=1.0)
    async def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Not yet")
        return "success"
    
    result = await flaky_function()
    assert result == "success"
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_all_fail():
    """Test retry decorator when all attempts fail."""
    call_count = 0
    
    @retry(max_attempts=3, delay=0.01)
    async def always_fails():
        nonlocal call_count
        call_count += 1
        raise ValueError("Always fails")
    
    with pytest.raises(ValueError):
        await always_fails()
    
    assert call_count == 3


@pytest.mark.asyncio
async def test_timeout_success():
    """Test timeout decorator with successful execution."""
    
    @timeout(1.0)
    async def quick_function():
        await asyncio.sleep(0.01)
        return "done"
    
    result = await quick_function()
    assert result == "done"


@pytest.mark.asyncio
async def test_timeout_exceeded():
    """Test timeout decorator when timeout is exceeded."""
    
    @timeout(0.1)
    async def slow_function():
        await asyncio.sleep(1.0)
        return "done"
    
    with pytest.raises(asyncio.TimeoutError):
        await slow_function()


@pytest.mark.asyncio
async def test_rate_limit():
    """Test rate limit decorator."""
    call_times = []
    
    @rate_limit(max_calls=3, time_window=1.0)
    async def rate_limited_function(user_id: str):
        call_times.append(asyncio.get_event_loop().time())
        return "done"
    
    # Make 3 calls quickly (should succeed)
    for _ in range(3):
        await rate_limited_function("user123")
    
    assert len(call_times) == 3
    
    # 4th call should be delayed
    start_time = asyncio.get_event_loop().time()
    await rate_limited_function("user123")
    end_time = asyncio.get_event_loop().time()
    
    # Should have waited at least some time
    assert end_time - start_time > 0.5


@pytest.mark.asyncio
async def test_rate_limit_different_keys():
    """Test rate limit with different keys."""
    
    @rate_limit(max_calls=2, time_window=1.0)
    async def rate_limited_function(user_id: str):
        return f"done-{user_id}"
    
    # Different users should have independent limits
    result1 = await rate_limited_function("user1")
    result2 = await rate_limited_function("user2")
    result3 = await rate_limited_function("user1")
    result4 = await rate_limited_function("user2")
    
    assert result1 == "done-user1"
    assert result2 == "done-user2"
    assert result3 == "done-user1"
    assert result4 == "done-user2"
