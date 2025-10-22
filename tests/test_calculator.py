import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver
from app.operations import OperationFactory
from app.calculator_memento import CalculatorMemento
from app.logger import LoggingObserver


# ---------------------------
# FIXTURE: Calculator instance
# ---------------------------
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path, max_history_size=1)

        # Patch paths to redirect logs and history to temporary dirs
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            yield Calculator(config=config)


# ---------------------------
# TEST: History size limit
# ---------------------------
@pytest.mark.parametrize(
    "operations,expected_history_length",
    [
        ([(1, 2), (3, 4)], 1),  # Exceeding max history size should remove oldest entry
        ([(10, 5)], 1),         # Single operation stays in history
    ]
)
def test_history_size_limit(calculator, operations, expected_history_length):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    
    for args in operations:
        calculator.perform_operation(*args)
    
    assert len(calculator.history) == expected_history_length


# ---------------------------
# TEST: Calculator Initialization
# ---------------------------
@pytest.mark.parametrize(
    "expected_values",
    [
        ([], [], [], None),  # Default initialization state
    ]
)
def test_calculator_initialization(calculator, expected_values):
    exp_history, exp_undo, exp_redo, exp_op = expected_values
    assert calculator.history == exp_history
    assert calculator.undo_stack == exp_undo
    assert calculator.redo_stack == exp_redo
    assert calculator.operation_strategy == exp_op


# ---------------------------
# TEST: Logging Setup
# ---------------------------
@pytest.mark.parametrize(
    "log_dir,log_file",
    [
        (Path('/tmp/logs'), Path('/tmp/logs/calculator.log')),
    ]
)
@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock, log_dir, log_file):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = log_dir
        mock_log_file.return_value = log_file
        
        Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")


# ---------------------------
# TEST: Add/Remove Observers
# ---------------------------
@pytest.mark.parametrize("observer_class", [LoggingObserver, AutoSaveObserver])
def test_add_observer(calculator, observer_class):
    # AutoSaveObserver needs calculator passed in its constructor
    observer = observer_class(calculator) if observer_class is AutoSaveObserver else observer_class()
    calculator.add_observer(observer)
    assert observer in calculator.observers


@pytest.mark.parametrize("observer_class", [LoggingObserver, AutoSaveObserver])
def test_remove_observer(calculator, observer_class):
    observer = observer_class(calculator) if observer_class is AutoSaveObserver else observer_class()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers


# ---------------------------
# TEST: Setting Operations
# ---------------------------
@pytest.mark.parametrize("operation_name", ["add", "subtract", "multiply", "divide"])
def test_set_operation(calculator, operation_name):
    operation = OperationFactory.create_operation(operation_name)
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation


# ---------------------------
# TEST: Performing Operations
# ---------------------------
@pytest.mark.parametrize(
    "op_name,a,b,expected_result",
    [
        ("add", 2, 3, Decimal('5')),
        ("subtract", 5, 2, Decimal('3')),
        ("multiply", 3, 3, Decimal('9')),
        ("divide", 8, 2, Decimal('4')),
    ]
)
def test_perform_operation_success(calculator, op_name, a, b, expected_result):
    operation = OperationFactory.create_operation(op_name)
    calculator.set_operation(operation)
    result = calculator.perform_operation(a, b)
    assert result == expected_result


@pytest.mark.parametrize(
    "invalid_a,b",
    [
        ('invalid', 3),
        (None, 4),
    ]
)
def test_perform_operation_validation_error(calculator, invalid_a, b):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation(invalid_a, b)


@pytest.mark.parametrize(
    "a,b",
    [
        (2, 3),
        (5, 10),
    ]
)
def test_perform_operation_operation_error(calculator, a, b):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(a, b)


# ---------------------------
# TEST: Undo / Redo
# ---------------------------
@pytest.mark.parametrize(
    "operation_name,a,b",
    [
        ("add", 2, 3),
        ("subtract", 10, 5),
    ]
)
def test_undo(calculator, operation_name, a, b):
    operation = OperationFactory.create_operation(operation_name)
    calculator.set_operation(operation)
    calculator.perform_operation(a, b)
    calculator.undo()
    assert calculator.history == []


@pytest.mark.parametrize(
    "operation_name,a,b",
    [
        ("add", 2, 3),
        ("multiply", 3, 3),
    ]
)
def test_redo(calculator, operation_name, a, b):
    operation = OperationFactory.create_operation(operation_name)
    calculator.set_operation(operation)
    calculator.perform_operation(a, b)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1


# ---------------------------
# TEST: History Management
# ---------------------------
@patch('app.calculator.pd.DataFrame.to_csv')
@pytest.mark.parametrize(
    "a,b",
    [
        (2, 3),
        (10, 5),
    ]
)
def test_save_history(mock_to_csv, calculator, a, b):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(a, b)
    calculator.save_history()
    mock_to_csv.assert_called_once()


