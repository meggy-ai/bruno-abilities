"""Tests for MusicAbility."""

import os
import tempfile
from unittest.mock import Mock, patch

import pygame
import pytest

from bruno_abilities.abilities.music_ability import MusicAbility
from bruno_abilities.base.ability_base import AbilityContext


@pytest.fixture
def music():
    """Create a music ability instance with mocked pygame."""
    with (
        patch("pygame.mixer.init"),
        patch("pygame.mixer.music.set_volume"),
        patch("pygame.mixer.quit"),
    ):
        ability = MusicAbility()
        yield ability
        # Cleanup
        pygame.mixer.music.stop = Mock()
        pygame.mixer.quit = Mock()


@pytest.fixture
def context():
    """Create a basic context."""
    return AbilityContext(user_id="user1")


@pytest.fixture
def other_context():
    """Create another user context."""
    return AbilityContext(user_id="user2")


@pytest.fixture
def temp_audio_file():
    """Create a temporary audio file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(b"fake audio data")
        temp_path = f.name

    yield temp_path

    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


@pytest.mark.asyncio
async def test_music_metadata(music):
    """Test music ability metadata."""
    metadata = music.metadata
    assert metadata.name == "music"
    assert metadata.display_name == "Music Control"
    assert "entertainment" in metadata.category
    assert metadata.version == "1.0.0"
    assert len(metadata.parameters) > 0


@pytest.mark.asyncio
async def test_play_from_file(music, context, temp_audio_file):
    """Test playing music from file path."""
    with patch("pygame.mixer.music.load"), patch("pygame.mixer.music.play"):
        result = await music.execute({"action": "play", "file_path": temp_audio_file}, context)

        assert result.success is True
        assert "title" in result.data
        assert result.data["state"] == "playing"


@pytest.mark.asyncio
async def test_play_nonexistent_file(music, context):
    """Test playing nonexistent file fails."""
    result = await music.execute({"action": "play", "file_path": "/nonexistent/file.mp3"}, context)

    assert result.success is False
    assert "not found" in result.error.lower()


@pytest.mark.asyncio
async def test_play_without_parameters(music, context):
    """Test playing without parameters fails."""
    result = await music.execute({"action": "play"}, context)

    assert result.success is False
    assert "must provide" in result.error.lower()


@pytest.mark.asyncio
async def test_pause_playback(music, context, temp_audio_file):
    """Test pausing playback."""
    # Start playback
    with patch("pygame.mixer.music.load"), patch("pygame.mixer.music.play"):
        await music.execute({"action": "play", "file_path": temp_audio_file}, context)

    # Pause
    with patch("pygame.mixer.music.pause"):
        result = await music.execute({"action": "pause"}, context)

        assert result.success is True
        assert result.data["state"] == "paused"


@pytest.mark.asyncio
async def test_pause_without_playing(music, context):
    """Test pausing when nothing is playing fails."""
    result = await music.execute({"action": "pause"}, context)

    assert result.success is False
    assert "nothing is currently playing" in result.error.lower()


@pytest.mark.asyncio
async def test_resume_from_pause(music, context, temp_audio_file):
    """Test resuming paused playback."""
    # Start and pause
    with patch("pygame.mixer.music.load"), patch("pygame.mixer.music.play"):
        await music.execute({"action": "play", "file_path": temp_audio_file}, context)

    with patch("pygame.mixer.music.pause"):
        await music.execute({"action": "pause"}, context)

    # Resume
    with patch("pygame.mixer.music.unpause"):
        result = await music.execute({"action": "play"}, context)

        assert result.success is True
        assert result.data["state"] == "playing"
        assert "resumed" in result.data["message"].lower()


@pytest.mark.asyncio
async def test_stop_playback(music, context, temp_audio_file):
    """Test stopping playback."""
    # Start playback
    with patch("pygame.mixer.music.load"), patch("pygame.mixer.music.play"):
        await music.execute({"action": "play", "file_path": temp_audio_file}, context)

    # Stop
    with patch("pygame.mixer.music.stop"):
        result = await music.execute({"action": "stop"}, context)

        assert result.success is True
        assert result.data["state"] == "stopped"


@pytest.mark.asyncio
async def test_stop_without_playing(music, context):
    """Test stopping when nothing is playing fails."""
    result = await music.execute({"action": "stop"}, context)

    assert result.success is False
    assert "nothing is currently playing" in result.error.lower()


@pytest.mark.asyncio
async def test_set_volume(music, context):
    """Test setting volume."""
    with patch("pygame.mixer.music.set_volume") as mock_set_volume:
        result = await music.execute({"action": "volume", "volume": 0.5}, context)

        assert result.success is True
        assert result.data["volume"] == 0.5
        assert result.data["percentage"] == 50
        mock_set_volume.assert_called_once_with(0.5)


@pytest.mark.asyncio
async def test_set_volume_invalid(music, context):
    """Test setting invalid volume fails."""
    result = await music.execute({"action": "volume", "volume": 1.5}, context)

    assert result.success is False
    assert "between 0.0 and 1.0" in result.error.lower()


@pytest.mark.asyncio
async def test_set_volume_without_parameter(music, context):
    """Test setting volume without parameter fails."""
    result = await music.execute({"action": "volume"}, context)

    assert result.success is False
    assert "volume parameter is required" in result.error.lower()


@pytest.mark.asyncio
async def test_create_playlist(music, context):
    """Test creating a playlist."""
    result = await music.execute(
        {
            "action": "playlist",
            "sub_action": "create",
            "playlist_name": "My Favorites",
            "description": "Best songs",
        },
        context,
    )

    assert result.success is True
    assert "playlist_id" in result.data
    assert result.data["name"] == "My Favorites"


@pytest.mark.asyncio
async def test_create_playlist_without_name(music, context):
    """Test creating playlist without name fails."""
    result = await music.execute({"action": "playlist", "sub_action": "create"}, context)

    assert result.success is False
    assert "playlist_name is required" in result.error.lower()


@pytest.mark.asyncio
async def test_list_playlists(music, context):
    """Test listing playlists."""
    # Create some playlists
    await music.execute(
        {"action": "playlist", "sub_action": "create", "playlist_name": "Rock"},
        context,
    )
    await music.execute(
        {"action": "playlist", "sub_action": "create", "playlist_name": "Jazz"},
        context,
    )

    # List
    result = await music.execute({"action": "playlist", "sub_action": "list"}, context)

    assert result.success is True
    assert result.data["count"] == 2
    assert len(result.data["playlists"]) == 2


@pytest.mark.asyncio
async def test_add_track_to_playlist(music, context, temp_audio_file):
    """Test adding track to playlist."""
    # Create track
    with patch("pygame.mixer.music.load"), patch("pygame.mixer.music.play"):
        play_result = await music.execute({"action": "play", "file_path": temp_audio_file}, context)

    track_id = play_result.data["track_id"]

    # Create playlist
    playlist_result = await music.execute(
        {"action": "playlist", "sub_action": "create", "playlist_name": "Test"},
        context,
    )
    playlist_id = playlist_result.data["playlist_id"]

    # Add track to playlist
    result = await music.execute(
        {
            "action": "playlist",
            "sub_action": "add_track",
            "playlist_id": playlist_id,
            "track_id": track_id,
        },
        context,
    )

    assert result.success is True
    assert result.data["track_count"] == 1


@pytest.mark.asyncio
async def test_delete_playlist(music, context):
    """Test deleting playlist."""
    # Create playlist
    create_result = await music.execute(
        {"action": "playlist", "sub_action": "create", "playlist_name": "Temp"},
        context,
    )
    playlist_id = create_result.data["playlist_id"]

    # Delete
    result = await music.execute(
        {"action": "playlist", "sub_action": "delete", "playlist_id": playlist_id},
        context,
    )

    assert result.success is True

    # Verify deleted
    list_result = await music.execute({"action": "playlist", "sub_action": "list"}, context)
    assert list_result.data["count"] == 0


@pytest.mark.asyncio
async def test_play_playlist(music, context, temp_audio_file):
    """Test playing a playlist."""
    # Create track and playlist
    with patch("pygame.mixer.music.load"), patch("pygame.mixer.music.play"):
        play_result = await music.execute({"action": "play", "file_path": temp_audio_file}, context)

    track_id = play_result.data["track_id"]

    playlist_result = await music.execute(
        {"action": "playlist", "sub_action": "create", "playlist_name": "Test"},
        context,
    )
    playlist_id = playlist_result.data["playlist_id"]

    await music.execute(
        {
            "action": "playlist",
            "sub_action": "add_track",
            "playlist_id": playlist_id,
            "track_id": track_id,
        },
        context,
    )

    # Play playlist
    with patch("pygame.mixer.music.load"), patch("pygame.mixer.music.play"):
        result = await music.execute({"action": "play", "playlist_id": playlist_id}, context)

        assert result.success is True
        assert result.data["state"] == "playing"


@pytest.mark.asyncio
async def test_play_empty_playlist(music, context):
    """Test playing empty playlist fails."""
    # Create empty playlist
    playlist_result = await music.execute(
        {"action": "playlist", "sub_action": "create", "playlist_name": "Empty"},
        context,
    )
    playlist_id = playlist_result.data["playlist_id"]

    # Try to play
    result = await music.execute({"action": "play", "playlist_id": playlist_id}, context)

    assert result.success is False
    assert "empty" in result.error.lower()


@pytest.mark.asyncio
async def test_queue_operations(music, context, temp_audio_file):
    """Test queue management."""
    # Create track
    with patch("pygame.mixer.music.load"), patch("pygame.mixer.music.play"):
        play_result = await music.execute({"action": "play", "file_path": temp_audio_file}, context)

    track_id = play_result.data["track_id"]

    # Add to queue
    result = await music.execute(
        {"action": "queue", "sub_action": "add", "track_id": track_id}, context
    )

    assert result.success is True

    # List queue
    list_result = await music.execute({"action": "queue", "sub_action": "list"}, context)

    assert list_result.success is True
    assert list_result.data["total"] >= 1


@pytest.mark.asyncio
async def test_queue_clear(music, context, temp_audio_file):
    """Test clearing queue."""
    # Create and add track
    with patch("pygame.mixer.music.load"), patch("pygame.mixer.music.play"):
        play_result = await music.execute({"action": "play", "file_path": temp_audio_file}, context)

    track_id = play_result.data["track_id"]
    await music.execute({"action": "queue", "sub_action": "add", "track_id": track_id}, context)

    # Clear queue
    result = await music.execute({"action": "queue", "sub_action": "clear"}, context)

    assert result.success is True

    # Verify empty
    list_result = await music.execute({"action": "queue", "sub_action": "list"}, context)
    assert list_result.data["total"] == 0


@pytest.mark.asyncio
async def test_queue_shuffle(music, context):
    """Test shuffle toggle."""
    result = await music.execute({"action": "queue", "sub_action": "shuffle"}, context)

    assert result.success is True
    assert "shuffle" in result.data


@pytest.mark.asyncio
async def test_queue_repeat(music, context):
    """Test setting repeat mode."""
    result = await music.execute(
        {"action": "queue", "sub_action": "repeat", "repeat": "all"}, context
    )

    assert result.success is True
    assert result.data["repeat"] == "all"


@pytest.mark.asyncio
async def test_skip_track(music, context, temp_audio_file):
    """Test skipping to next track."""
    # Create playlist with track
    with patch("pygame.mixer.music.load"), patch("pygame.mixer.music.play"):
        play_result = await music.execute({"action": "play", "file_path": temp_audio_file}, context)

    track_id = play_result.data["track_id"]

    # Add to queue
    await music.execute({"action": "queue", "sub_action": "add", "track_id": track_id}, context)
    await music.execute({"action": "queue", "sub_action": "add", "track_id": track_id}, context)

    # Skip
    with (
        patch("pygame.mixer.music.load"),
        patch("pygame.mixer.music.play"),
        patch("pygame.mixer.music.stop"),
    ):
        result = await music.execute({"action": "skip"}, context)

        assert result.success is True


@pytest.mark.asyncio
async def test_previous_track(music, context, temp_audio_file):
    """Test going to previous track."""
    # Setup queue
    with patch("pygame.mixer.music.load"), patch("pygame.mixer.music.play"):
        play_result = await music.execute({"action": "play", "file_path": temp_audio_file}, context)

    track_id = play_result.data["track_id"]
    await music.execute({"action": "queue", "sub_action": "add", "track_id": track_id}, context)

    # Move forward then back
    with (
        patch("pygame.mixer.music.load"),
        patch("pygame.mixer.music.play"),
        patch("pygame.mixer.music.stop"),
    ):
        await music.execute({"action": "skip"}, context)
        result = await music.execute({"action": "previous"}, context)

        assert result.success is True


@pytest.mark.asyncio
async def test_scan_library(music, context):
    """Test scanning music library."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create fake audio files
        for i in range(3):
            file_path = os.path.join(temp_dir, f"song{i}.mp3")
            with open(file_path, "wb") as f:
                f.write(b"fake audio")

        # Scan
        result = await music.execute({"action": "library", "library_path": temp_dir}, context)

        assert result.success is True
        assert result.data["tracks_added"] == 3


