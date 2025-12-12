"""Tests for the base ability framework."""

import asyncio
import pytest
from datetime import datetime, timedelta

from bruno_abilities.base.ability_base import (
    BaseAbility,
    AbilityResult,
    AbilityContext,
)
from bruno_abilities.base.metadata import (
    AbilityMetadata,
    ParameterMetadata,
    ParameterType,
    AbilityCapability,
)


class TestAbility(BaseAbility):
    """Test ability for unit tests."""
    
    @property
    def metadata(self) -> AbilityMetadata:
        return AbilityMetadata(
            name="test_ability",
            display_name="Test Ability",
            description="A test ability for unit testing",
            category="testing",
            parameters=[
                ParameterMetadata(
                    name="message",
                    type=str,
                    parameter_type=ParameterType.STRING,
                    description="Test message",
                    required=True,
                ),
                ParameterMetadata(
                    name="count",
                    type=int,
                    parameter_type=ParameterType.INTEGER,
                    description="Test count",
                    required=False,
                    default=1,
                ),
            ],
        )
    
    async def _execute(
        self,
        parameters: dict,
        context: AbilityContext
    ) -> AbilityResult:
        message = parameters.get("message", "")
        count = parameters.get("count", 1)
        
        return AbilityResult(
            success=True,
            data={"message": message, "count": count}
        )


@pytest.mark.asyncio
async def test_ability_initialization():
    """Test ability initialization."""
    ability = TestAbility()
    assert not ability._is_initialized
    
    await ability.initialize()
    assert ability._is_initialized
    
    # Should not re-initialize
    await ability.initialize()
    assert ability._is_initialized


@pytest.mark.asyncio
async def test_ability_cleanup():
    """Test ability cleanup."""
    ability = TestAbility()
    await ability.initialize()
    
    ability.set_state("test_key", "test_value")
    assert ability.get_state("test_key") == "test_value"
    
    await ability.cleanup()
    assert not ability._is_initialized
    assert ability.get_state("test_key") is None


@pytest.mark.asyncio
async def test_ability_execute_success():
    """Test successful ability execution."""
    ability = TestAbility()
    context = AbilityContext(user_id="user123")
    
    result = await ability.execute(
        {"message": "Hello", "count": 3},
        context
    )
    
    assert result.success
    assert result.data["message"] == "Hello"
    assert result.data["count"] == 3
    assert result.error is None


@pytest.mark.asyncio
async def test_ability_execute_with_defaults():
    """Test execution with default parameters."""
    ability = TestAbility()
    context = AbilityContext(user_id="user123")
    
    result = await ability.execute(
        {"message": "Hello"},
        context
    )
    
    assert result.success
    assert result.data["count"] == 1  # Default value


@pytest.mark.asyncio
async def test_ability_execute_missing_required():
    """Test execution with missing required parameter."""
    ability = TestAbility()
    context = AbilityContext(user_id="user123")
    
    result = await ability.execute(
        {"count": 5},  # Missing required 'message'
        context
    )
    
    assert not result.success
    assert "message" in result.error.lower()


@pytest.mark.asyncio
async def test_ability_cancellation():
    """Test ability cancellation."""
    ability = TestAbility()
    
    assert not ability.is_cancelled()
    
    await ability.cancel()
    assert ability.is_cancelled()
    
    await ability.reset_cancellation()
    assert not ability.is_cancelled()


@pytest.mark.asyncio
async def test_ability_state_management():
    """Test ability state management."""
    ability = TestAbility()
    
    # Set and get state
    ability.set_state("key1", "value1")
    ability.set_state("key2", 42)
    
    assert ability.get_state("key1") == "value1"
    assert ability.get_state("key2") == 42
    assert ability.get_state("key3", "default") == "default"
    
    # Clear state
    ability.clear_state()
    assert ability.get_state("key1") is None


@pytest.mark.asyncio
async def test_ability_health_check():
    """Test ability health check."""
    ability = TestAbility()
    
    # Should be unhealthy before initialization
    healthy = await ability.health_check()
    assert not healthy
    
    # Should be healthy after initialization
    await ability.initialize()
    healthy = await ability.health_check()
    assert healthy


def test_ability_metadata():
    """Test ability metadata."""
    ability = TestAbility()
    metadata = ability.metadata
    
    assert metadata.name == "test_ability"
    assert metadata.display_name == "Test Ability"
    assert len(metadata.parameters) == 2
    assert metadata.category == "testing"


def test_ability_metadata_function_schema():
    """Test metadata to function schema conversion."""
    ability = TestAbility()
    schema = ability.metadata.to_function_schema()
    
    assert schema["name"] == "test_ability"
    assert "description" in schema
    assert "parameters" in schema
    assert "message" in schema["parameters"]["properties"]
    assert "count" in schema["parameters"]["properties"]
    assert "message" in schema["parameters"]["required"]
    assert "count" not in schema["parameters"]["required"]


def test_ability_result():
    """Test AbilityResult model."""
    result = AbilityResult(
        success=True,
        data={"test": "data"},
        metadata={"execution_time": 1.5}
    )
    
    assert result.success
    assert result.data["test"] == "data"
    assert result.error is None
    assert result.metadata["execution_time"] == 1.5
    assert isinstance(result.timestamp, datetime)


def test_ability_context():
    """Test AbilityContext model."""
    context = AbilityContext(
        user_id="user123",
        session_id="session456",
        metadata={"source": "web"}
    )
    
    assert context.user_id == "user123"
    assert context.session_id == "session456"
    assert context.metadata["source"] == "web"
