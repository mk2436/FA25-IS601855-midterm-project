import pytest
from datetime import datetime
from app.calculator_memento import CalculatorMemento
from app.calculation import Calculation
from app.operations import OperationFactory

def test_calculator_memento_to_dict():
    # Create a sample Calculation instance
    calc = Calculation(
        operation=str(OperationFactory.create_operation('add')),
        operand1=2,
        operand2=3
    )

    # Create a memento with the calculation in history
    memento = CalculatorMemento(history=[calc])

    # Convert memento to dictionary
    memento_dict = memento.to_dict()

    # Check that 'history' is a list of dictionaries
    assert isinstance(memento_dict['history'], list)
    assert all(isinstance(item, dict) for item in memento_dict['history'])

    # Check that the calculation inside history is serialized correctly
    history_item = memento_dict['history'][0]
    assert history_item['operation'] == str(calc.operation)
    assert history_item['operand1'] == str(calc.operand1)  # compare as string
    assert history_item['operand2'] == str(calc.operand2)  # compare as string
    assert history_item['result'] == str(calc.result)      # compare as string
    assert 'timestamp' in memento_dict


def test_calculator_memento_from_dict():
    # Prepare a sample serialized calculation
    calc = Calculation(
        operation=str(OperationFactory.create_operation('add')),
        operand1=2,
        operand2=3
    )
    calc_dict = calc.to_dict()

    # Prepare a serialized memento dictionary
    timestamp = datetime.now()
    memento_dict = {
        'history': [calc_dict],
        'timestamp': timestamp.isoformat()
    }

    # Deserialize memento from dictionary
    memento = CalculatorMemento.from_dict(memento_dict)

    # Check that the history was restored correctly
    assert len(memento.history) == 1
    restored_calc = memento.history[0]
    assert restored_calc.operation == calc.operation
    assert restored_calc.operand1 == calc.operand1
    assert restored_calc.operand2 == calc.operand2
    assert restored_calc.result == calc.result

    # Check that the timestamp was restored correctly
    assert memento.timestamp == timestamp



import pytest
from datetime import datetime
from app.calculator_memento import CalculatorMemento
from app.calculation import Calculation
from app.operations import OperationFactory

# --- Existing tests remain unchanged ---


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
    Simulate undo/redo using CalculatorMemento.
    """
    # Step 1: Perform operation and create calculation
    operation = str(OperationFactory.create_operation(op_name))
    calc = Calculation(operation=operation, operand1=operand1, operand2=operand2)
    
    # Step 2: Save state in memento (before undo/redo)
    history = [calc]
    memento_before = CalculatorMemento(history=list(history))

    # Step 3: Simulate performing another operation
    new_calc = Calculation(
        operation=str(OperationFactory.create_operation("add")),
        operand1=10,
        operand2=20
    )
    history.append(new_calc)
    
    # Save state after new operation
    memento_after = CalculatorMemento(history=list(history))

    # Step 4: Undo: restore history from previous memento
    history_restored = memento_before.history
    assert len(history_restored) == 1
    restored_calc = history_restored[0]
    assert restored_calc.result == expected_result

    # Step 5: Redo: restore history from after-memento
    history_redo = memento_after.history
    assert len(history_redo) == 2
    assert history_redo[1].result == new_calc.result


@pytest.mark.parametrize(
    "custom_timestamp",
    [
        datetime(2020, 1, 1, 0, 0, 0),
        datetime(1999, 12, 31, 23, 59, 59),
        datetime.now()
    ]
)
def test_memento_with_custom_timestamp(custom_timestamp):
    memento = CalculatorMemento(history=[], timestamp=custom_timestamp)
    data = memento.to_dict()
    restored = CalculatorMemento.from_dict(data)
    assert restored.timestamp == custom_timestamp
    assert restored.history == []



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
    # Create calculation
    op = str(OperationFactory.create_operation(operation_name))
    calc = Calculation(operation=op, operand1=operand1, operand2=operand2)

    # Create memento
    memento = CalculatorMemento(history=[calc])
    data = memento.to_dict()

    # Check serialization
    assert data['history'][0]['operation'] == str(calc.operation)
    assert data['history'][0]['operand1'] == str(calc.operand1)
    assert data['history'][0]['operand2'] == str(calc.operand2)
    assert data['history'][0]['result'] == str(calc.result)
    assert 'timestamp' in data

    # Deserialize and check
    restored = CalculatorMemento.from_dict(data)
    restored_calc = restored.history[0]
    assert restored_calc.operation == calc.operation
    assert restored_calc.operand1 == calc.operand1
    assert restored_calc.operand2 == calc.operand2
    assert restored_calc.result == calc.result
    assert restored.timestamp == memento.timestamp


@pytest.mark.parametrize(
    "operations",
    [
        [("add", 1, 2), ("multiply", 3, 4)],
        [("subtract", 10, 5), ("divide", 20, 4)],
        [("add", 0, 0), ("subtract", 5, 10), ("multiply", 2, 3)],
    ]
)
def test_memento_multiple_operations(operations):
    # Create calculations
    history = [
        Calculation(
            operation=str(OperationFactory.create_operation(op_name)),
            operand1=a,
            operand2=b
        )
        for op_name, a, b in operations
    ]

    # Create memento
    memento = CalculatorMemento(history=history)
    data = memento.to_dict()

    # Check history length
    assert len(data['history']) == len(operations)

    # Deserialize and check all operations
    restored = CalculatorMemento.from_dict(data)
    assert len(restored.history) == len(operations)
    for original, restored_calc in zip(history, restored.history):
        assert restored_calc.operation == original.operation
        assert restored_calc.operand1 == original.operand1
        assert restored_calc.operand2 == original.operand2
        assert restored_calc.result == original.result




# ---------------------------
# Edge-case
# ---------------------------

@pytest.mark.parametrize(
    "history_ops",
    [
        [],  # Empty history
        [None],  # None in history
        [
            Calculation(
                operation=str(OperationFactory.create_operation("add")),
                operand1=1,
                operand2=2
            )
        ] * 50  # Large history (50 repeated calculations)
    ]
)
def test_memento_edge_cases_history(history_ops):
    memento = CalculatorMemento(history=history_ops)
    
    if history_ops == [None]:
        # Expect AttributeError when serializing a None calculation
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
    memento = CalculatorMemento(history=[], timestamp=custom_timestamp)
    data = memento.to_dict()
    restored = CalculatorMemento.from_dict(data)
    assert restored.timestamp == custom_timestamp
    assert restored.history == []