@pytest.mark.asyncio
async def test_scan_nonexistent_path(music, context):
    """Test scanning nonexistent path fails."""
    result = await music.execute({"action": "library", "library_path": "/nonexistent"}, context)

    assert result.success is False
    assert "not found" in result.error.lower()


@pytest.mark.asyncio
async def test_get_status(music, context):
    """Test getting playback status."""
    result = await music.execute({"action": "status"}, context)

    assert result.success is True
    assert "state" in result.data
    assert "volume" in result.data
    assert "repeat" in result.data
    assert "shuffle" in result.data


@pytest.mark.asyncio
async def test_get_history(music, context, temp_audio_file):
    """Test getting listening history."""
    # Play a track to create history
    with patch("pygame.mixer.music.load"), patch("pygame.mixer.music.play"):
        await music.execute({"action": "play", "file_path": temp_audio_file}, context)

    # Get history
    result = await music.execute({"action": "history"}, context)

    assert result.success is True
    assert "history" in result.data
    assert isinstance(result.data["history"], list)


@pytest.mark.asyncio
async def test_multiple_users(music, context, other_context):
    """Test that users have separate playlists."""
    # User 1 creates playlist
    await music.execute(
        {"action": "playlist", "sub_action": "create", "playlist_name": "User 1"},
        context,
    )

    # User 2 creates playlist
    await music.execute(
        {
            "action": "playlist",
            "sub_action": "create",
            "playlist_name": "User 2",
        },
        other_context,
    )

    # Each user should only see their own
    user1_list = await music.execute({"action": "playlist", "sub_action": "list"}, context)
    user2_list = await music.execute({"action": "playlist", "sub_action": "list"}, other_context)

    assert user1_list.data["count"] == 1
    assert user2_list.data["count"] == 1


