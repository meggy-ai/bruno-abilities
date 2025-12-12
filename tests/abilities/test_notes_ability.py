"""Tests for notes ability."""

import pytest

from bruno_abilities.abilities.notes_ability import NotesAbility
from bruno_abilities.base.ability_base import AbilityContext


@pytest.fixture
def notes_ability():
    """Create a notes ability instance."""
    return NotesAbility()


@pytest.fixture
def context():
    """Create an ability context."""
    return AbilityContext(
        user_id="test_user",
        session_id="test_session",
    )


@pytest.mark.asyncio
async def test_notes_metadata(notes_ability):
    """Test that notes ability has proper metadata."""
    metadata = notes_ability.metadata

    assert metadata.name == "notes"
    assert metadata.display_name == "Notes"
    assert "notes" in metadata.description.lower()
    assert "notes" in metadata.tags


@pytest.mark.asyncio
async def test_create_note_basic(notes_ability, context):
    """Test creating a basic note."""
    result = await notes_ability.execute(
        {
            "action": "create",
            "title": "Test Note",
            "content": "This is a test note",
        },
        context,
    )

    assert result.success is True
    assert "note_id" in result.data
    assert result.data["title"] == "Test Note"


@pytest.mark.asyncio
async def test_create_note_without_title(notes_ability, context):
    """Test that creating a note without title fails."""
    result = await notes_ability.execute(
        {
            "action": "create",
            "content": "Content without title",
        },
        context,
    )

    assert result.success is False
    assert "title" in result.error.lower()


@pytest.mark.asyncio
async def test_create_note_with_tags(notes_ability, context):
    """Test creating a note with tags."""
    result = await notes_ability.execute(
        {
            "action": "create",
            "title": "Tagged Note",
            "content": "Note with tags",
            "tags": "important,work,project",
        },
        context,
    )

    assert result.success is True
    assert len(result.data["tags"]) == 3
    assert "important" in result.data["tags"]


@pytest.mark.asyncio
async def test_create_note_with_category_and_folder(notes_ability, context):
    """Test creating a note with category and folder."""
    result = await notes_ability.execute(
        {
            "action": "create",
            "title": "Organized Note",
            "content": "Well organized",
            "category": "work",
            "folder": "Projects/Important",
        },
        context,
    )

    assert result.success is True
    assert result.data["category"] == "work"
    assert result.data["folder"] == "Projects/Important"


@pytest.mark.asyncio
async def test_create_note_from_template(notes_ability, context):
    """Test creating a note from a template."""
    result = await notes_ability.execute(
        {
            "action": "create",
            "title": "Team Meeting",
            "template": "meeting",
        },
        context,
    )

    assert result.success is True
    note_id = result.data["note_id"]

    # Read the note to verify template was applied
    read_result = await notes_ability.execute(
        {
            "action": "read",
            "note_id": note_id,
        },
        context,
    )

    assert "Agenda" in read_result.data["content"]
    assert "Action Items" in read_result.data["content"]


@pytest.mark.asyncio
async def test_create_note_with_invalid_template(notes_ability, context):
    """Test that invalid template is rejected."""
    result = await notes_ability.execute(
        {
            "action": "create",
            "title": "Test",
            "template": "nonexistent",
        },
        context,
    )

    assert result.success is False
    assert "template" in result.error.lower()


@pytest.mark.asyncio
async def test_read_note(notes_ability, context):
    """Test reading a note."""
    # Create note
    create_result = await notes_ability.execute(
        {
            "action": "create",
            "title": "Read Test",
            "content": "# Test Content\n\nThis is a test.",
            "tags": "test",
        },
        context,
    )

    note_id = create_result.data["note_id"]

    # Read note
    read_result = await notes_ability.execute(
        {
            "action": "read",
            "note_id": note_id,
        },
        context,
    )

    assert read_result.success is True
    assert read_result.data["title"] == "Read Test"
    assert "Test Content" in read_result.data["content"]
    assert "test" in read_result.data["tags"]


