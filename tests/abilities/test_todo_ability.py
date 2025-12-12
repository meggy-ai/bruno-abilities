"""Tests for TodoAbility."""

import pytest

from bruno_abilities.abilities.todo_ability import TodoAbility
from bruno_abilities.base.ability_base import AbilityContext


@pytest.fixture
def todo():
    """Create a todo ability instance."""
    return TodoAbility()


@pytest.fixture
def context():
    """Create a basic context."""
    return AbilityContext(user_id="user1")


@pytest.fixture
def other_context():
    """Create another user context."""
    return AbilityContext(user_id="user2")


@pytest.mark.asyncio
async def test_todo_metadata(todo):
    """Test todo ability metadata."""
    metadata = todo.metadata
    assert metadata.name == "todo"
    assert metadata.display_name == "To-Do List"
    assert "information_storage" in metadata.category
    assert metadata.version == "1.0.0"
    assert len(metadata.parameters) > 0


@pytest.mark.asyncio
async def test_create_task_basic(todo, context):
    """Test creating a basic task."""
    result = await todo.execute(
        {"action": "create", "title": "Buy groceries"},
        context,
    )

    assert result.success is True
    assert "task_id" in result.data
    assert result.data["title"] == "Buy groceries"
    assert result.data["priority"] == "medium"


@pytest.mark.asyncio
async def test_create_task_without_title(todo, context):
    """Test creating task without title fails."""
    result = await todo.execute(
        {"action": "create"},
        context,
    )

    assert result.success is False
    assert "Title is required" in result.error


@pytest.mark.asyncio
async def test_create_task_with_priority(todo, context):
    """Test creating task with priority."""
    result = await todo.execute(
        {
            "action": "create",
            "title": "Urgent task",
            "priority": "urgent",
            "description": "This is urgent",
        },
        context,
    )

    assert result.success is True
    assert result.data["priority"] == "urgent"


@pytest.mark.asyncio
async def test_create_task_with_due_date(todo, context):
    """Test creating task with due date."""
    result = await todo.execute(
        {
            "action": "create",
            "title": "Meeting prep",
            "due_date": "tomorrow",
        },
        context,
    )

    assert result.success is True
    assert result.data["due_date"] is not None


@pytest.mark.asyncio
async def test_create_task_with_tags(todo, context):
    """Test creating task with tags."""
    result = await todo.execute(
        {
            "action": "create",
            "title": "Review code",
            "tags": "review,urgent,code",
        },
        context,
    )

    assert result.success is True


@pytest.mark.asyncio
async def test_create_task_with_project(todo, context):
    """Test creating task with project and category."""
    result = await todo.execute(
        {
            "action": "create",
            "title": "Design mockups",
            "project": "Website Redesign",
            "category": "design",
        },
        context,
    )

    assert result.success is True


@pytest.mark.asyncio
async def test_create_recurring_task(todo, context):
    """Test creating recurring task."""
    result = await todo.execute(
        {
            "action": "create",
            "title": "Daily standup",
            "recurrence": "daily",
            "due_date": "tomorrow 9am",
        },
        context,
    )

    assert result.success is True
    assert result.data["recurrence"] == "daily"


@pytest.mark.asyncio
async def test_list_tasks(todo, context):
    """Test listing tasks."""
    # Create multiple tasks
    await todo.execute(
        {"action": "create", "title": "Task 1", "priority": "high"},
        context,
    )
    await todo.execute(
        {"action": "create", "title": "Task 2", "priority": "low"},
        context,
    )
    await todo.execute(
        {"action": "create", "title": "Task 3", "priority": "urgent"},
        context,
    )

    result = await todo.execute({"action": "list"}, context)

    assert result.success is True
    assert result.data["count"] == 3
    assert len(result.data["tasks"]) == 3
    # Check sorting: urgent should be first
    assert result.data["tasks"][0]["priority"] == "urgent"


