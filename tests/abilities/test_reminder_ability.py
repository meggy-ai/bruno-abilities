"""Tests for reminder ability."""

import asyncio
from datetime import datetime, timedelta

import pytest
import pytz

from bruno_abilities.abilities.reminder_ability import ReminderAbility, ReminderState
from bruno_abilities.base.ability_base import AbilityContext


@pytest.fixture
def reminder_ability():
    """Create a reminder ability instance."""
    ability = ReminderAbility()
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
async def test_reminder_metadata(reminder_ability):
    """Test that reminder ability has proper metadata."""
    metadata = reminder_ability.metadata

    assert metadata.name == "reminder"
    assert metadata.display_name == "Reminder"
    assert "reminder" in metadata.description.lower()
    assert "reminder" in metadata.tags


@pytest.mark.asyncio
async def test_create_reminder(reminder_ability, context):
    """Test creating a basic reminder."""
    await reminder_ability.initialize()

    result = await reminder_ability.execute(
        {
            "action": "create",
            "title": "Test Reminder",
            "when": "in 2 hours",
            "priority": "high",
        },
        context,
    )

    assert result.success is True
    assert "reminder_id" in result.data
    assert result.data["title"] == "Test Reminder"
    assert result.data["priority"] == "high"


@pytest.mark.asyncio
async def test_create_reminder_without_title(reminder_ability, context):
    """Test that creating a reminder without title fails."""
    result = await reminder_ability.execute(
        {
            "action": "create",
            "when": "tomorrow",
        },
        context,
    )

    assert result.success is False
    assert "title" in result.error.lower()


@pytest.mark.asyncio
async def test_create_reminder_without_when(reminder_ability, context):
    """Test that creating a reminder without when fails."""
    result = await reminder_ability.execute(
        {
            "action": "create",
            "title": "Test",
        },
        context,
    )

    assert result.success is False
    assert "when" in result.error.lower()


@pytest.mark.asyncio
async def test_create_reminder_with_past_time(reminder_ability, context):
    """Test that creating a reminder with past time fails."""
    result = await reminder_ability.execute(
        {
            "action": "create",
            "title": "Past Reminder",
            "when": "yesterday",
        },
        context,
    )

    assert result.success is False
    assert "future" in result.error.lower()


@pytest.mark.asyncio
async def test_create_reminder_with_details(reminder_ability, context):
    """Test creating a reminder with full details."""
    await reminder_ability.initialize()

    result = await reminder_ability.execute(
        {
            "action": "create",
            "title": "Important Meeting",
            "when": "in 3 hours",
            "description": "Discuss project roadmap",
            "category": "work",
            "priority": "urgent",
            "tags": "meeting,important",
        },
        context,
    )

    assert result.success is True
    assert result.data["title"] == "Important Meeting"
    assert result.data["priority"] == "urgent"
    assert result.data["category"] == "work"
    assert "meeting" in result.data["tags"]
    assert "important" in result.data["tags"]


@pytest.mark.asyncio
async def test_complete_reminder(reminder_ability, context):
    """Test completing a reminder."""
    await reminder_ability.initialize()

    # Create reminder
    create_result = await reminder_ability.execute(
        {
            "action": "create",
            "title": "Test Task",
            "when": "in 5 hours",
        },
        context,
    )

    assert create_result.success is True
    reminder_id = create_result.data["reminder_id"]

    # Complete reminder
    complete_result = await reminder_ability.execute(
        {
            "action": "complete",
            "reminder_id": reminder_id,
        },
        context,
    )

    assert complete_result.success is True
    assert complete_result.data["state"] == ReminderState.COMPLETED.value


@pytest.mark.asyncio
async def test_cancel_reminder(reminder_ability, context):
    """Test cancelling a reminder."""
    await reminder_ability.initialize()

    # Create reminder
    create_result = await reminder_ability.execute(
        {
            "action": "create",
            "title": "Test Cancel",
            "when": "tomorrow",
        },
        context,
    )

    assert create_result.success is True
    reminder_id = create_result.data["reminder_id"]

    # Cancel reminder
    cancel_result = await reminder_ability.execute(
        {
            "action": "cancel",
            "reminder_id": reminder_id,
        },
        context,
    )

    assert cancel_result.success is True
    assert cancel_result.data["state"] == ReminderState.CANCELLED.value


@pytest.mark.asyncio
async def test_snooze_reminder(reminder_ability, context):
    """Test snoozing a reminder."""
    await reminder_ability.initialize()

    # Create reminder
    create_result = await reminder_ability.execute(
        {
            "action": "create",
            "title": "Snooze Test",
            "when": "in 1 hour",
        },
        context,
    )

    assert create_result.success is True
    reminder_id = create_result.data["reminder_id"]

    # Snooze reminder
    snooze_result = await reminder_ability.execute(
        {
            "action": "snooze",
            "reminder_id": reminder_id,
            "snooze_minutes": 15,
        },
        context,
    )

    assert snooze_result.success is True
    assert snooze_result.data["snooze_minutes"] == 15
    assert "snoozed_until" in snooze_result.data


@pytest.mark.asyncio
async def test_list_reminders(reminder_ability, context):
    """Test listing all reminders."""
    await reminder_ability.initialize()

    # Create multiple reminders
    reminder_ids = []
    for i in range(3):
        result = await reminder_ability.execute(
            {
                "action": "create",
                "title": f"Reminder {i}",
                "when": f"in {i + 1} hours",
            },
            context,
        )
        assert result.success is True
        reminder_ids.append(result.data["reminder_id"])

    # List reminders
    list_result = await reminder_ability.execute(
        {"action": "list"},
        context,
    )

    assert list_result.success is True
    assert list_result.data["count"] == 3
    assert len(list_result.data["reminders"]) == 3


