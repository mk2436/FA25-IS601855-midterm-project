import pytest
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, PropertyMock

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.operations import OperationFactory
from app.commands import OperationCommand, CommandQueue


@pytest.fixture
def calculator():
    # Create a temporary project layout so Calculator does not write to repo dirs
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
    queue = CommandQueue()
    op = OperationFactory.create_operation('add')
    queue.add(OperationCommand(op, 1, 1))
    queue.add(OperationCommand(op, 2, 2))

    assert len(queue.list_commands()) == 2
    queue.clear()
    assert queue.list_commands() == []
