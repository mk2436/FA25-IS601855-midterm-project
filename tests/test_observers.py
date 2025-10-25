
"""
tests/test_observers.py

This module contains unit tests for the Observer pattern implementation in the calculator application.
It tests two main observer classes:

1. LoggingObserver:
   - Tests logging of calculation operations
   - Verifies correct log message formatting
   - Includes parameterized tests for various calculation scenarios
   - Tests error handling for invalid inputs

2. AutoSaveObserver:
   - Tests automatic saving of calculator history
   - Verifies configuration-based auto-save behavior
   - Tests error handling during save operations
   - Includes parameterized tests for different auto-save scenarios

The tests use pytest fixtures and mocking extensively to:
- Mock calculator and calculation objects
- Patch logging functionality
- Test both success and failure scenarios
- Validate observer pattern implementation
- Verify error handling and edge cases

Each section is clearly marked with headers and includes both positive and negative test cases.
"""

import pytest
from unittest.mock import Mock, patch
from app.calculation import Calculation
from app.history import AutoSaveObserver
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.logger import LoggingObserver 

# Sample setup for mock calculation
calculation_mock = Mock(spec=Calculation)
calculation_mock.operation = "addition"
calculation_mock.operand1 = 5
calculation_mock.operand2 = 3
calculation_mock.result = 8

# -----------------------
# LoggingObserver Tests
# -----------------------

@patch('logging.info')
def test_logging_observer_logs_calculation(logging_info_mock):
    observer = LoggingObserver()
    observer.update(calculation_mock)
    logging_info_mock.assert_called_once_with(
        "Calculation performed: addition (5, 3) = 8"
    )

def test_logging_observer_no_calculation():
    observer = LoggingObserver()
    with pytest.raises(AttributeError):
        observer.update(None)  # Passing None should raise an exception as there's no calculation



@pytest.mark.parametrize(
    "operation, operand1, operand2, result, expected_log",
    [
        ("add", 1, 2, 3, "Calculation performed: add (1, 2) = 3"),
        ("sub", 5, 3, 2, "Calculation performed: sub (5, 3) = 2"),
        ("mul", None, 5, None, "Calculation performed: mul (None, 5) = None"),
        ("", 0, 0, 0, "Calculation performed:  (0, 0) = 0"),
        ("@#$%", -1, 1, 0, "Calculation performed: @#$% (-1, 1) = 0"),
    ]
)
def test_logging_observer_parameterized(operation, operand1, operand2, result, expected_log):
    calc_mock = Mock(spec=Calculation)
    calc_mock.operation = operation
    calc_mock.operand1 = operand1
    calc_mock.operand2 = operand2
    calc_mock.result = result

    observer = LoggingObserver()
    with patch("logging.info") as logging_info_mock:
        observer.update(calc_mock)
        logging_info_mock.assert_called_once_with(expected_log)


# -----------------------
# AutoSaveObserver Tests
# -----------------------


def test_autosave_observer_triggers_save():
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = True
    observer = AutoSaveObserver(calculator_mock)
    
    observer.update(calculation_mock)
    calculator_mock.save_history.assert_called_once()

@patch('logging.info')
def test_autosave_observer_logs_autosave(logging_info_mock):
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = True
    observer = AutoSaveObserver(calculator_mock)
    
    observer.update(calculation_mock)
    logging_info_mock.assert_called_once_with("History auto-saved")

def test_autosave_observer_does_not_trigger_save_when_disabled():
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = False
    observer = AutoSaveObserver(calculator_mock)
    
    observer.update(calculation_mock)
    calculator_mock.save_history.assert_not_called()

@pytest.mark.parametrize(
    "auto_save_enabled, save_side_effect, expected_calls, log_expected",
    [
        (True, None, 1, "History auto-saved"),  # Normal auto-save
        (True, Exception("Save failed"), 1, None),  # Exception during save
        (False, None, 0, None),  # Auto-save disabled
    ]
)
def test_autosave_observer_parameterized(auto_save_enabled, save_side_effect, expected_calls, log_expected):
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = auto_save_enabled
    calculator_mock.save_history.side_effect = save_side_effect

    observer = AutoSaveObserver(calculator_mock)

    with patch("logging.info") as logging_info_mock:
        if save_side_effect:
            with pytest.raises(Exception, match="Save failed"):
                observer.update(Mock(spec=Calculation))
        else:
            observer.update(Mock(spec=Calculation))

        assert calculator_mock.save_history.call_count == expected_calls
        if log_expected:
            logging_info_mock.assert_called_once_with(log_expected)
        else:
            logging_info_mock.assert_not_called()


# -----------------------
# Invalid constructor / update tests
# -----------------------


@pytest.mark.parametrize(
    "observer_class, init_arg, update_arg, expected_exception",
    [
        (AutoSaveObserver, None, Mock(), TypeError),  # Passing None -> TypeError
        (LoggingObserver, None, None, TypeError),  # LoggingObserver() cannot take arguments
    ]
)
def test_observer_invalid_cases(observer_class, init_arg, update_arg, expected_exception):
    if init_arg is None:
        with pytest.raises(expected_exception):
            observer_class(init_arg)
    else:
        observer = observer_class(init_arg)
        with pytest.raises(expected_exception):
            observer.update(update_arg)



# Additional negative test cases for AutoSaveObserver

def test_autosave_observer_invalid_calculator():
    with pytest.raises(TypeError):
        AutoSaveObserver(None)  # Passing None should raise a TypeError

def test_autosave_observer_no_calculation():
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = True
    observer = AutoSaveObserver(calculator_mock)
    
    with pytest.raises(AttributeError):
        observer.update(None)  # Passing None should raise an exception