@pytest.mark.asyncio
async def test_list_tasks_with_status_filter(todo, context):
    """Test listing tasks with status filter."""
    # Create and complete a task
    create_result = await todo.execute(
        {"action": "create", "title": "Task 1"},
        context,
    )
    task_id = create_result.data["task_id"]

    await todo.execute(
        {"action": "complete", "task_id": task_id},
        context,
    )

    # Create another task
    await todo.execute(
        {"action": "create", "title": "Task 2"},
        context,
    )

    # List only completed tasks
    result = await todo.execute(
        {"action": "list", "status": "completed"},
        context,
    )

    assert result.success is True
    assert result.data["count"] == 1


@pytest.mark.asyncio
async def test_update_task(todo, context):
    """Test updating task."""
    # Create task
    create_result = await todo.execute(
        {"action": "create", "title": "Original title"},
        context,
    )
    task_id = create_result.data["task_id"]

    # Update task
    result = await todo.execute(
        {
            "action": "update",
            "task_id": task_id,
            "title": "Updated title",
            "priority": "high",
            "project": "New Project",
        },
        context,
    )

    assert result.success is True
    assert result.data["title"] == "Updated title"
    assert "priority" in result.data["changes"]


@pytest.mark.asyncio
async def test_update_task_without_id(todo, context):
    """Test updating task without task_id fails."""
    result = await todo.execute(
        {"action": "update", "title": "New title"},
        context,
    )

    assert result.success is False
    assert "task_id is required" in result.error


@pytest.mark.asyncio
async def test_complete_task(todo, context):
    """Test completing task."""
    # Create task
    create_result = await todo.execute(
        {"action": "create", "title": "Finish report"},
        context,
    )
    task_id = create_result.data["task_id"]

    # Complete task
    result = await todo.execute(
        {"action": "complete", "task_id": task_id},
        context,
    )

    assert result.success is True
    assert result.data["status"] == "completed"
    assert result.data["completed_at"] is not None
    assert result.data["completion_count"] == 1


@pytest.mark.asyncio
async def test_complete_recurring_task(todo, context):
    """Test completing recurring task resets it."""
    # Create recurring task
    create_result = await todo.execute(
        {
            "action": "create",
            "title": "Weekly review",
            "recurrence": "weekly",
            "due_date": "tomorrow",  # Use "tomorrow" instead of "next Monday"
        },
        context,
    )

    # Check if creation was successful
    if not create_result.success:
        pytest.fail(f"Failed to create task: {create_result.error}")

    task_id = create_result.data["task_id"]

    # Complete task
    result = await todo.execute(
        {"action": "complete", "task_id": task_id},
        context,
    )

    assert result.success is True
    assert result.data["recurring"] is True
    assert result.data["status"] == "todo"  # Reset to todo
    assert result.data["completion_count"] == 1


@pytest.mark.asyncio
async def test_cancel_task(todo, context):
    """Test cancelling task."""
    # Create task
    create_result = await todo.execute(
        {"action": "create", "title": "Meeting"},
        context,
    )
    task_id = create_result.data["task_id"]

    # Cancel task
    result = await todo.execute(
        {"action": "cancel", "task_id": task_id},
        context,
    )

    assert result.success is True
    assert result.data["status"] == "cancelled"


@pytest.mark.asyncio
async def test_delete_task(todo, context):
    """Test deleting task."""
    # Create task
    create_result = await todo.execute(
        {"action": "create", "title": "Temporary task"},
        context,
    )
    task_id = create_result.data["task_id"]

    # Delete task
    result = await todo.execute(
        {"action": "delete", "task_id": task_id},
        context,
    )

    assert result.success is True

    # Verify task is gone
    list_result = await todo.execute({"action": "list"}, context)
    assert list_result.data["count"] == 0


@pytest.mark.asyncio
async def test_search_tasks(todo, context):
    """Test searching tasks."""
    # Create tasks with different content
    await todo.execute(
        {"action": "create", "title": "Python project", "tags": "coding"},
        context,
    )
    await todo.execute(
        {"action": "create", "title": "Meeting notes", "category": "work"},
        context,
    )
    await todo.execute(
        {"action": "create", "title": "Buy python book", "tags": "shopping"},
        context,
    )

    # Search for "python"
    result = await todo.execute(
        {"action": "search", "search_query": "python"},
        context,
    )

    assert result.success is True
    assert result.data["count"] == 2  # Two tasks contain "python"


