########################
# Exception Hierarchy  #
########################

"""
This module defines the exception hierarchy for the calculator application,
providing structured error handling across all components.

Key Features:
1. Base Exception:
   - CalculatorError serves as the root for all calculator-specific errors
   - Enables unified exception handling for the entire application

2. Validation Errors:
   - ValidationError is raised when user input is invalid
   - Handles non-numeric values, out-of-range inputs, and other validation failures

3. Operation Errors:
   - OperationError is raised when a calculation operation fails
   - Covers arithmetic errors such as division by zero and invalid operations

4. Configuration Errors:
   - ConfigurationError is raised when calculator settings are invalid
   - Handles issues like improper directory paths, invalid configuration values, or missing settings

5. Integration & Extensibility:
   - Provides a clear hierarchy for catching and distinguishing error types
   - Designed to support maintainable and scalable error handling across modules
"""

class CalculatorError(Exception):
    """
    Base exception class for calculator-specific errors.

    All custom exceptions for the calculator application inherit from this class,
    allowing for unified error handling.
    """
    pass


class ValidationError(CalculatorError):
    """
    Raised when input validation fails.

    This exception is triggered when user inputs do not meet the required criteria,
    such as entering non-numeric values or exceeding maximum allowed values.
    """
    pass


class OperationError(CalculatorError):
    """
    Raised when a calculation operation fails.

    This exception is used to indicate failures during the execution of arithmetic
    operations, such as division by zero or invalid operations.
    """
    pass


class ConfigurationError(CalculatorError):
    """
    Raised when calculator configuration is invalid.

    Triggered when there are issues with the calculator's configuration settings,
    such as invalid directory paths or improper configuration values.
    """
    pass
