"""Tests for timer ability."""

import asyncio

import pytest

from bruno_abilities.abilities.timer_ability import TimerAbility, TimerState
from bruno_abilities.base.ability_base import AbilityContext


@pytest.fixture
def timer_ability():
    """Create a timer ability instance."""
    return TimerAbility()


@pytest.fixture
def context():
    """Create an ability context."""
    return AbilityContext(
        user_id="test_user",
        session_id="test_session",
    )


@pytest.mark.asyncio
async def test_timer_metadata(timer_ability):
    """Test that timer ability has proper metadata."""
    metadata = timer_ability.metadata

    assert metadata.name == "timer"
    assert metadata.display_name == "Timer"
    assert "countdown" in metadata.description.lower()
    assert "timer" in metadata.tags


@pytest.mark.asyncio
async def test_create_timer(timer_ability, context):
    """Test creating a basic timer."""
    result = await timer_ability.execute(
        {
            "action": "create",
            "duration": 2,
            "name": "Test Timer",
        },
        context,
    )

    assert result.success is True
    assert "timer_id" in result.data
    assert result.data["name"] == "Test Timer"
    assert result.data["duration_seconds"] == 2
    assert result.data["state"] == TimerState.RUNNING.value


@pytest.mark.asyncio
async def test_create_timer_without_duration(timer_ability, context):
    """Test that creating a timer without duration fails."""
    result = await timer_ability.execute(
        {
            "action": "create",
        },
        context,
    )

    assert result.success is False
    assert "duration" in result.error.lower()


@pytest.mark.asyncio
async def test_create_timer_with_negative_duration(timer_ability, context):
    """Test that creating a timer with negative duration fails."""
    result = await timer_ability.execute(
        {
            "action": "create",
            "duration": -10,
        },
        context,
    )

    assert result.success is False
    assert "greater than 0" in result.error.lower()


@pytest.mark.asyncio
async def test_pause_and_resume_timer(timer_ability, context):
    """Test pausing and resuming a timer."""
    # Create timer
    create_result = await timer_ability.execute(
        {
            "action": "create",
            "duration": 10,
            "name": "Pausable Timer",
        },
        context,
    )

    assert create_result.success is True
    timer_id = create_result.data["timer_id"]

    # Wait a bit
    await asyncio.sleep(0.2)

    # Pause timer
    pause_result = await timer_ability.execute(
        {
            "action": "pause",
            "timer_id": timer_id,
        },
        context,
    )

    assert pause_result.success is True
    assert pause_result.data["state"] == TimerState.PAUSED.value

    paused_remaining = pause_result.data["remaining_seconds"]

    # Wait while paused
    await asyncio.sleep(0.5)

    # Check that remaining time didn't decrease while paused
    status_result = await timer_ability.execute(
        {
            "action": "status",
            "timer_id": timer_id,
        },
        context,
    )

    assert status_result.success is True
    # Allow for small timing differences
    assert abs(status_result.data["remaining_seconds"] - paused_remaining) <= 1

    # Resume timer
    resume_result = await timer_ability.execute(
        {
            "action": "resume",
            "timer_id": timer_id,
        },
        context,
    )

    assert resume_result.success is True
    assert resume_result.data["state"] == TimerState.RUNNING.value

    # Cleanup
    await timer_ability.execute(
        {"action": "cancel", "timer_id": timer_id},
        context,
    )


@pytest.mark.asyncio
async def test_cancel_timer(timer_ability, context):
    """Test cancelling a timer."""
    # Create timer
    create_result = await timer_ability.execute(
        {
            "action": "create",
            "duration": 10,
        },
        context,
    )

    assert create_result.success is True
    timer_id = create_result.data["timer_id"]

    # Cancel timer
    cancel_result = await timer_ability.execute(
        {
            "action": "cancel",
            "timer_id": timer_id,
        },
        context,
    )

    assert cancel_result.success is True
    assert cancel_result.data["state"] == TimerState.CANCELLED.value


@pytest.mark.asyncio
async def test_extend_timer(timer_ability, context):
    """Test extending a running timer."""
    # Create timer
    create_result = await timer_ability.execute(
        {
            "action": "create",
            "duration": 5,
        },
        context,
    )

    assert create_result.success is True
    timer_id = create_result.data["timer_id"]

    # Wait a bit
    await asyncio.sleep(0.2)

    # Extend timer
    extend_result = await timer_ability.execute(
        {
            "action": "extend",
            "timer_id": timer_id,
            "extend_seconds": 10,
        },
        context,
    )

    assert extend_result.success is True
    assert extend_result.data["remaining_seconds"] > 5

    # Cleanup
    await timer_ability.execute(
        {"action": "cancel", "timer_id": timer_id},
        context,
    )


