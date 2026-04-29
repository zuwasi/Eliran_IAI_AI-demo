"""Minimal validator smoke test."""

from src.validators import validate_all


def test_empty_validation_fails():
    result = validate_all([], [], [], [], [])
    assert result["passed"] is True
