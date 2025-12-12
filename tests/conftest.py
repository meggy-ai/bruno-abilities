"""Common test fixtures and configuration."""

import pytest
import asyncio


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing."""
    return "test_user_123"


@pytest.fixture
def sample_session_id():
    """Sample session ID for testing."""
    return "test_session_456"