@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
@pytest.mark.parametrize(
    "operation_name,operand1,operand2,result",
    [
        ('Addition', '2', '3', '5'),
        ('Addition', '10', '20', '30'),
    ]
)
def test_load_history(mock_exists, mock_read_csv, calculator, operation_name, operand1, operand2, result):
    mock_read_csv.return_value = pd.DataFrame({
        'operation': [operation_name],
        'operand1': [operand1],
        'operand2': [operand2],
        'result': [result],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    try:
        calculator.load_history()
        assert len(calculator.history) == 1
        assert calculator.history[0].operation == operation_name
        assert calculator.history[0].operand1 == Decimal(operand1)
        assert calculator.history[0].operand2 == Decimal(operand2)
        assert calculator.history[0].result == Decimal(result)
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")


# ---------------------------
# TEST: Clear History
# ---------------------------
@pytest.mark.parametrize(
    "operation_name,a,b",
    [
        ("add", 2, 3),
        ("multiply", 4, 5),
    ]
)
def test_clear_history(calculator, operation_name, a, b):
    operation = OperationFactory.create_operation(operation_name)
    calculator.set_operation(operation)
    calculator.perform_operation(a, b)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call("History saved successfully.")
        mock_print.assert_any_call("Goodbye!")

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nAvailable commands:")


@pytest.mark.parametrize(
    "user_inputs,expected_output",
    [
        (['add', '2', '3', 'exit'], "\nResult: 5")
    ]
)
@patch('builtins.input')
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input, user_inputs, expected_output):
    # Feed inputs to REPL
    mock_input.side_effect = user_inputs

    # Run REPL
    calculator_repl()

    # Assert the exact output was printed
    mock_print.assert_any_call(expected_output)



# ---------------------------
# TEST: Empty History Saved
# ---------------------------
def test_save_empty_history(calculator):
    with patch('app.calculator.pd.DataFrame.to_csv') as mock_to_csv:
        calculator.save_history()
        mock_to_csv.assert_called_once()

# ---------------------------
# TEST: Empty History Loaded with logs  
# ---------------------------
def test_load_empty_history(calculator):
    with patch('app.calculator.Path.exists', return_value=False):
        calculator.load_history()
        assert calculator.history == []

def test_load_empty_history_logs(calculator):
    with patch('app.calculator.Path.exists', return_value=True), \
         patch('app.calculator.pd.read_csv', return_value=pd.DataFrame()), \
         patch('app.calculator.logging.info') as mock_logging_info:
        calculator.load_history()
        mock_logging_info.assert_called_with("Loaded empty history file")


def test_load_history_raises_operation_error(calculator):
    # Patch Path.exists to True so it tries to read the file
    with patch('app.calculator.Path.exists', return_value=True), \
         patch('app.calculator.pd.read_csv', side_effect=Exception("CSV read error")), \
         patch('app.calculator.logging.error') as mock_logging_error:
        # The load_history should raise OperationError
        with pytest.raises(OperationError) as exc_info:
            calculator.load_history()
        
        # Assert the logged error contains the expected message
        mock_logging_error.assert_called()
        logged_msg = mock_logging_error.call_args[0][0]
        assert "Failed to load history" in logged_msg
        assert "CSV read error" in logged_msg

        # Assert the raised OperationError message matches
        assert "CSV read error" in str(exc_info.value)


# ---------------------------
# TEST: Empty History Loaded as DataFrame
# ---------------------------

@pytest.mark.parametrize(
    "operations,expected_results",
    [
        # Case 1: empty history
        ([], []),

        # Case 2: single calculation
        ([('add', '2', '3')], ["5"]),

        # Case 3: multiple calculations
        ([('add', '1', '2'), ('multiply', '2', '3')], ["3", "6"]),
    ]
)
def test_get_history_dataframe(calculator, operations, expected_results):
    # Allow more history entries for this test
    calculator.config.max_history_size = 10

    # Perform operations to populate history
    for op_name, a, b in operations:
        calculator.set_operation(OperationFactory.create_operation(op_name))
        calculator.perform_operation(Decimal(a), Decimal(b))

    # Get DataFrame
    df = calculator.get_history_dataframe()

    # Assert number of rows
    assert len(df) == len(expected_results)

    # Assert results match
    for i, expected in enumerate(expected_results):
        assert df.iloc[i]['result'] == expected



@pytest.mark.parametrize(
    "operations,expected_history",
    [
        # Case 1: empty history
        ([], []),

        # Case 2: single calculation
        ([('add', '2', '3')], ["Addition(2, 3) = 5"]),

        # Case 3: multiple calculations
        ([('add', '1', '2'), ('multiply', '2', '3')],
         ["Addition(1, 2) = 3", "Multiplication(2, 3) = 6"])
    ]
)
def test_show_history(calculator, operations, expected_history):
    # Allow enough history entries
    calculator.config.max_history_size = 10

    # Perform operations to populate history
    for op_name, a, b in operations:
        calculator.set_operation(OperationFactory.create_operation(op_name))
        calculator.perform_operation(Decimal(a), Decimal(b))

    # Call show_history
    history_output = calculator.show_history()

    # Assert that output matches expected formatted strings
    assert history_output == expected_history

def test_undo(calculator):
    # Case 1: undo when nothing to undo
    assert calculator.undo() is False

    # Allow enough history entries
    calculator.config.max_history_size = 10

    # Perform two operations
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(Decimal('2'), Decimal('3'))  # result = 5
    calculator.perform_operation(Decimal('4'), Decimal('5'))  # result = 9

    # Save current history
    current_history = calculator.history.copy()

    # Push a memento for undo stack manually for testing
    calculator.undo_stack.append(CalculatorMemento(current_history[:-1]))  # simulate previous state

    # Undo the last operation
    undone = calculator.undo()
    assert undone is True

    # The history should now match the previous state
    assert calculator.history == current_history[:-1]

    # The redo stack should contain the state before undo
    assert len(calculator.redo_stack) == 1
    assert calculator.redo_stack[0].history == current_history



@pytest.mark.parametrize(
    "initial_ops,undo_indices,expected_redo_results",
    [
        # Case 1: empty redo stack
        ([], [], [False]),

        # Case 2: single redo
        ([('add', '2', '3'), ('add', '4', '5')], [1], [True]),

        # Case 3: multiple redo steps
        ([('add', '1', '2'), ('multiply', '2', '3'), ('add', '5', '5')], [2, 1], [True, True]),
    ]
)
def test_redo_parameterized(calculator, initial_ops, undo_indices, expected_redo_results):
    calculator.config.max_history_size = 10

    # Perform initial operations
    for op_name, a, b in initial_ops:
        calculator.set_operation(OperationFactory.create_operation(op_name))
        calculator.perform_operation(Decimal(a), Decimal(b))

    # Simulate undo actions by pushing mementos to redo stack
    # (simulate that these operations were undone)
    for idx in undo_indices:
        # Copy history up to the point before the "undone" operation
        memento_state = calculator.history[:idx]
        calculator.redo_stack.append(CalculatorMemento(memento_state))

    # Perform redos and check results
    for expected in expected_redo_results:
        result = calculator.redo()
        assert result is expected


@pytest.mark.parametrize(
    "history_items",
    [
        # Case 1: empty history
        [],
        # Case 2: non-empty history
        [('add', '2', '3')],
    ]
)
def test_save_history_exception_block(calculator, history_items):
    # Populate history if needed
    for op_name, a, b in history_items:
        calculator.set_operation(OperationFactory.create_operation(op_name))
        calculator.perform_operation(Decimal(a), Decimal(b))

    # Patch DataFrame.to_csv to raise Exception and logging.error to track logging
    with patch('app.calculator.pd.DataFrame.to_csv', side_effect=Exception("Disk full")), \
         patch('app.calculator.logging.error') as mock_logging_error:

        # Assert that OperationError is raised
        with pytest.raises(OperationError) as excinfo:
            calculator.save_history()

        # Assert logging.error was called with the correct message
        mock_logging_error.assert_called()
        logged_message = str(mock_logging_error.call_args[0][0])
        assert "Failed to save history: Disk full" in logged_message

        # Assert exception message matches
        assert "Failed to save history: Disk full" in str(excinfo.value)



def test_perform_operation_exception_block(calculator):
    # Create a mock operation that will raise an exception
    mock_operation = Mock()
    mock_operation.execute.side_effect = Exception("Execution failed")
    mock_operation.__str__ = Mock(return_value="MockOperation")

    # Set the mock operation as the current operation
    calculator.set_operation(mock_operation)

    # Patch logging.error to capture error logging
    with patch('app.calculator.logging.error') as mock_logging_error:
        # Call perform_operation and assert that OperationError is raised
        with pytest.raises(OperationError) as excinfo:
            calculator.perform_operation(Decimal('2'), Decimal('3'))

        # Ensure logging.error was called with the correct message
        mock_logging_error.assert_called()
        logged_message = str(mock_logging_error.call_args[0][0])
        assert "Operation failed: Execution failed" in logged_message

        # Ensure the raised OperationError contains the correct message
        assert "Operation failed: Execution failed" in str(excinfo.value)



def test_setup_logging_exception(calculator):
    # Patch os.makedirs to raise an exception
    with patch('app.calculator.os.makedirs', side_effect=Exception("Permission denied")), \
         patch('builtins.print') as mock_print:

        # Call _setup_logging and assert it raises the exception
        with pytest.raises(Exception) as excinfo:
            calculator._setup_logging()

        # Ensure print was called with the expected error message
        mock_print.assert_called()
        printed_message = str(mock_print.call_args[0][0])
        assert "Error setting up logging: Permission denied" in printed_message

        # Ensure the original exception is re-raised
        assert "Permission denied" in str(excinfo.value)


def test_calculator_init_load_history_warning():
    # Create a dummy config
    config = CalculatorConfig()

    # Patch load_history to raise an exception, triggering the except block
    with patch.object(Calculator, "load_history", side_effect=Exception("Test load failure")), \
         patch("app.calculator.logging.warning") as mock_warning:
        
        # Instantiate the calculator
        calc = Calculator(config=config)

        # Check that logging.warning was called with the correct message
        mock_warning.assert_called_once()
        warning_msg = mock_warning.call_args[0][0]
        assert "Could not load existing history: Test load failure" in warning_msg