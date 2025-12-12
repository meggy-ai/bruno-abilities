# Release Notes - bruno-abilities v0.1.0

**Release Date**: December 12, 2025
**Type**: Initial Alpha Release
**Status**: Ready for Testing and Early Adoption

---

## Overview

bruno-abilities v0.1.0 is the first alpha release of the action execution layer for Bruno Personal Assistant. This release transforms Bruno from a conversational AI into a functional personal assistant by providing 6 production-ready abilities covering time management, information storage, and entertainment.

---

## Highlights

### ✨ 6 Production-Ready Abilities

- **⏱️ Timer** - Countdown timers with callbacks and pause/resume
- **⏰ Alarm** - Scheduled alarms with audio playback and recurrence
- **🔔 Reminder** - Text-based reminders with flexible scheduling
- **📝 Notes** - Full CRUD operations with search and tags
- **✅ Todo** - Task management with priorities and due dates
- **🎵 Music** - Local music playback control

### 🏗️ Robust Foundation

- **Async-first design** for efficient concurrent operations
- **Type-safe** with Pydantic v2 validation throughout
- **Event-driven** with full bruno-core EventBus integration
- **Extensible** framework for custom ability creation
- **Well-tested** with 164 passing tests and 67% coverage

### 📦 Production-Ready Packaging

- **PyPI distribution** with automated publishing
- **Multi-OS/Python support** (Ubuntu/Windows/macOS × Python 3.10/3.11/3.12)
- **CI/CD pipeline** with automated testing and linting
- **Pre-commit hooks** for code quality enforcement
- **Dependabot** for automated dependency updates

---

## Installation

```bash
# Core installation
pip install bruno-abilities

# With music playback support
pip install bruno-abilities[music]

# Development installation
pip install bruno-abilities[dev]
```

---

## Quick Start

```python
import asyncio
from bruno_abilities.abilities import TimerAbility, NotesAbility
from bruno_core.models import AbilityRequest

async def main():
    # Create and initialize abilities
    timer = TimerAbility()
    notes = NotesAbility()

    await timer.initialize()
    await notes.initialize()

    # Set a timer
    timer_response = await timer.execute(AbilityRequest(
        action="set_timer",
        parameters={"duration_seconds": 60, "label": "Tea"}
    ))
    print(f"Timer: {timer_response.data}")

    # Create a note
    note_response = await notes.execute(AbilityRequest(
        action="create_note",
        parameters={"title": "Ideas", "content": "Brainstorm features"}
    ))
    print(f"Note: {note_response.data}")

    # Cleanup
    await timer.shutdown()
    await notes.shutdown()

asyncio.run(main())
```

---

## What's New

### Core Framework

#### BaseAbility
- Abstract base class extending bruno-core's AbilityInterface
- Built-in lifecycle management (initialize, execute, shutdown, health_check)
- Automatic parameter validation and error handling
- Support for long-running operations and cancellation

#### Parameter Extraction
- Extract parameters from natural language using patterns
- Support for dates, times, durations, and priorities
- Flexible parsing with dateparser integration
- Type coercion and validation

#### Decorators
- `@with_retry` - Automatic retry with exponential backoff
- `@with_timeout` - Timeout protection for operations
- `@rate_limit` - Rate limiting for API calls

### Abilities

#### TimerAbility
```python
# Set a 5-minute timer
await timer.execute_action("set_timer", duration_seconds=300, label="Break")

# Pause a running timer
await timer.execute_action("pause_timer", timer_id="timer_123")

# Resume a paused timer
await timer.execute_action("resume_timer", timer_id="timer_123")

# List all active timers
await timer.execute_action("list_timers")
```

#### AlarmAbility
```python
# Set a daily wake-up alarm
await alarm.execute_action(
    "set_alarm",
    time="07:00",
    label="Wake up",
    repeat_days=["monday", "tuesday", "wednesday", "thursday", "friday"]
)

# Snooze an alarm for 10 minutes
await alarm.execute_action("snooze_alarm", alarm_id="alarm_456", minutes=10)
```

#### ReminderAbility
```python
# Create a reminder
await reminder.execute_action(
    "create_reminder",
    text="Doctor appointment",
    remind_at="2025-12-15 14:00"
)

# Search reminders
await reminder.execute_action("search_reminders", query="doctor")
```

#### NotesAbility
```python
# Create a note with tags
await notes.execute_action(
    "create_note",
    title="Project Plan",
    content="Q1 objectives...",
    tags=["work", "planning"]
)

# Search notes by content
await notes.execute_action("search_notes", query="objectives")
```