@pytest.mark.asyncio
async def test_permission_denied_playlist(music, context, other_context):
    """Test that users cannot modify others' playlists."""
    # User 1 creates playlist
    create_result = await music.execute(
        {"action": "playlist", "sub_action": "create", "playlist_name": "User 1"},
        context,
    )
    playlist_id = create_result.data["playlist_id"]

    # User 2 tries to delete it
    result = await music.execute(
        {"action": "playlist", "sub_action": "delete", "playlist_id": playlist_id},
        other_context,
    )

    assert result.success is False
    assert "permission" in result.error.lower()


@pytest.mark.asyncio
async def test_invalid_action(music, context):
    """Test invalid action."""
    result = await music.execute({"action": "invalid_action"}, context)

    assert result.success is False
    assert "unknown action" in result.error.lower()


@pytest.mark.asyncio
async def test_music_cleanup(music, context, temp_audio_file):
    """Test cleanup removes all data."""
    # Create some data
    with patch("pygame.mixer.music.load"), patch("pygame.mixer.music.play"):
        await music.execute({"action": "play", "file_path": temp_audio_file}, context)

    await music.execute(
        {"action": "playlist", "sub_action": "create", "playlist_name": "Test"},
        context,
    )

    # Cleanup
    with patch("pygame.mixer.music.stop"), patch("pygame.mixer.quit"):
        await music._cleanup()

    # Verify all cleared
    assert len(music._tracks) == 0
    assert len(music._playlists) == 0
    assert len(music._queue) == 0
