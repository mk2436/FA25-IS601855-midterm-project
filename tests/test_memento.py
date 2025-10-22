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