@pytest.mark.asyncio
async def test_search_tasks_without_query(todo, context):
    """Test searching without query fails."""
    result = await todo.execute(
        {"action": "search"},
        context,
    )

    assert result.success is False
    assert "search_query is required" in result.error


@pytest.mark.asyncio
async def test_task_dependencies(todo, context):
    """Test task dependencies."""
    # Create first task
    task1_result = await todo.execute(
        {"action": "create", "title": "Write code"},
        context,
    )
    task1_id = task1_result.data["task_id"]

    # Create second task depending on first
    task2_result = await todo.execute(
        {
            "action": "create",
            "title": "Test code",
            "depends_on": task1_id,
        },
        context,
    )

    assert task2_result.success is True
    assert task1_id in task2_result.data["depends_on"]


@pytest.mark.asyncio
async def test_blocked_by_dependency(todo, context):
    """Test that task with incomplete dependency cannot be completed."""
    # Create dependency task
    task1_result = await todo.execute(
        {"action": "create", "title": "Prepare data"},
        context,
    )
    task1_id = task1_result.data["task_id"]

    # Create dependent task
    task2_result = await todo.execute(
        {
            "action": "create",
            "title": "Analyze data",
            "depends_on": task1_id,
        },
        context,
    )
    task2_id = task2_result.data["task_id"]

    # Try to complete dependent task without completing dependency
    result = await todo.execute(
        {"action": "complete", "task_id": task2_id},
        context,
    )

    assert result.success is False
    assert "dependency" in result.error.lower()


@pytest.mark.asyncio
async def test_complete_with_dependency_met(todo, context):
    """Test completing task after dependency is met."""
    # Create and complete first task
    task1_result = await todo.execute(
        {"action": "create", "title": "First task"},
        context,
    )
    task1_id = task1_result.data["task_id"]

    await todo.execute(
        {"action": "complete", "task_id": task1_id},
        context,
    )

    # Create dependent task
    task2_result = await todo.execute(
        {
            "action": "create",
            "title": "Second task",
            "depends_on": task1_id,
        },
        context,
    )
    task2_id = task2_result.data["task_id"]

    # Should be able to complete now
    result = await todo.execute(
        {"action": "complete", "task_id": task2_id},
        context,
    )

    assert result.success is True


@pytest.mark.asyncio
async def test_create_subtask(todo, context):
    """Test creating subtask."""
    # Create parent task
    parent_result = await todo.execute(
        {"action": "create", "title": "Project milestone"},
        context,
    )
    parent_id = parent_result.data["task_id"]

    # Create subtask
    result = await todo.execute(
        {
            "action": "add_subtask",
            "parent_task": parent_id,
            "title": "Subtask 1",
        },
        context,
    )

    assert result.success is True


@pytest.mark.asyncio
async def test_list_shows_subtask_count(todo, context):
    """Test that list shows subtask count."""
    # Create parent task
    parent_result = await todo.execute(
        {"action": "create", "title": "Parent"},
        context,
    )
    parent_id = parent_result.data["task_id"]

    # Create subtasks
    await todo.execute(
        {
            "action": "add_subtask",
            "parent_task": parent_id,
            "title": "Sub 1",
        },
        context,
    )
    await todo.execute(
        {
            "action": "add_subtask",
            "parent_task": parent_id,
            "title": "Sub 2",
        },
        context,
    )

    # List tasks
    result = await todo.execute({"action": "list"}, context)

    # Find parent in results
    parent_data = next((t for t in result.data["tasks"] if t["task_id"] == parent_id), None)

    assert parent_data is not None
    assert parent_data["subtasks_count"] == 2


