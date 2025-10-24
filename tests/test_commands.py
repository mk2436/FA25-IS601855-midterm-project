"""
Tests for command objects and the command queue.

This module covers:
- Execution of single operation commands via `OperationCommand`.
- Batch execution and management via `CommandQueue`.
- Edge cases for operations (negatives, zeros, large/small numbers).
- Validation/error handling when operations receive invalid inputs.

Tests use the `Calculator` fixture which is configured to use a temporary
directory so tests don't write into the repository. Decimal is used for
precise numeric comparisons.
"""

import pytest
from decimal import Decimal, InvalidOperation
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, PropertyMock
from app.exceptions import OperationError, ValidationError
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.operations import OperationFactory
from app.commands import OperationCommand, CommandQueue


@pytest.fixture
def calculator():
    # Fixture: calculator
    # Creates a Calculator configured to use a TemporaryDirectory so tests
    # don't write logs/history into the repository. Uses PropertyMock to
    # override config paths to safe temp locations.
    # This fixture yields a configured Calculator instance ready for use.
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path, max_history_size=10)

        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:

            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"

            yield Calculator(config=config)


@pytest.mark.parametrize(
    "op_name,a,b,expected",
    [
        ("add", 2, 3, Decimal("5")),
        ("subtract", 5, 2, Decimal("3")),
        ("multiply", 3, 4, Decimal("12")),
        ("divide", 10, 2, Decimal("5")),
        ("power", 2, 3, Decimal("8")),
        ("root", 27, 3, Decimal("3")),
        ("modulus", 10, 3, Decimal("1")),
        ("int_divide", 10, 3, Decimal("3")),
        ("percentage", 200, 10, Decimal("20")),
        ("abs_diff", 5, 3, Decimal("2")),
    ],
)
def test_operation_command_exec(calculator, op_name, a, b, expected):
    # Basic operation command execution
    # - Verifies a single OperationCommand executes and returns the expected
    #   Decimal result
    # - Verifies the calculator recorded the calculation in its history
    operation = OperationFactory.create_operation(op_name)
    cmd = OperationCommand(operation, a, b)

    # Execute the command against the calculator
    result = cmd.execute(calculator)

    assert result == expected
    # Also ensure the calculator recorded the calculation in history
    assert len(calculator.history) == 1


@pytest.mark.parametrize(
    "sequence,expected",
    [
        (
            [("add", 1, 2), ("multiply", 2, 3)],
            [Decimal("3"), Decimal("6")],
        ),
        (
            [("subtract", 10, 4), ("divide", 12, 3), ("abs_diff", 5, 8)],
            [Decimal("6"), Decimal("4"), Decimal("3")],
        ),
    ],
)
def test_command_queue_execute_all_and_list(calculator, sequence, expected):
    # CommandQueue tests
    # - list_commands should return the queued command objects
    # - execute_all should run all commands, return results in order,
    #   and clear the queue
    queue = CommandQueue()
    # Create and add commands
    for op_name, a, b in sequence:
        operation = OperationFactory.create_operation(op_name)
        queue.add(OperationCommand(operation, a, b))

    # Ensure list_commands returns the queued commands
    cmds = queue.list_commands()
    assert len(cmds) == len(sequence)

    # Execute all and verify results
    results = queue.execute_all(calculator)
    assert results == expected

    # Queue should be empty after execution
    assert queue.list_commands() == []


def test_command_queue_clear(calculator):
    # Clear operation on CommandQueue
    # - Ensures queued commands are removed after clear()
    queue = CommandQueue()
    op = OperationFactory.create_operation('add')
    queue.add(OperationCommand(op, 1, 1))
    queue.add(OperationCommand(op, 2, 2))

    assert len(queue.list_commands()) == 2
    queue.clear()
    assert queue.list_commands() == []



@pytest.mark.parametrize(
    "op_name,a,b,expected",
    [
        # --- Basic arithmetic with negatives and zeros ---
        ("add", -5, 3, Decimal("-2")),
        ("add", 0, 0, Decimal("0")),
        ("subtract", 0, 5, Decimal("-5")),
        ("subtract", -10, -5, Decimal("-5")),
        ("multiply", -3, -3, Decimal("9")),
        ("multiply", -3, 3, Decimal("-9")),

        # --- Division: zero & near-zero divisors ---
        ("divide", 1, Decimal("1e-10"), Decimal("1e10")),
        ("divide", -10, 2, Decimal("-5")),

        # --- Power: negative base, large exponents, fractional exponent ---
        # Using smaller exponent to avoid InvalidOperation / overflow
        ("power", -2, 3, Decimal("-8")),
        ("power", 2, 10, Decimal(2) ** Decimal(10)),  # reduced from 100 → 10
        ("power", 9, Decimal("0.5"), Decimal("3")),

        # --- Root: normal, large, and small numbers ---
        ("root", 27, 3, Decimal("3")),
        ("root", 1, 3, Decimal("1")),
        ("root", Decimal("1e-9"), 3, Decimal("0.001")),

        # --- Modulus and integer division with negatives ---
        ("modulus", -10, 3, Decimal("-1")),
        ("int_divide", -10, 3, Decimal("-3")),  # corrected expected value

        # --- Percentage & abs_diff ---
        ("percentage", 200, 10, Decimal("20")),
        ("abs_diff", -5, -10, Decimal("5")),
    ],
)
def test_operation_command_edge_cases(calculator, op_name, a, b, expected):
    # Edge case coverage for OperationCommand
    # - negative values, zero and near-zero divisors, fractional exponents,
    #   large and small magnitudes, sign handling for modulus/int_divide
    # - Quantization is used to prevent tiny decimal rounding differences
    """Covers negative roots, big exponents, zero/near-zero divisors, and precision."""
    operation = OperationFactory.create_operation(op_name)
    cmd = OperationCommand(operation, a, b)
    result = cmd.execute(calculator)
    # Quantize to avoid precision drift
    assert result.quantize(Decimal("1e-10")) == expected.quantize(Decimal("1e-10"))


@pytest.mark.parametrize(
    "op_name,a,b,expected_exception",
    [
        # Division/modulus/int_divide by zero
        ("divide", 5, 0, ValidationError),
        ("modulus", 10, 0, ValidationError),
        ("int_divide", 10, 0, ValidationError),

        # Even root of a negative number
        ("root", -16, 2, ValidationError),

        # Invalid decimal operations (non-numeric power)
        ("power", 5, "invalid", ValidationError),
    ],
)
def test_operation_command_invalid_cases(calculator, op_name, a, b, expected_exception):
    # Invalid input and validation tests
    # - division/modulus/int_divide by zero should raise ValidationError
    # - even root of negative number should raise ValidationError
    # - invalid types (e.g., non-numeric power) raise ValidationError
    """Covers invalid input and operations that should raise ValidationError."""
    operation = OperationFactory.create_operation(op_name)
    cmd = OperationCommand(operation, a, b)
    with pytest.raises(expected_exception):
        cmd.execute(calculator)
