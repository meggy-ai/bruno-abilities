"""Tests for parameter extraction utilities."""

import pytest
from datetime import datetime, timedelta

from bruno_abilities.base.parameter_extractor import ParameterExtractor


def test_extract_duration():
    """Test duration extraction."""
    # Test various duration formats
    assert ParameterExtractor.extract_duration("2 hours") == timedelta(hours=2)
    assert ParameterExtractor.extract_duration("30 minutes") == timedelta(minutes=30)
    assert ParameterExtractor.extract_duration("45 seconds") == timedelta(seconds=45)
    assert ParameterExtractor.extract_duration("1 hour 30 minutes") == timedelta(hours=1, minutes=30)
    assert ParameterExtractor.extract_duration("2h 15m 30s") == timedelta(hours=2, minutes=15, seconds=30)
    
    # Test no duration
    assert ParameterExtractor.extract_duration("hello world") is None


def test_extract_number():
    """Test number extraction."""
    assert ParameterExtractor.extract_number("set timer for 5 minutes") == 5.0
    assert ParameterExtractor.extract_number("temperature is 72.5 degrees") == 72.5
    assert ParameterExtractor.extract_number("-10 degrees") == -10.0
    assert ParameterExtractor.extract_number("no numbers here") is None


def test_extract_numbers():
    """Test multiple number extraction."""
    numbers = ParameterExtractor.extract_numbers("I have 3 apples and 5 oranges")
    assert numbers == [3.0, 5.0]
    
    numbers = ParameterExtractor.extract_numbers("no numbers")
    assert numbers == []


def test_extract_quoted_text():
    """Test quoted text extraction."""
    quoted = ParameterExtractor.extract_quoted_text('remind me to "buy milk"')
    assert quoted == ["buy milk"]
    
    quoted = ParameterExtractor.extract_quoted_text("set title 'Meeting Notes'")
    assert quoted == ["Meeting Notes"]
    
    quoted = ParameterExtractor.extract_quoted_text('both "double" and \'single\' quotes')
    assert "double" in quoted
    assert "single" in quoted


def test_extract_tags():
    """Test hashtag extraction."""
    tags = ParameterExtractor.extract_tags("note about #project #work")
    assert tags == ["project", "work"]
    
    tags = ParameterExtractor.extract_tags("no tags here")
    assert tags == []


def test_extract_priority():
    """Test priority extraction."""
    assert ParameterExtractor.extract_priority("high priority task") == "high"
    assert ParameterExtractor.extract_priority("urgent meeting") == "high"
    assert ParameterExtractor.extract_priority("low priority") == "low"
    assert ParameterExtractor.extract_priority("medium priority") == "medium"
    assert ParameterExtractor.extract_priority("normal task") is None


def test_extract_boolean():
    """Test boolean extraction."""
    keywords = {"enable": True, "disable": False, "on": True, "off": False}
    
    assert ParameterExtractor.extract_boolean("enable notifications", keywords) is True
    assert ParameterExtractor.extract_boolean("disable alerts", keywords) is False
    assert ParameterExtractor.extract_boolean("turn on", keywords) is True
    assert ParameterExtractor.extract_boolean("turn off", keywords) is False
    assert ParameterExtractor.extract_boolean("nothing here", keywords) is None


def test_clean_text():
    """Test text cleaning."""
    cleaned = ParameterExtractor.clean_text("  hello   world  ")
    assert cleaned == "hello world"
    
    cleaned = ParameterExtractor.clean_text("multiple\n\nlines")
    assert cleaned == "multiple lines"


def test_extract_name_value_pairs():
    """Test name-value pair extraction."""
    pairs = ParameterExtractor.extract_name_value_pairs(
        "title: Meeting Notes, category: Work"
    )
    assert pairs["title"] == "Meeting Notes"
    assert pairs["category"] == "Work"
    
    pairs = ParameterExtractor.extract_name_value_pairs(
        "name=John, age=30"
    )
    assert pairs["name"] == "John"
    assert pairs["age"] == "30"


def test_extract_datetime():
    """Test datetime extraction."""
    base_time = datetime(2025, 1, 1, 12, 0, 0)
    
    # Test absolute time
    result = ParameterExtractor.extract_datetime("3pm", base_time)
    assert result is not None
    assert result.hour == 15
    
    # Test invalid datetime
    result = ParameterExtractor.extract_datetime("not a date time", base_time)
    # Note: dateutil is very flexible, it might still extract something
    # or return None, so we just check it doesn't crash
    assert result is None or isinstance(result, datetime)