@pytest.mark.asyncio
async def test_update_note_content(notes_ability, context):
    """Test updating note content."""
    # Create note
    create_result = await notes_ability.execute(
        {
            "action": "create",
            "title": "Update Test",
            "content": "Original content",
        },
        context,
    )

    note_id = create_result.data["note_id"]

    # Update content
    update_result = await notes_ability.execute(
        {
            "action": "update",
            "note_id": note_id,
            "content": "Updated content",
        },
        context,
    )

    assert update_result.success is True
    assert update_result.data["version"] == 2
    assert "content" in update_result.data["changes"]

    # Verify update
    read_result = await notes_ability.execute(
        {"action": "read", "note_id": note_id},
        context,
    )

    assert read_result.data["content"] == "Updated content"


@pytest.mark.asyncio
async def test_update_note_metadata(notes_ability, context):
    """Test updating note metadata."""
    # Create note
    create_result = await notes_ability.execute(
        {
            "action": "create",
            "title": "Original Title",
            "content": "Content",
        },
        context,
    )

    note_id = create_result.data["note_id"]

    # Update metadata
    update_result = await notes_ability.execute(
        {
            "action": "update",
            "note_id": note_id,
            "title": "New Title",
            "category": "updated",
            "tags": "new,tags",
        },
        context,
    )

    assert update_result.success is True
    assert "title" in update_result.data["changes"]
    assert "category" in update_result.data["changes"]
    assert "tags" in update_result.data["changes"]


@pytest.mark.asyncio
async def test_delete_note(notes_ability, context):
    """Test deleting a note."""
    # Create note
    create_result = await notes_ability.execute(
        {
            "action": "create",
            "title": "Delete Test",
            "content": "To be deleted",
        },
        context,
    )

    note_id = create_result.data["note_id"]

    # Delete note
    delete_result = await notes_ability.execute(
        {
            "action": "delete",
            "note_id": note_id,
        },
        context,
    )

    assert delete_result.success is True

    # Verify deletion
    read_result = await notes_ability.execute(
        {"action": "read", "note_id": note_id},
        context,
    )

    assert read_result.success is False
    assert "not found" in read_result.error.lower()


@pytest.mark.asyncio
async def test_search_notes(notes_ability, context):
    """Test searching for notes."""
    # Create multiple notes
    await notes_ability.execute(
        {
            "action": "create",
            "title": "Python Tutorial",
            "content": "Learning Python",
            "tags": "programming",
        },
        context,
    )

    await notes_ability.execute(
        {
            "action": "create",
            "title": "JavaScript Guide",
            "content": "Learning JavaScript",
            "tags": "programming",
        },
        context,
    )

    await notes_ability.execute(
        {
            "action": "create",
            "title": "Shopping List",
            "content": "Buy groceries",
            "tags": "personal",
        },
        context,
    )

    # Search for programming notes
    search_result = await notes_ability.execute(
        {
            "action": "search",
            "search_query": "programming",
        },
        context,
    )

    assert search_result.success is True
    assert search_result.data["count"] == 2

    # Search in content
    search_result2 = await notes_ability.execute(
        {
            "action": "search",
            "search_query": "python",
        },
        context,
    )

    assert search_result2.success is True
    assert search_result2.data["count"] == 1


@pytest.mark.asyncio
async def test_list_notes(notes_ability, context):
    """Test listing all notes."""
    # Create multiple notes
    for i in range(3):
        await notes_ability.execute(
            {
                "action": "create",
                "title": f"Note {i}",
                "content": f"Content {i}",
            },
            context,
        )

    # List notes
    list_result = await notes_ability.execute(
        {"action": "list"},
        context,
    )

    assert list_result.success is True
    assert list_result.data["count"] == 3


@pytest.mark.asyncio
async def test_archive_note(notes_ability, context):
    """Test archiving a note."""
    # Create note
    create_result = await notes_ability.execute(
        {
            "action": "create",
            "title": "Archive Test",
            "content": "To be archived",
        },
        context,
    )

    note_id = create_result.data["note_id"]

    # Archive note
    archive_result = await notes_ability.execute(
        {
            "action": "archive",
            "note_id": note_id,
        },
        context,
    )

    assert archive_result.success is True
    assert archive_result.data["archived"] is True

    # Verify archived note not in list by default
    list_result = await notes_ability.execute(
        {"action": "list"},
        context,
    )

    assert list_result.data["count"] == 0

    # Verify archived note in list when requested
    list_result2 = await notes_ability.execute(
        {"action": "list", "show_archived": True},
        context,
    )

    assert list_result2.data["count"] == 1


