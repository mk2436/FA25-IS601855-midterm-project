"""
tests/test_calculator_memento.py

Unit tests for the CalculatorMemento class and its integration with Calculation and OperationFactory.

These tests cover:
- Serialization and deserialization of CalculatorMemento objects.
- Correct preservation of Calculation history and timestamps.
- Simulation of undo/redo behavior using mementos.
- Handling of single and multiple operations.
- Edge cases including empty history, None values, large history, and invalid timestamps.

The tests use pytest parametrize to cover multiple scenarios efficiently.
"""

import pytest
from datetime import datetime
from app.calculator_memento import CalculatorMemento
from app.calculation import Calculation
from app.operations import OperationFactory


# ---------------------------
# Basic Serialization Tests
# ---------------------------

def test_calculator_memento_to_dict():
    """
    Test that a CalculatorMemento object can be correctly serialized to a dictionary.
    Ensures that:
    - history is a list of dictionaries
    - calculation fields are serialized as strings
    - timestamp field exists
    """
    calc = Calculation(
        operation=str(OperationFactory.create_operation('add')),
        operand1=2,
        operand2=3
    )
    memento = CalculatorMemento(history=[calc])
    memento_dict = memento.to_dict()

    assert isinstance(memento_dict['history'], list)
    assert all(isinstance(item, dict) for item in memento_dict['history'])

    history_item = memento_dict['history'][0]
    assert history_item['operation'] == str(calc.operation)
    assert history_item['operand1'] == str(calc.operand1)
    assert history_item['operand2'] == str(calc.operand2)
    assert history_item['result'] == str(calc.result)
    assert 'timestamp' in memento_dict


def test_calculator_memento_from_dict():
    """
    Test deserialization of a CalculatorMemento from a dictionary.
    Verifies:
    - history is restored correctly
    - individual Calculation objects maintain their data
    - timestamp is correctly restored
    """
    calc = Calculation(
        operation=str(OperationFactory.create_operation('add')),
        operand1=2,
        operand2=3
    )
    calc_dict = calc.to_dict()
    timestamp = datetime.now()
    memento_dict = {
        'history': [calc_dict],
        'timestamp': timestamp.isoformat()
    }

    memento = CalculatorMemento.from_dict(memento_dict)
    assert len(memento.history) == 1
    restored_calc = memento.history[0]
    assert restored_calc.operation == calc.operation
    assert restored_calc.operand1 == calc.operand1
    assert restored_calc.operand2 == calc.operand2
    assert restored_calc.result == calc.result
    assert memento.timestamp == timestamp


# ---------------------------
# Undo/Redo Simulation Tests
# ---------------------------

@pytest.mark.parametrize(
    "op_name, operand1, operand2, expected_result",
    [
        ("add", 2, 3, 5),
        ("subtract", 5, 2, 3),
        ("multiply", 4, 3, 12),
        ("divide", 10, 2, 5),
    ]
)
def test_undo_redo_simulation(op_name, operand1, operand2, expected_result):
    """
    Simulate undo and redo using CalculatorMemento objects.
    Steps:
    1. Perform an operation and save initial state
    2. Perform a second operation and save updated state
    3. Undo by restoring previous memento
    4. Redo by restoring after-memento
    """
    operation = str(OperationFactory.create_operation(op_name))
    calc = Calculation(operation=operation, operand1=operand1, operand2=operand2)
    
    history = [calc]
    memento_before = CalculatorMemento(history=list(history))

    new_calc = Calculation(
        operation=str(OperationFactory.create_operation("add")),
        operand1=10,
        operand2=20
    )
    history.append(new_calc)
    memento_after = CalculatorMemento(history=list(history))

    # Undo check
    history_restored = memento_before.history
    assert len(history_restored) == 1
    restored_calc = history_restored[0]
    assert restored_calc.result == expected_result

    # Redo check
    history_redo = memento_after.history
    assert len(history_redo) == 2
    assert history_redo[1].result == new_calc.result


# ---------------------------
# Timestamp Handling Tests
# ---------------------------

@pytest.mark.parametrize(
    "custom_timestamp",
    [
        datetime(2020, 1, 1, 0, 0, 0),
        datetime(1999, 12, 31, 23, 59, 59),
        datetime.now()
    ]
)
def test_memento_with_custom_timestamp(custom_timestamp):
    """
    Ensure CalculatorMemento can handle custom timestamps correctly.
    """
    memento = CalculatorMemento(history=[], timestamp=custom_timestamp)
    data = memento.to_dict()
    restored = CalculatorMemento.from_dict(data)
    assert restored.timestamp == custom_timestamp
    assert restored.history == []


# ---------------------------
# Single Operation Serialization
# ---------------------------