@pytest.mark.asyncio
async def test_search_reminders(reminder_ability, context):
    """Test searching reminders."""
    await reminder_ability.initialize()

    # Create reminders with different categories
    await reminder_ability.execute(
        {
            "action": "create",
            "title": "Work Task",
            "when": "tomorrow",
            "category": "work",
        },
        context,
    )

    await reminder_ability.execute(
        {
            "action": "create",
            "title": "Personal Task",
            "when": "in 2 days",
            "category": "personal",
        },
        context,
    )

    # Search for work reminders
    search_result = await reminder_ability.execute(
        {
            "action": "search",
            "search_query": "work",
        },
        context,
    )

    assert search_result.success is True
    assert search_result.data["count"] == 1
    assert search_result.data["reminders"][0]["category"] == "work"


@pytest.mark.asyncio
async def test_reminder_status(reminder_ability, context):
    """Test getting reminder status."""
    await reminder_ability.initialize()

    # Create reminder
    create_result = await reminder_ability.execute(
        {
            "action": "create",
            "title": "Status Test",
            "when": "in 4 hours",
            "description": "Test description",
            "priority": "high",
        },
        context,
    )

    assert create_result.success is True
    reminder_id = create_result.data["reminder_id"]

    # Get status
    status_result = await reminder_ability.execute(
        {
            "action": "status",
            "reminder_id": reminder_id,
        },
        context,
    )

    assert status_result.success is True
    assert status_result.data["reminder_id"] == reminder_id
    assert status_result.data["title"] == "Status Test"
    assert status_result.data["description"] == "Test description"
    assert status_result.data["priority"] == "high"


@pytest.mark.asyncio
async def test_reminder_trigger(reminder_ability, context):
    """Test that reminders trigger at the right time."""
    await reminder_ability.initialize()

    triggered = []

    async def callback(reminder):
        triggered.append(reminder.reminder_id)

    # Create reminder
    result = await reminder_ability.execute(
        {
            "action": "create",
            "title": "Trigger Test",
            "when": "in 1 hour",
        },
        context,
    )

    assert result.success is True
    reminder_id = result.data["reminder_id"]

    # Manually adjust the reminder to trigger soon
    reminder = reminder_ability._reminders[reminder_id]
    reminder.callback = callback
    # Set remind_at to trigger in 2 seconds
    reminder.remind_at = datetime.now(pytz.UTC) + timedelta(seconds=2)

    # Wait for reminder to trigger
    await asyncio.sleep(3)

    # Check that reminder was triggered
    assert reminder_id in triggered

    # Check reminder state
    status_result = await reminder_ability.execute(
        {
            "action": "status",
            "reminder_id": reminder_id,
        },
        context,
    )

    assert status_result.success is True
    assert status_result.data["state"] == ReminderState.COMPLETED.value


@pytest.mark.asyncio
async def test_recurring_reminder(reminder_ability, context):
    """Test recurring reminders."""
    await reminder_ability.initialize()

    # Create recurring reminder
    result = await reminder_ability.execute(
        {
            "action": "create",
            "title": "Daily Standup",
            "when": "in 2 hours",
            "recurring_days": 1,  # Daily
        },
        context,
    )

    assert result.success is True
    assert result.data["recurring"] is True


@pytest.mark.asyncio
async def test_multiple_users(reminder_ability):
    """Test that users can't access each other's reminders."""
    await reminder_ability.initialize()

    context1 = AbilityContext(user_id="user1", session_id="session1")
    context2 = AbilityContext(user_id="user2", session_id="session2")

    # User 1 creates a reminder
    result1 = await reminder_ability.execute(
        {
            "action": "create",
            "title": "User 1 Reminder",
            "when": "tomorrow",
        },
        context1,
    )

    assert result1.success is True
    reminder_id = result1.data["reminder_id"]

    # User 2 tries to complete user 1's reminder
    result2 = await reminder_ability.execute(
        {
            "action": "complete",
            "reminder_id": reminder_id,
        },
        context2,
    )

    assert result2.success is False
    assert "permission" in result2.error.lower()


@pytest.mark.asyncio
async def test_invalid_action(reminder_ability, context):
    """Test that invalid actions are rejected."""
    result = await reminder_ability.execute(
        {
            "action": "invalid_action",
        },
        context,
    )

    assert result.success is False
    assert "unknown action" in result.error.lower()


@pytest.mark.asyncio
async def test_invalid_priority(reminder_ability, context):
    """Test that invalid priority is rejected."""
    result = await reminder_ability.execute(
        {
            "action": "create",
            "title": "Test",
            "when": "tomorrow",
            "priority": "invalid",
        },
        context,
    )

    assert result.success is False
    assert "priority" in result.error.lower()


@pytest.mark.asyncio
async def test_reminder_cleanup(reminder_ability, context):
    """Test that reminders are cleaned up properly."""
    await reminder_ability.initialize()

    # Create multiple reminders
    for i in range(3):
        await reminder_ability.execute(
            {
                "action": "create",
                "title": f"Reminder {i}",
                "when": "tomorrow",
            },
            context,
        )

    # Clean up
    await reminder_ability._cleanup()

    # Verify all reminders are cleared
    assert len(reminder_ability._reminders) == 0
    assert len(reminder_ability._user_reminders) == 0
    assert reminder_ability._monitor_task.done()