@pytest.mark.asyncio
async def test_unarchive_note(notes_ability, context):
    """Test unarchiving a note."""
    # Create and archive note
    create_result = await notes_ability.execute(
        {
            "action": "create",
            "title": "Unarchive Test",
            "content": "Test",
        },
        context,
    )

    note_id = create_result.data["note_id"]

    await notes_ability.execute(
        {"action": "archive", "note_id": note_id},
        context,
    )

    # Unarchive note (toggle)
    unarchive_result = await notes_ability.execute(
        {
            "action": "archive",
            "note_id": note_id,
        },
        context,
    )

    assert unarchive_result.success is True
    assert unarchive_result.data["archived"] is False


@pytest.mark.asyncio
async def test_link_notes(notes_ability, context):
    """Test linking two notes."""
    # Create two notes
    result1 = await notes_ability.execute(
        {"action": "create", "title": "Note 1", "content": "First note"},
        context,
    )

    result2 = await notes_ability.execute(
        {"action": "create", "title": "Note 2", "content": "Second note"},
        context,
    )

    note_id1 = result1.data["note_id"]
    note_id2 = result2.data["note_id"]

    # Link notes
    link_result = await notes_ability.execute(
        {
            "action": "link",
            "note_id": note_id1,
            "linked_note_id": note_id2,
        },
        context,
    )

    assert link_result.success is True

    # Verify bidirectional link
    read_result1 = await notes_ability.execute(
        {"action": "read", "note_id": note_id1},
        context,
    )

    read_result2 = await notes_ability.execute(
        {"action": "read", "note_id": note_id2},
        context,
    )

    assert note_id2 in read_result1.data["linked_notes"]
    assert note_id1 in read_result2.data["linked_notes"]


@pytest.mark.asyncio
async def test_list_templates(notes_ability, context):
    """Test listing available templates."""
    result = await notes_ability.execute(
        {"action": "list_templates"},
        context,
    )

    assert result.success is True
    assert result.data["count"] >= 3  # blank, meeting, daily
    template_ids = [t["template_id"] for t in result.data["templates"]]
    assert "blank" in template_ids
    assert "meeting" in template_ids
    assert "daily" in template_ids


@pytest.mark.asyncio
async def test_version_history(notes_ability, context):
    """Test that version history is maintained."""
    # Create note
    create_result = await notes_ability.execute(
        {
            "action": "create",
            "title": "Version Test",
            "content": "Version 1",
        },
        context,
    )

    note_id = create_result.data["note_id"]

    # Update multiple times
    for i in range(2, 5):
        await notes_ability.execute(
            {
                "action": "update",
                "note_id": note_id,
                "content": f"Version {i}",
            },
            context,
        )

    # Read and check version
    read_result = await notes_ability.execute(
        {"action": "read", "note_id": note_id},
        context,
    )

    assert read_result.data["version"] == 4


@pytest.mark.asyncio
async def test_multiple_users(notes_ability):
    """Test that users can't access each other's notes."""
    context1 = AbilityContext(user_id="user1", session_id="session1")
    context2 = AbilityContext(user_id="user2", session_id="session2")

    # User 1 creates a note
    result1 = await notes_ability.execute(
        {
            "action": "create",
            "title": "User 1 Note",
            "content": "Private",
        },
        context1,
    )

    note_id = result1.data["note_id"]

    # User 2 tries to read user 1's note
    result2 = await notes_ability.execute(
        {
            "action": "read",
            "note_id": note_id,
        },
        context2,
    )

    assert result2.success is False
    assert "permission" in result2.error.lower()


@pytest.mark.asyncio
async def test_invalid_action(notes_ability, context):
    """Test that invalid actions are rejected."""
    result = await notes_ability.execute(
        {
            "action": "invalid_action",
        },
        context,
    )

    assert result.success is False
    assert "unknown action" in result.error.lower()


@pytest.mark.asyncio
async def test_notes_cleanup(notes_ability, context):
    """Test that notes are cleaned up properly."""
    # Create multiple notes
    for i in range(3):
        await notes_ability.execute(
            {
                "action": "create",
                "title": f"Note {i}",
                "content": "Test",
            },
            context,
        )

    # Clean up
    await notes_ability._cleanup()

    # Verify all notes are cleared
    assert len(notes_ability._notes) == 0
    assert len(notes_ability._user_notes) == 0