@pytest.mark.parametrize(
    "operation_name,operand1,operand2",
    [
        ("add", 2, 3),
        ("subtract", 10, 5),
        ("multiply", 4, 5),
        ("divide", 20, 4),
    ]
)
def test_memento_single_operation_serialization(operation_name, operand1, operand2):
    """
    Test serialization and deserialization of a memento with a single calculation.
    Ensures fields are correctly preserved in both directions.
    """
    op = str(OperationFactory.create_operation(operation_name))
    calc = Calculation(operation=op, operand1=operand1, operand2=operand2)
    memento = CalculatorMemento(history=[calc])
    data = memento.to_dict()

    # Verify serialization
    assert data['history'][0]['operation'] == str(calc.operation)
    assert data['history'][0]['operand1'] == str(calc.operand1)
    assert data['history'][0]['operand2'] == str(calc.operand2)
    assert data['history'][0]['result'] == str(calc.result)
    assert 'timestamp' in data

    # Verify deserialization
    restored = CalculatorMemento.from_dict(data)
    restored_calc = restored.history[0]
    assert restored_calc.operation == calc.operation
    assert restored_calc.operand1 == calc.operand1
    assert restored_calc.operand2 == calc.operand2
    assert restored_calc.result == calc.result
    assert restored.timestamp == memento.timestamp


# ---------------------------
# Multiple Operations Tests
# ---------------------------

@pytest.mark.parametrize(
    "operations",
    [
        [("add", 1, 2), ("multiply", 3, 4)],
        [("subtract", 10, 5), ("divide", 20, 4)],
        [("add", 0, 0), ("subtract", 5, 10), ("multiply", 2, 3)],
    ]
)
def test_memento_multiple_operations(operations):
    """
    Test memento serialization/deserialization for multiple calculations in history.
    """
    history = [
        Calculation(
            operation=str(OperationFactory.create_operation(op_name)),
            operand1=a,
            operand2=b
        )
        for op_name, a, b in operations
    ]
    memento = CalculatorMemento(history=history)
    data = memento.to_dict()

    assert len(data['history']) == len(operations)

    restored = CalculatorMemento.from_dict(data)
    assert len(restored.history) == len(operations)
    for original, restored_calc in zip(history, restored.history):
        assert restored_calc.operation == original.operation
        assert restored_calc.operand1 == original.operand1
        assert restored_calc.operand2 == original.operand2
        assert restored_calc.result == original.result


# ---------------------------
# Edge Case Tests
# ---------------------------

@pytest.mark.parametrize(
    "history_ops",
    [
        [],  # Empty history
        [None],  # History containing None
        [
            Calculation(
                operation=str(OperationFactory.create_operation("add")),
                operand1=1,
                operand2=2
            )
        ] * 50  # Large history
    ]
)
def test_memento_edge_cases_history(history_ops):
    """
    Test how memento handles edge cases in history:
    - empty list
    - None entries (should raise)
    - large histories
    """
    memento = CalculatorMemento(history=history_ops)
    
    if history_ops == [None]:
        with pytest.raises(AttributeError):
            memento.to_dict()
    else:
        data = memento.to_dict()
        restored = CalculatorMemento.from_dict(data)
        assert restored.history == history_ops


@pytest.mark.parametrize(
    "timestamp_str, should_raise",
    [
        ("2020-01-01T12:00:00", False),  # valid ISO timestamp
        ("not-a-timestamp", True),       # invalid timestamp
        ("", True),                       # empty string
        (None, True),                     # None value
    ]
)
def test_memento_edge_cases_timestamp(timestamp_str, should_raise):
    """
    Test deserialization behavior with various timestamp edge cases.
    Ensures exceptions are raised for invalid timestamp values.
    """
    if should_raise:
        with pytest.raises((ValueError, TypeError)):
            CalculatorMemento.from_dict({'history': [], 'timestamp': timestamp_str})
    else:
        memento = CalculatorMemento.from_dict({'history': [], 'timestamp': timestamp_str})
        assert isinstance(memento.timestamp, datetime)
        assert memento.history == []


@pytest.mark.parametrize(
    "custom_timestamp",
    [
        datetime(1999, 12, 31, 23, 59, 59),
        datetime(2025, 10, 24, 15, 0, 0),
        datetime.now()
    ]
)
def test_memento_custom_timestamps(custom_timestamp):
    """
    Verify that CalculatorMemento correctly handles various custom timestamp values.
    """
    memento = CalculatorMemento(history=[], timestamp=custom_timestamp)
    data = memento.to_dict()
    restored = CalculatorMemento.from_dict(data)
    assert restored.timestamp == custom_timestamp
    assert restored.history == []
