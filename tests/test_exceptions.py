"""
tests/test_exceptions.py

Unit tests for the custom exception hierarchy in the calculator application.

These tests verify:
- Each custom exception class can be raised and caught as expected.
- Subclasses of CalculatorError (ValidationError, OperationError, ConfigurationError)
  properly inherit from the base class.
- Exception messages are preserved and displayed correctly.
"""

import pytest
from app.exceptions import CalculatorError, ValidationError, OperationError, ConfigurationError
import builtins

# ----------------------------------------------------------------------
# TEST: CalculatorError base class
# ----------------------------------------------------------------------
# Ensures CalculatorError serves as the root exception type for the application.
# ----------------------------------------------------------------------
def test_calculator_error_is_base_exception():
    with pytest.raises(CalculatorError) as exc_info:
        raise CalculatorError("Base calculator error occurred")
    assert str(exc_info.value) == "Base calculator error occurred"


# ----------------------------------------------------------------------
# TEST: ValidationError inheritance and message
# ----------------------------------------------------------------------
# Confirms that ValidationError inherits from CalculatorError and that its
# message is properly propagated when raised.
# ----------------------------------------------------------------------
def test_validation_error_is_calculator_error():
    with pytest.raises(CalculatorError) as exc_info:
        raise ValidationError("Validation failed")
    assert isinstance(exc_info.value, CalculatorError)
    assert str(exc_info.value) == "Validation failed"


def test_validation_error_specific_exception():
    with pytest.raises(ValidationError) as exc_info:
        raise ValidationError("Validation error")
    assert str(exc_info.value) == "Validation error"


# ----------------------------------------------------------------------
# TEST: OperationError inheritance and message
# ----------------------------------------------------------------------
# Validates that OperationError is correctly derived from CalculatorError
# and that its message is displayed properly.
# ----------------------------------------------------------------------
def test_operation_error_is_calculator_error():
    with pytest.raises(CalculatorError) as exc_info:
        raise OperationError("Operation failed")
    assert isinstance(exc_info.value, CalculatorError)
    assert str(exc_info.value) == "Operation failed"


def test_operation_error_specific_exception():
    with pytest.raises(OperationError) as exc_info:
        raise OperationError("Specific operation error")
    assert str(exc_info.value) == "Specific operation error"


# ----------------------------------------------------------------------
# TEST: ConfigurationError inheritance and message
# ----------------------------------------------------------------------
# Verifies that ConfigurationError inherits from CalculatorError and
# maintains its message when raised.
# ----------------------------------------------------------------------
def test_configuration_error_is_calculator_error():
    with pytest.raises(CalculatorError) as exc_info:
        raise ConfigurationError("Configuration invalid")
    assert isinstance(exc_info.value, CalculatorError)
    assert str(exc_info.value) == "Configuration invalid"


def test_configuration_error_specific_exception():
    with pytest.raises(ConfigurationError) as exc_info:
        raise ConfigurationError("Specific configuration error")
    assert str(exc_info.value) == "Specific configuration error"


# ----------------------------------------------------------------------
# TEST: Edge cases for exception hierarchy and message preservation
# ----------------------------------------------------------------------
# Ensures that all CalculatorError subclasses behave consistently when:
# - Raised with empty or unusual messages
# - Chained from other exceptions
# - Instantiated without explicit messages
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "exception_class,message",
    [
        (ValidationError, ""),  # Empty message
        (ValidationError, " "),  # Whitespace only
        (OperationError, None),  # No message
        (ConfigurationError, "Unexpected symbol in config!"),  # Special characters
    ],
)
def test_exception_message_preservation(exception_class, message):
    """Verify exceptions preserve provided messages, even if empty or None."""
    exc = exception_class(message)
    if message is None:
        # Default str() for Exception(None) is 'None'
        assert str(exc) == "None"
    else:
        assert str(exc) == message


@pytest.mark.parametrize(
    "exception_class",
    [ValidationError, OperationError, ConfigurationError],
)
def test_exception_chaining(exception_class):
    """Verify exception chaining (from another exception) works as expected."""
    original = builtins.ValueError("Underlying error")
    with pytest.raises(exception_class) as exc_info:
        try:
            raise original
        except builtins.ValueError as e:
            raise exception_class("Wrapped error") from e
    assert isinstance(exc_info.value.__cause__, builtins.ValueError)
    assert str(exc_info.value.__cause__) == "Underlying error"
    assert str(exc_info.value) == "Wrapped error"