@pytest.mark.asyncio
async def test_list_timers(timer_ability, context):
    """Test listing all timers."""
    # Create multiple timers
    timer_ids = []
    for i in range(3):
        result = await timer_ability.execute(
            {
                "action": "create",
                "duration": 10,
                "name": f"Timer {i}",
            },
            context,
        )
        assert result.success is True
        timer_ids.append(result.data["timer_id"])

    # List timers
    list_result = await timer_ability.execute(
        {"action": "list"},
        context,
    )

    assert list_result.success is True
    assert list_result.data["count"] == 3
    assert len(list_result.data["timers"]) == 3

    # Cleanup
    for timer_id in timer_ids:
        await timer_ability.execute(
            {"action": "cancel", "timer_id": timer_id},
            context,
        )


@pytest.mark.asyncio
async def test_timer_status(timer_ability, context):
    """Test getting timer status."""
    # Create timer
    create_result = await timer_ability.execute(
        {
            "action": "create",
            "duration": 10,
            "name": "Status Timer",
        },
        context,
    )

    assert create_result.success is True
    timer_id = create_result.data["timer_id"]

    # Get status
    status_result = await timer_ability.execute(
        {
            "action": "status",
            "timer_id": timer_id,
        },
        context,
    )

    assert status_result.success is True
    assert status_result.data["timer_id"] == timer_id
    assert status_result.data["name"] == "Status Timer"
    assert status_result.data["state"] == TimerState.RUNNING.value
    assert "started_at" in status_result.data

    # Cleanup
    await timer_ability.execute(
        {"action": "cancel", "timer_id": timer_id},
        context,
    )


@pytest.mark.asyncio
async def test_timer_completion(timer_ability, context):
    """Test that a timer completes successfully."""
    # Create a short timer
    create_result = await timer_ability.execute(
        {
            "action": "create",
            "duration": 1,  # 1 second
            "name": "Quick Timer",
        },
        context,
    )

    assert create_result.success is True
    timer_id = create_result.data["timer_id"]

    # Wait for timer to complete
    await asyncio.sleep(1.5)

    # Check status
    status_result = await timer_ability.execute(
        {
            "action": "status",
            "timer_id": timer_id,
        },
        context,
    )

    assert status_result.success is True
    assert status_result.data["state"] == TimerState.COMPLETED.value
    assert status_result.data["remaining_seconds"] == 0
    assert "completed_at" in status_result.data


@pytest.mark.asyncio
async def test_multiple_users(timer_ability):
    """Test that users can't access each other's timers."""
    context1 = AbilityContext(user_id="user1", session_id="session1")
    context2 = AbilityContext(user_id="user2", session_id="session2")

    # User 1 creates a timer
    result1 = await timer_ability.execute(
        {
            "action": "create",
            "duration": 10,
        },
        context1,
    )

    assert result1.success is True
    timer_id = result1.data["timer_id"]

    # User 2 tries to pause user 1's timer
    result2 = await timer_ability.execute(
        {
            "action": "pause",
            "timer_id": timer_id,
        },
        context2,
    )

    assert result2.success is False
    assert "permission" in result2.error.lower()

    # Cleanup
    await timer_ability.execute(
        {"action": "cancel", "timer_id": timer_id},
        context1,
    )


@pytest.mark.asyncio
async def test_invalid_action(timer_ability, context):
    """Test that invalid actions are rejected."""
    result = await timer_ability.execute(
        {
            "action": "invalid_action",
        },
        context,
    )

    assert result.success is False
    assert "unknown action" in result.error.lower()


@pytest.mark.asyncio
async def test_pause_non_running_timer(timer_ability, context):
    """Test that pausing a non-running timer fails."""
    # Create and cancel a timer
    create_result = await timer_ability.execute(
        {
            "action": "create",
            "duration": 10,
        },
        context,
    )

    timer_id = create_result.data["timer_id"]

    await timer_ability.execute(
        {"action": "cancel", "timer_id": timer_id},
        context,
    )

    # Try to pause cancelled timer
    pause_result = await timer_ability.execute(
        {
            "action": "pause",
            "timer_id": timer_id,
        },
        context,
    )

    assert pause_result.success is False
    assert "not running" in pause_result.error.lower()


@pytest.mark.asyncio
async def test_resume_non_paused_timer(timer_ability, context):
    """Test that resuming a non-paused timer fails."""
    # Create a running timer
    create_result = await timer_ability.execute(
        {
            "action": "create",
            "duration": 10,
        },
        context,
    )

    timer_id = create_result.data["timer_id"]

    # Try to resume running timer
    resume_result = await timer_ability.execute(
        {
            "action": "resume",
            "timer_id": timer_id,
        },
        context,
    )

    assert resume_result.success is False
    assert "not paused" in resume_result.error.lower()

    # Cleanup
    await timer_ability.execute(
        {"action": "cancel", "timer_id": timer_id},
        context,
    )


@pytest.mark.asyncio
async def test_timer_cleanup(timer_ability, context):
    """Test that timers are cleaned up properly."""
    # Create multiple timers
    for _i in range(3):
        await timer_ability.execute(
            {
                "action": "create",
                "duration": 10,
            },
            context,
        )

    # Clean up
    await timer_ability._cleanup()

    # Verify all timers are cleared
    assert len(timer_ability._timers) == 0
    assert len(timer_ability._user_timers) == 0