#### TodoAbility
```python
# Create a high-priority task
await todo.execute_action(
    "create_task",
    title="Release v1.0",
    description="Final testing and deployment",
    priority="high",
    due_date="2025-12-20"
)

# List pending tasks
await todo.execute_action("list_tasks", status="pending")
```

#### MusicAbility
```python
# Play a track
await music.execute_action("play", track_path="/music/song.mp3")

# Set volume to 75%
await music.execute_action("set_volume", level=75)

# Get playback status
status = await music.execute_action("get_status")
```

### Integration

#### With Bruno Core
```python
from bruno_core.events import EventBus
from bruno_abilities.registry import AbilityRegistry

# Create event bus and registry
event_bus = EventBus()
registry = AbilityRegistry()

# Discover abilities
await registry.discover_abilities()

# Subscribe to ability events
event_bus.subscribe("ability.completed", lambda e: print(f"Done: {e.data}"))
```

#### With Bruno LLM
```python
from bruno_llm import LLMFactory
from bruno_abilities.base import ParameterExtractor

# Extract parameters using LLM
llm = LLMFactory.create("openai", model="gpt-4")
extractor = ParameterExtractor()

params = extractor.extract_from_text(
    "Set a timer for 5 minutes",
    expected_params=["duration", "label"]
)
```

#### With Bruno Memory
```python
from bruno_memory import MemoryFactory
from bruno_abilities.infrastructure import StateManager

# Persistent state storage
memory = MemoryFactory.create("sqlite", database="bruno.db")
state_manager = StateManager(memory_backend=memory)

# Abilities use state manager automatically
timer = TimerAbility(state_manager=state_manager)
```

---

## Technical Details

### Requirements
- Python 3.10 or higher
- bruno-core >= 0.1.0
- bruno-llm >= 0.1.0
- bruno-memory >= 0.1.0

### Test Coverage
- **164 tests passing** (0 failures)
- **67% overall coverage**
  - Timer: 87%
  - Alarm: 81%
  - Reminder: 88%
  - Notes: 90%
  - Todo: 81%
  - Music: 88%
  - Base Framework: 84-93%
  - Infrastructure: 18-26% (improvement planned)

### Code Quality
- 100% type hints coverage
- Ruff formatting and linting
- Pre-commit hooks enforced
- Mypy strict mode validation

---

## Known Issues & Limitations

1. **Infrastructure Coverage** - StateManager and registry modules need improved test coverage (planned for v0.2.0)
2. **Music Streaming** - Only local file playback supported (streaming in roadmap)
3. **Natural Language** - Basic pattern matching for parameters (LLM integration coming)
4. **Documentation** - API docs not yet on ReadTheDocs (in progress)

---

## Upgrade Notes

This is the initial release, so no upgrades from previous versions are needed.

### For New Users
1. Install: `pip install bruno-abilities`
2. Import abilities: `from bruno_abilities.abilities import TimerAbility`
3. Initialize and use

### For Bruno Ecosystem Integration
1. Abilities auto-register via entry points
2. Use with bruno-core registry for automatic discovery
3. Integrate with bruno-llm for natural language
4. Use bruno-memory for persistent state

---

## Breaking Changes

None - this is the initial release.

---

## Deprecations

None - this is the initial release.

---

## Security Updates

- Bandit security scanning integrated
- Input validation on all parameters
- No known vulnerabilities in dependencies

---

## Contributors

- Meggy AI Team

Special thanks to the Bruno community for feedback and testing!

---

## What's Next (v0.2.0 Roadmap)

- Improve infrastructure test coverage to 80%+
- Add natural language processing with LLM integration
- Music streaming support
- Additional abilities (weather, calendar, email)
- API documentation on ReadTheDocs
- Performance optimizations
- Enhanced error messages

---

## Support

- **Documentation**: [README.md](README.md) | [CONTRIBUTING.md](CONTRIBUTING.md)
- **Issues**: [GitHub Issues](https://github.com/meggy-ai/bruno-abilities/issues)
- **Discussions**: [GitHub Discussions](https://github.com/meggy-ai/bruno-abilities/discussions)
- **Email**: contact@meggy-ai.com

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Ready to get started?** Install bruno-abilities today and transform your Bruno assistant with powerful, production-ready abilities!

```bash
pip install bruno-abilities
```

For questions, feedback, or contributions, join us on [GitHub](https://github.com/meggy-ai/bruno-abilities)!
