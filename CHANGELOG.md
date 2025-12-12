# Changelog

All notable changes to bruno-abilities will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete ability implementations:
  - **TimerAbility**: Countdown timers with async callbacks
  - **AlarmAbility**: Scheduled alarms with audio playback
  - **ReminderAbility**: Text-based reminders with persistence
  - **NotesAbility**: CRUD operations on notes with search
  - **TodoAbility**: Task management with priorities and status
  - **MusicAbility**: Local music playback control
- Base ability framework with abstract base class
- Rich metadata system for ability description
- Parameter validation framework with Pydantic models
- Ability registry and discovery system
- Lifecycle management for abilities
- Decorators for retry, timeout, and rate limiting
- Parameter extraction utilities for natural language
- StateManager for ability state persistence
- GitHub Actions workflows (test, lint, publish)
- Pre-commit hooks configuration
- Dependabot for automated dependency updates
- MANIFEST.in for package data
- Release automation script
- Comprehensive test suite (164 tests, 67% coverage)

## [0.1.0] - 2025-12-12

### Added
- Initial project structure
- Package configuration (pyproject.toml)
- Foundation layer implementation (Phase 1)
- Project documentation and README
- MIT License
- Implementation plan and roadmap

[Unreleased]: https://github.com/meggy-ai/bruno-abilities/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/meggy-ai/bruno-abilities/releases/tag/v0.1.0