@pytest.mark.asyncio
async def test_get_stats(todo, context):
    """Test getting productivity statistics."""
    # Create various tasks
    await todo.execute(
        {"action": "create", "title": "Task 1", "priority": "high"},
        context,
    )
    await todo.execute(
        {"action": "create", "title": "Task 2", "priority": "low"},
        context,
    )

    task3_result = await todo.execute(
        {"action": "create", "title": "Task 3", "project": "Project A"},
        context,
    )

    # Complete one task
    await todo.execute(
        {"action": "complete", "task_id": task3_result.data["task_id"]},
        context,
    )

    # Get stats
    result = await todo.execute({"action": "stats"}, context)

    assert result.success is True
    assert result.data["total_tasks"] == 3
    assert result.data["completed"] == 1
    assert result.data["todo"] == 2
    assert result.data["completion_rate"] > 0
    assert "Project A" in result.data["by_project"]


@pytest.mark.asyncio
async def test_stats_overdue_tasks(todo, context):
    """Test stats show overdue tasks."""
    # Create task with past due date
    await todo.execute(
        {
            "action": "create",
            "title": "Overdue task",
            "due_date": "yesterday",
        },
        context,
    )

    # Get stats
    result = await todo.execute({"action": "stats"}, context)

    assert result.success is True
    assert result.data["overdue"] >= 1


@pytest.mark.asyncio
async def test_multiple_users(todo, context, other_context):
    """Test that users can only see their own tasks."""
    # User 1 creates task
    await todo.execute(
        {"action": "create", "title": "User 1 task"},
        context,
    )

    # User 2 creates task
    await todo.execute(
        {"action": "create", "title": "User 2 task"},
        other_context,
    )

    # Each user should only see their own task
    user1_list = await todo.execute({"action": "list"}, context)
    user2_list = await todo.execute({"action": "list"}, other_context)

    assert user1_list.data["count"] == 1
    assert user2_list.data["count"] == 1


@pytest.mark.asyncio
async def test_permission_denied_update(todo, context, other_context):
    """Test that users cannot update other users' tasks."""
    # User 1 creates task
    create_result = await todo.execute(
        {"action": "create", "title": "User 1 task"},
        context,
    )
    task_id = create_result.data["task_id"]

    # User 2 tries to update it
    result = await todo.execute(
        {
            "action": "update",
            "task_id": task_id,
            "title": "Hacked",
        },
        other_context,
    )

    assert result.success is False
    assert "permission" in result.error.lower()


@pytest.mark.asyncio
async def test_invalid_action(todo, context):
    """Test invalid action."""
    result = await todo.execute(
        {"action": "invalid_action"},
        context,
    )

    assert result.success is False
    assert "Unknown action" in result.error


@pytest.mark.asyncio
async def test_invalid_priority(todo, context):
    """Test creating task with invalid priority."""
    result = await todo.execute(
        {
            "action": "create",
            "title": "Task",
            "priority": "super_duper_urgent",
        },
        context,
    )

    assert result.success is False
    assert "Invalid priority" in result.error


@pytest.mark.asyncio
async def test_invalid_recurrence(todo, context):
    """Test creating task with invalid recurrence."""
    result = await todo.execute(
        {
            "action": "create",
            "title": "Task",
            "recurrence": "every_blue_moon",
        },
        context,
    )

    assert result.success is False
    assert "Invalid recurrence" in result.error


@pytest.mark.asyncio
async def test_invalid_dependency(todo, context):
    """Test creating task with non-existent dependency."""
    result = await todo.execute(
        {
            "action": "create",
            "title": "Task",
            "depends_on": "nonexistent_task_id",
        },
        context,
    )

    assert result.success is False
    assert "Dependency task not found" in result.error


@pytest.mark.asyncio
async def test_todo_cleanup(todo, context):
    """Test cleanup removes all tasks."""
    # Create some tasks
    await todo.execute(
        {"action": "create", "title": "Task 1"},
        context,
    )
    await todo.execute(
        {"action": "create", "title": "Task 2"},
        context,
    )

    # Cleanup
    await todo._cleanup()

    # Verify all tasks are gone
    result = await todo.execute({"action": "list"}, context)
    assert result.data["count"] == 0
