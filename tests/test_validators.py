"""
tests/test_input_validators.py

Unit tests for InputValidator.validate_number using CalculatorConfig constraints.

These tests cover:
- Valid number inputs: integers, decimals, strings, positive, negative, zero.
- Input trimming for string numbers.
- Invalid input handling: non-numeric strings, empty strings, whitespace, None.
- Maximum value enforcement, both positive and negative.
"""

import pytest
from decimal import Decimal
from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError
from app.input_validators import InputValidator  # adjust as per your file structure

# ----------------------------------------------------------------------
# Sample configuration
# ----------------------------------------------------------------------
# Set max input value to 1 million for testing validation limits.
# ----------------------------------------------------------------------
config = CalculatorConfig(max_input_value=Decimal('1000000'))

# ----------------------------------------------------------------------
# VALID NUMBER TESTS
# ----------------------------------------------------------------------
# Positive, negative, zero, integer, decimal, string input variants.
# ----------------------------------------------------------------------
def test_validate_number_positive_integer():
    assert InputValidator.validate_number(123, config) == Decimal('123')

def test_validate_number_positive_decimal():
    assert InputValidator.validate_number(123.456, config) == Decimal('123.456').normalize()

def test_validate_number_positive_string_integer():
    assert InputValidator.validate_number("123", config) == Decimal('123')

def test_validate_number_positive_string_decimal():
    assert InputValidator.validate_number("123.456", config) == Decimal('123.456').normalize()

def test_validate_number_negative_integer():
    assert InputValidator.validate_number(-789, config) == Decimal('-789')

def test_validate_number_negative_decimal():
    assert InputValidator.validate_number(-789.123, config) == Decimal('-789.123').normalize()

def test_validate_number_negative_string_integer():
    assert InputValidator.validate_number("-789", config) == Decimal('-789')

def test_validate_number_negative_string_decimal():
    assert InputValidator.validate_number("-789.123", config) == Decimal('-789.123').normalize()

def test_validate_number_zero():
    assert InputValidator.validate_number(0, config) == Decimal('0')

def test_validate_number_trimmed_string():
    assert InputValidator.validate_number("  456  ", config) == Decimal('456')

# ----------------------------------------------------------------------
# INVALID INPUT TESTS
# ----------------------------------------------------------------------
# Ensure proper exceptions are raised for invalid formats, excessive values,
# empty inputs, whitespace, None, and non-numeric types.
# ----------------------------------------------------------------------
def test_validate_number_invalid_string():
    with pytest.raises(ValidationError, match="Invalid number format: abc"):
        InputValidator.validate_number("abc", config)

def test_validate_number_exceeds_max_value():
    with pytest.raises(ValidationError, match="Value exceeds maximum allowed"):
        InputValidator.validate_number(Decimal('1000001'), config)

def test_validate_number_exceeds_max_value_string():
    with pytest.raises(ValidationError, match="Value exceeds maximum allowed"):
        InputValidator.validate_number("1000001", config)

def test_validate_number_exceeds_negative_max_value():
    with pytest.raises(ValidationError, match="Value exceeds maximum allowed"):
        InputValidator.validate_number(-Decimal('1000001'), config)

def test_validate_number_empty_string():
    with pytest.raises(ValidationError, match="Invalid number format: "):
        InputValidator.validate_number("", config)

def test_validate_number_whitespace_string():
    with pytest.raises(ValidationError, match="Invalid number format: "):
        InputValidator.validate_number("   ", config)

def test_validate_number_none_value():
    with pytest.raises(ValidationError, match="Invalid number format: None"):
        InputValidator.validate_number(None, config)

def test_validate_number_non_numeric_type():
    with pytest.raises(ValidationError, match="Invalid number format: "):
        InputValidator.validate_number([], config)
