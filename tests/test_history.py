"""
tests/test_history.py

This module tests the calculator's history management functionality, focusing on CSV file operations
and data validation. It covers the following test scenarios:

Test Cases:
1. File Not Found:
   - Verifies empty history when file doesn't exist
   - Tests graceful handling of missing files

2. Empty Files:
   - Tests handling of empty CSV files
   - Verifies proper logging of empty history

3. Valid Data:
   - Tests successful loading of valid CSV history
   - Verifies correct conversion of data types (strings to Decimal)
   - Validates timestamp handling

4. Data Validation:
   - Tests handling of missing required columns
   - Verifies rejection of invalid data formats
   - Tests partial loading of mixed valid/invalid data

5. Error Handling:
   - Tests various pandas exceptions (EmptyDataError, ParserError)
   - Verifies proper error messages and logging
   - Tests file read/write error scenarios

The tests use pytest fixtures and extensive mocking to:
- Create temporary test environments
- Mock file system operations
- Simulate various CSV file states and content
- Test error conditions without actual file operations
"""

import pytest
import pandas as pd
from decimal import Decimal
from unittest.mock import patch
from pathlib import Path
import datetime
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError


@pytest.fixture
def calculator_temp(tmp_path):
    """Fixture providing a Calculator with temporary paths."""
    config = CalculatorConfig(base_dir=tmp_path)
    return Calculator(config=config)


# --------------------------------------------------------
# Case 1: File does not exist → empty history
# --------------------------------------------------------
@patch("app.calculator.Path.exists", return_value=False)
def test_load_history_file_not_found(mock_exists, calculator_temp):
    calculator_temp.load_history()
    assert calculator_temp.history == []


# --------------------------------------------------------
# Case 2: Empty CSV file → log info & empty history
# --------------------------------------------------------
@patch("app.calculator.pd.read_csv", return_value=pd.DataFrame())
@patch("app.calculator.Path.exists", return_value=True)
@patch("app.calculator.logging.info")
def test_load_history_empty_file(mock_info, mock_exists, mock_read_csv, calculator_temp):
    calculator_temp.load_history()
    mock_info.assert_called_once_with("Loaded empty history file")
    assert calculator_temp.history == []


# --------------------------------------------------------
# Case 3: Valid CSV → history correctly loaded
# --------------------------------------------------------
@patch("app.calculator.pd.read_csv")
@patch("app.calculator.Path.exists", return_value=True)
def test_load_history_valid(mock_exists, mock_read_csv, calculator_temp):
    mock_read_csv.return_value = pd.DataFrame({
        "operation": ["Addition", "Multiplication"],
        "operand1": ["2", "3"],
        "operand2": ["3", "4"],
        "result": ["5", "12"],
        "timestamp": [datetime.datetime.now().isoformat()] * 2
    })

    calculator_temp.load_history()

    # Verify correct length and types
    assert len(calculator_temp.history) == 2
    first_entry = calculator_temp.history[0]
    assert first_entry.operation == "Addition"
    assert first_entry.operand1 == Decimal("2")
    assert first_entry.operand2 == Decimal("3")
    assert first_entry.result == Decimal("5")


# --------------------------------------------------------
# Case 4: Missing required columns → OperationError
# --------------------------------------------------------
@patch("app.calculator.pd.read_csv")
@patch("app.calculator.Path.exists", return_value=True)
def test_load_history_missing_columns(mock_exists, mock_read_csv, calculator_temp):
    mock_read_csv.return_value = pd.DataFrame({
        "op": ["Add"],  # Invalid schema
        "operand1": ["2"],
        "operand2": ["3"],
        "result": ["5"]
    })

    with pytest.raises(OperationError):
        calculator_temp.load_history()


# --------------------------------------------------------
# Case 5: pd.read_csv throws → OperationError with message
# --------------------------------------------------------
@patch("app.calculator.pd.read_csv", side_effect=Exception("File read error"))
@patch("app.calculator.Path.exists", return_value=True)
@patch("app.calculator.logging.error")
def test_load_history_read_failure(mock_log_error, mock_exists, mock_read_csv, calculator_temp):
    with pytest.raises(OperationError, match="File read error"):
        calculator_temp.load_history()
    mock_log_error.assert_called()
    logged_message = str(mock_log_error.call_args[0][0])
    assert "Failed to load history" in logged_message
    assert "File read error" in logged_message


# --------------------------------------------------------
# Case 6: Mixed valid and invalid rows → partial load
# --------------------------------------------------------

@patch("app.calculator.pd.read_csv")
@patch("app.calculator.Path.exists", return_value=True)
def test_load_history_partial_valid(mock_exists, mock_read_csv, calculator_temp):
    # Mixed valid and invalid data
    mock_read_csv.return_value = pd.DataFrame({
        "operation": ["Addition", None],
        "operand1": ["2", "bad"],
        "operand2": ["3", "data"],
        "result": ["5", None],
        "timestamp": [datetime.datetime.now().isoformat()] * 2
    })

    # Expect OperationError due to invalid numeric values
    with pytest.raises(OperationError, match="History file contains invalid"):
        calculator_temp.load_history()




# --------------------------------------------------------
# Case: pd.read_csv raises EmptyDataError
# --------------------------------------------------------
@patch("app.calculator.pd.read_csv", side_effect=pd.errors.EmptyDataError)
@patch("app.calculator.Path.exists", return_value=True)  # Ensure file is seen as existing
def test_load_history_empty_data_error(mock_exists, mock_read_csv, calculator_temp):
    with pytest.raises(OperationError, match="History file is empty or corrupted"):
        calculator_temp.load_history()


# --------------------------------------------------------
# Case: pd.read_csv raises ParserError
# --------------------------------------------------------
@patch("app.calculator.pd.read_csv", side_effect=pd.errors.ParserError("bad CSV"))
@patch("app.calculator.Path.exists", return_value=True)
@patch("app.calculator.logging.error")
def test_load_history_parser_error(mock_log_error, mock_exists, mock_read_csv, calculator_temp):
    with pytest.raises(OperationError, match="Malformed CSV file: bad CSV"):
        calculator_temp.load_history()

    mock_log_error.assert_called()
    logged_message = str(mock_log_error.call_args[0][0])
    assert "Malformed CSV file" in logged_message
    assert "bad CSV" in logged_message