"""Tests for alarm ability."""

import asyncio
from datetime import datetime, timedelta

import pytest

from bruno_abilities.abilities.alarm_ability import AlarmAbility, AlarmState
from bruno_abilities.base.ability_base import AbilityContext


@pytest.fixture
def alarm_ability():
    """Create an alarm ability instance."""
    ability = AlarmAbility()
    yield ability
    # Cleanup after test
    if ability._monitor_task:
        ability._monitor_task.cancel()


@pytest.fixture
def context():
    """Create an ability context."""
    return AbilityContext(
        user_id="test_user",
        session_id="test_session",
    )


@pytest.mark.asyncio
async def test_alarm_metadata(alarm_ability):
    """Test that alarm ability has proper metadata."""
    metadata = alarm_ability.metadata

    assert metadata.name == "alarm"
    assert metadata.display_name == "Alarm"
    assert "alarm" in metadata.description.lower()
    assert "alarm" in metadata.tags


@pytest.mark.asyncio
async def test_create_alarm_with_time_format(alarm_ability, context):
    """Test creating an alarm with HH:MM format."""
    # Start monitoring
    await alarm_ability.initialize()

    result = await alarm_ability.execute(
        {
            "action": "create",
            "time": "14:30",
            "name": "Afternoon Alarm",
            "recurrence": "none",
        },
        context,
    )

    assert result.success is True
    assert "alarm_id" in result.data
    assert result.data["name"] == "Afternoon Alarm"
    assert result.data["recurrence"] == "none"
    assert result.data["state"] == AlarmState.ACTIVE.value


@pytest.mark.asyncio
async def test_create_alarm_without_time(alarm_ability, context):
    """Test that creating an alarm without time fails."""
    result = await alarm_ability.execute(
        {
            "action": "create",
            "name": "No Time Alarm",
        },
        context,
    )

    assert result.success is False
    assert "time" in result.error.lower()


@pytest.mark.asyncio
async def test_create_alarm_with_invalid_time(alarm_ability, context):
    """Test that creating an alarm with invalid time fails."""
    result = await alarm_ability.execute(
        {
            "action": "create",
            "time": "25:70",  # Invalid time
        },
        context,
    )

    assert result.success is False
    assert "invalid" in result.error.lower()


@pytest.mark.asyncio
async def test_create_daily_alarm(alarm_ability, context):
    """Test creating a daily recurring alarm."""
    await alarm_ability.initialize()

    result = await alarm_ability.execute(
        {
            "action": "create",
            "time": "08:00",
            "name": "Daily Alarm",
            "recurrence": "daily",
        },
        context,
    )

    assert result.success is True
    assert result.data["recurrence"] == "daily"
    assert result.data["next_trigger"] is not None


@pytest.mark.asyncio
async def test_disable_and_enable_alarm(alarm_ability, context):
    """Test disabling and enabling an alarm."""
    await alarm_ability.initialize()

    # Create alarm
    create_result = await alarm_ability.execute(
        {
            "action": "create",
            "time": "10:00",
            "name": "Test Alarm",
        },
        context,
    )

    assert create_result.success is True
    alarm_id = create_result.data["alarm_id"]

    # Disable alarm
    disable_result = await alarm_ability.execute(
        {
            "action": "disable",
            "alarm_id": alarm_id,
        },
        context,
    )

    assert disable_result.success is True
    assert disable_result.data["state"] == AlarmState.DISABLED.value

    # Enable alarm
    enable_result = await alarm_ability.execute(
        {
            "action": "enable",
            "alarm_id": alarm_id,
        },
        context,
    )

    assert enable_result.success is True
    assert enable_result.data["state"] == AlarmState.ACTIVE.value


@pytest.mark.asyncio
async def test_delete_alarm(alarm_ability, context):
    """Test deleting an alarm."""
    await alarm_ability.initialize()

    # Create alarm
    create_result = await alarm_ability.execute(
        {
            "action": "create",
            "time": "11:00",
        },
        context,
    )

    assert create_result.success is True
    alarm_id = create_result.data["alarm_id"]

    # Delete alarm
    delete_result = await alarm_ability.execute(
        {
            "action": "delete",
            "alarm_id": alarm_id,
        },
        context,
    )

    assert delete_result.success is True

    # Verify alarm is deleted
    status_result = await alarm_ability.execute(
        {
            "action": "status",
            "alarm_id": alarm_id,
        },
        context,
    )

    assert status_result.success is False
    assert "not found" in status_result.error.lower()


@pytest.mark.asyncio
async def test_snooze_alarm(alarm_ability, context):
    """Test snoozing an alarm."""
    await alarm_ability.initialize()

    # Create alarm
    create_result = await alarm_ability.execute(
        {
            "action": "create",
            "time": "09:00",
            "name": "Snooze Test",
        },
        context,
    )

    assert create_result.success is True
    alarm_id = create_result.data["alarm_id"]

    # Snooze alarm
    snooze_result = await alarm_ability.execute(
        {
            "action": "snooze",
            "alarm_id": alarm_id,
            "snooze_minutes": 5,
        },
        context,
    )

    assert snooze_result.success is True
    assert snooze_result.data["snooze_minutes"] == 5
    assert "snooze_until" in snooze_result.data


