# Contributing to bruno-abilities

Thank you for your interest in contributing to bruno-abilities! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Creating New Abilities](#creating-new-abilities)
- [Documentation](#documentation)
- [Release Process](#release-process)

---

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Please be respectful, inclusive, and constructive in all interactions.

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- pip and virtualenv

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/bruno-abilities.git
cd bruno-abilities
```

3. Add the upstream repository:

```bash
git remote add upstream https://github.com/meggy-ai/bruno-abilities.git
```

---

## Development Setup

### Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate
```

### Install Dependencies

```bash
# Install package in editable mode with dev dependencies
pip install -e ".[dev,music]"

# Install pre-commit hooks
pre-commit install
```

### Verify Installation

```bash
# Run tests
pytest

# Check code quality
ruff check .
ruff format --check .

# Type check
mypy bruno_abilities
```

---

## Development Workflow

### 1. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or bug fix branch
git checkout -b fix/your-bug-fix
```

**Branch Naming Conventions**:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test improvements
- `chore/` - Maintenance tasks

### 2. Make Changes

- Write clean, well-documented code
- Follow the style guide
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bruno_abilities --cov-report=html

# Run specific test file
pytest tests/abilities/test_timer_ability.py -v

# Run only unit tests
pytest -m unit
```

### 4. Check Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy bruno_abilities

# Run all pre-commit hooks
pre-commit run --all-files
```

### 5. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new timer pause feature"
```

**Commit Message Format**:
Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add pause functionality to timer ability
fix: correct alarm time parsing for 24-hour format
docs: update README with music ability examples
test: add integration tests for notes ability
```

### 6. Push Changes

```bash
git push origin feature/your-feature-name
```

### 7. Create Pull Request

1. Go to GitHub and create a Pull Request
2. Fill out the PR template
3. Link any related issues
4. Wait for review

---

## Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use [ruff](https://github.com/astral-sh/ruff) for formatting and linting
- Maximum line length: 100 characters
- Use type hints for all functions
- Write comprehensive docstrings (Google style)

### Example

```python
from typing import Optional
from pydantic import Field

async def create_timer(
    duration_seconds: int,
    label: Optional[str] = None,
    callback: Optional[Callable] = None
) -> dict:
    """
    Create a new countdown timer.

    Args:
        duration_seconds: Timer duration in seconds (must be positive)
        label: Optional human-readable label for the timer
        callback: Optional async function to call when timer completes

    Returns:
        Dictionary containing timer_id and creation timestamp

    Raises:
        ValueError: If duration_seconds is not positive

    Example:
        >>> result = await create_timer(60, label="Tea timer")
        >>> print(result['timer_id'])
        'timer_abc123'
    """
    if duration_seconds <= 0:
        raise ValueError("Duration must be positive")

    # Implementation here
    return {"timer_id": "timer_abc123", "created_at": datetime.now()}
```

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    More detailed description if needed. Can span multiple lines
    and include additional context.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative
        TypeError: When param1 is not a string

    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
    pass
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── abilities/              # Ability-specific tests
│   ├── test_timer_ability.py
│   ├── test_alarm_ability.py
│   └── ...
├── test_ability_base.py    # Base framework tests
├── test_decorators.py      # Decorator tests
└── conftest.py             # Pytest fixtures
```

### Writing Tests

```python
import pytest
from bruno_abilities.abilities import TimerAbility
from bruno_core.models import AbilityRequest

@pytest.mark.asyncio
async def test_timer_creation():
    """Test creating a timer with valid parameters."""
    timer = TimerAbility()
    await timer.initialize()

    request = AbilityRequest(
        action="set_timer",
        parameters={"duration_seconds": 60, "label": "Test"}
    )

    response = await timer.execute(request)

    assert response.success is True
    assert "timer_id" in response.data

    await timer.shutdown()

@pytest.mark.asyncio
async def test_timer_invalid_duration():
    """Test timer creation fails with invalid duration."""
    timer = TimerAbility()
    await timer.initialize()

    request = AbilityRequest(
        action="set_timer",
        parameters={"duration_seconds": -10}
    )

    response = await timer.execute(request)

    assert response.success is False
    assert "error" in response.data

    await timer.shutdown()
```

### Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
async def test_parameter_validation():
    """Unit test for parameter validation."""
    pass

@pytest.mark.integration
async def test_ability_with_memory():
    """Integration test with memory backend."""
    pass

@pytest.mark.slow
async def test_long_running_timer():
    """Test that takes a long time to run."""
    pass
```

### Test Coverage

- Aim for 80%+ code coverage
- Test happy paths and error cases
- Test edge cases and boundary conditions
- Test async code properly with `@pytest.mark.asyncio`
- Mock external dependencies

---

## Pull Request Process

### PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guide
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated (README, docstrings, etc.)
- [ ] CHANGELOG.md updated (if applicable)
- [ ] Type hints added for all functions
- [ ] Pre-commit hooks pass
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
Describe the tests you ran and how to reproduce them:
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### Review Process

1. Automated checks must pass (CI/CD)
2. At least one approving review required
3. All conversations must be resolved
4. Branch must be up to date with main
5. Squash and merge preferred

---

## Creating New Abilities

### 1. Create Ability Class

```python
# bruno_abilities/abilities/weather_ability.py

from typing import Any, Dict
from bruno_abilities.base import BaseAbility
from bruno_core.models import AbilityMetadata, AbilityRequest, AbilityResponse

class WeatherAbility(BaseAbility):
    """Ability to fetch weather information."""

    def get_metadata(self) -> AbilityMetadata:
        return AbilityMetadata(
            name="weather",
            description="Get current weather and forecasts",
            version="1.0.0",
            author="Your Name",
            parameters=[
                {
                    "name": "location",
                    "type": "string",
                    "description": "City name or coordinates",
                    "required": True
                },
                {
                    "name": "units",
                    "type": "string",
                    "description": "Temperature units (celsius/fahrenheit)",
                    "required": False,
                    "default": "celsius"
                }
            ],
            examples=[
                "What's the weather in London?",
                "Get forecast for New York"
            ]
        )

    async def execute_action(
        self,
        request: AbilityRequest
    ) -> AbilityResponse:
        """Execute weather-related actions."""
        action = request.action
        params = request.parameters

        if action == "get_current":
            return await self._get_current_weather(params)
        elif action == "get_forecast":
            return await self._get_forecast(params)
        else:
            return AbilityResponse(
                request_id=request.id,
                ability_name="weather",
                success=False,
                data={"error": f"Unknown action: {action}"}
            )

    async def _get_current_weather(self, params: Dict[str, Any]) -> AbilityResponse:
        """Fetch current weather."""
        # Implementation here
        pass

    async def _get_forecast(self, params: Dict[str, Any]) -> AbilityResponse:
        """Fetch weather forecast."""
        # Implementation here
        pass
```

### 2. Add Tests

```python
# tests/abilities/test_weather_ability.py

import pytest
from bruno_abilities.abilities import WeatherAbility
from bruno_core.models import AbilityRequest

@pytest.mark.asyncio
async def test_weather_ability_initialization():
    """Test weather ability initializes correctly."""
    weather = WeatherAbility()
    await weather.initialize()

    metadata = weather.get_metadata()
    assert metadata.name == "weather"
    assert len(metadata.parameters) == 2

    await weather.shutdown()

@pytest.mark.asyncio
async def test_get_current_weather():
    """Test fetching current weather."""
    weather = WeatherAbility()
    await weather.initialize()

    request = AbilityRequest(
        action="get_current",
        parameters={"location": "London", "units": "celsius"}
    )

    response = await weather.execute(request)
    assert response.success is True

    await weather.shutdown()
```

### 3. Register Ability

Add to `pyproject.toml`:

```toml
[project.entry-points."bruno.abilities"]
weather = "bruno_abilities.abilities.weather_ability:WeatherAbility"
```

### 4. Add Documentation

Update README.md with:
- Ability description
- Available actions
- Example usage
- Parameter details

---

## Documentation

### Updating Documentation

- Keep README.md up to date
- Update docstrings when changing code
- Add examples for new features
- Update CHANGELOG.md for releases

### Building Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build Sphinx docs (when available)
cd docs
make html

# View documentation
open _build/html/index.html
```

---

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Creating a Release

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md with release notes
3. Run release script:

```bash
python scripts/release.py patch  # or minor, major
```

4. Review and push changes:

```bash
git push origin main
git push origin v0.1.1  # or appropriate version
```

5. Create GitHub release (triggers PyPI publish)

---

## Questions?

- **Issues**: [GitHub Issues](https://github.com/meggy-ai/bruno-abilities/issues)
- **Discussions**: [GitHub Discussions](https://github.com/meggy-ai/bruno-abilities/discussions)
- **Email**: contact@meggy-ai.com

---

Thank you for contributing to bruno-abilities! 🎉