@pytest.mark.asyncio
async def test_list_alarms(alarm_ability, context):
    """Test listing all alarms."""
    await alarm_ability.initialize()

    # Create multiple alarms
    alarm_ids = []
    for i in range(3):
        result = await alarm_ability.execute(
            {
                "action": "create",
                "time": f"{8 + i}:00",
                "name": f"Alarm {i}",
            },
            context,
        )
        assert result.success is True
        alarm_ids.append(result.data["alarm_id"])

    # List alarms
    list_result = await alarm_ability.execute(
        {"action": "list"},
        context,
    )

    assert list_result.success is True
    assert list_result.data["count"] == 3
    assert len(list_result.data["alarms"]) == 3


@pytest.mark.asyncio
async def test_alarm_status(alarm_ability, context):
    """Test getting alarm status."""
    await alarm_ability.initialize()

    # Create alarm
    create_result = await alarm_ability.execute(
        {
            "action": "create",
            "time": "12:00",
            "name": "Status Test",
            "recurrence": "daily",
        },
        context,
    )

    assert create_result.success is True
    alarm_id = create_result.data["alarm_id"]

    # Get status
    status_result = await alarm_ability.execute(
        {
            "action": "status",
            "alarm_id": alarm_id,
        },
        context,
    )

    assert status_result.success is True
    assert status_result.data["alarm_id"] == alarm_id
    assert status_result.data["name"] == "Status Test"
    assert status_result.data["recurrence"] == "daily"
    assert "created_at" in status_result.data


@pytest.mark.asyncio
async def test_multiple_users(alarm_ability):
    """Test that users can't access each other's alarms."""
    await alarm_ability.initialize()

    context1 = AbilityContext(user_id="user1", session_id="session1")
    context2 = AbilityContext(user_id="user2", session_id="session2")

    # User 1 creates an alarm
    result1 = await alarm_ability.execute(
        {
            "action": "create",
            "time": "13:00",
        },
        context1,
    )

    assert result1.success is True
    alarm_id = result1.data["alarm_id"]

    # User 2 tries to disable user 1's alarm
    result2 = await alarm_ability.execute(
        {
            "action": "disable",
            "alarm_id": alarm_id,
        },
        context2,
    )

    assert result2.success is False
    assert "permission" in result2.error.lower()


@pytest.mark.asyncio
async def test_invalid_action(alarm_ability, context):
    """Test that invalid actions are rejected."""
    result = await alarm_ability.execute(
        {
            "action": "invalid_action",
        },
        context,
    )

    assert result.success is False
    assert "unknown action" in result.error.lower()


@pytest.mark.asyncio
async def test_alarm_trigger(alarm_ability, context):
    """Test that alarms trigger at the right time."""
    import pytz

    await alarm_ability.initialize()

    # Create an alarm that triggers in 2 seconds by manually setting trigger time
    now_utc = datetime.now(pytz.UTC)

    triggered = []

    async def callback(alarm):
        triggered.append(alarm.alarm_id)

    # Create alarm with a time format (will be set for future)
    result = await alarm_ability.execute(
        {
            "action": "create",
            "time": "10:00",  # Set for a specific time
            "name": "Trigger Test",
        },
        context,
    )

    assert result.success is True
    alarm_id = result.data["alarm_id"]

    # Manually adjust the alarm to trigger soon for testing
    alarm = alarm_ability._alarms[alarm_id]
    alarm.callback = callback
    # Set next_trigger to trigger in 2 seconds (timezone-aware)
    alarm.next_trigger = now_utc + timedelta(seconds=2)

    # Wait for alarm to trigger
    await asyncio.sleep(3)

    # Check that alarm was triggered
    assert alarm_id in triggered

    # Check alarm state
    status_result = await alarm_ability.execute(
        {
            "action": "status",
            "alarm_id": alarm_id,
        },
        context,
    )

    assert status_result.success is True
    # For one-time alarms, state should be TRIGGERED
    assert status_result.data["state"] == AlarmState.TRIGGERED.value


@pytest.mark.asyncio
async def test_timezone_support(alarm_ability, context):
    """Test that alarms support different timezones."""
    await alarm_ability.initialize()

    result = await alarm_ability.execute(
        {
            "action": "create",
            "time": "15:00",
            "name": "NY Alarm",
            "timezone": "America/New_York",
        },
        context,
    )

    assert result.success is True
    assert result.data["timezone"] == "America/New_York"


@pytest.mark.asyncio
async def test_invalid_timezone(alarm_ability, context):
    """Test that invalid timezone is rejected."""
    result = await alarm_ability.execute(
        {
            "action": "create",
            "time": "15:00",
            "timezone": "Invalid/Timezone",
        },
        context,
    )

    assert result.success is False
    assert "timezone" in result.error.lower()


@pytest.mark.asyncio
async def test_alarm_cleanup(alarm_ability, context):
    """Test that alarms are cleaned up properly."""
    await alarm_ability.initialize()

    # Create multiple alarms
    for i in range(3):
        await alarm_ability.execute(
            {
                "action": "create",
                "time": f"{10 + i}:00",
            },
            context,
        )

    # Clean up
    await alarm_ability._cleanup()

    # Verify all alarms are cleared
    assert len(alarm_ability._alarms) == 0
    assert len(alarm_ability._user_alarms) == 0
    assert alarm_ability._monitor_task.done()
