"""
tests/test_calculator_repl.py

Unit and integration tests for the Calculator REPL (Read-Eval-Print Loop).

These tests cover:
- Basic command handling: help, exit, unknown commands, cancel.
- Arithmetic operations with valid operands.
- Undo/redo behavior, including empty history cases.
- History display, clear, save, and load functionality.
- Handling of exceptions: ValidationError, OperationError.
- Queue command functionality: add, run, show, clear, cancel, unknown operations.
- Edge cases: EOFError, empty input, mixed case commands, special characters.
- Verification that printed output matches expected messages.
"""

import pytest
from unittest.mock import patch
from app.calculator_repl import calculator_repl
from app.exceptions import ValidationError, OperationError
from app import operations  # import the operation classes


# ----------------------------------------------------------------------
# REPL BASIC COMMANDS TESTS
# ----------------------------------------------------------------------
# Tests handling of help, exit, undo/redo, save/load errors,
# unknown commands, cancel, EOFError, and empty input.
# ----

@pytest.mark.parametrize(
    "user_inputs, expected_prints",
    [
        # help command
        (["help", "exit"], ["Available commands:", "Goodbye!"]),
        (["HELP", "Exit"], ["Available commands:", "Goodbye!"]),

        # undo with nothing to undo
        (["undo", "exit"], ["Nothing to undo", "Goodbye!"]),
        # redo with nothing to redo
        (["redo", "exit"], ["Nothing to redo", "Goodbye!"]),
        # save with forced error
        (["save", "exit"], ["Error saving history", "Goodbye!"]),
        # load with forced error
        (["load", "exit"], ["Error loading history", "Goodbye!"]),
        # unknown command
        (["foobar", "exit"], ["Unknown command", "Goodbye!"]),
        # cancel operation
        (["add", "cancel", "exit"], ["Operation cancelled", "Goodbye!"]),
        # Ctrl+D / EOFError simulation
        (["EOFError"], ["Input terminated. Exiting..."]),

        # empty input
        (["", "exit"], ["Unknown command", "Goodbye!"]),
        (["    ", "exit"], ["Unknown command", "Goodbye!"]),


    ]
)
def test_calculator_repl(user_inputs, expected_prints):
    # Transform "EOFError" string to actual exception for input side_effect
    side_effects = [EOFError() if x == "EOFError" else x for x in user_inputs]

    with patch("builtins.input", side_effect=side_effects), \
         patch("builtins.print") as mock_print, \
         patch("app.calculator.Calculator.save_history") as mock_save, \
         patch("app.calculator.Calculator.load_history") as mock_load:

        # Force save/load to raise errors
        mock_save.side_effect = OperationError("Forced save error")
        mock_load.side_effect = OperationError("Forced load error")

        try:
            calculator_repl()
        except (SystemExit, EOFError):
            pass  # Ignore termination exceptions

        # Collect printed lines
        printed = [str(call.args[0]).strip() for call in mock_print.call_args_list if call.args]

        # Assert each expected print exists in output
        for expected in expected_prints:
            assert any(expected in line for line in printed), \
                f"Expected '{expected}' not found in printed lines: {printed}"




# ----------------------------------------------------------------------
# REPL HISTORY DISPLAY TESTS
# ----------------------------------------------------------------------
# Tests empty, single-entry, and multi-entry history display.
# ----------------------------------------------------------------------
@pytest.mark.parametrize(
    "user_inputs, expected_prints, history_list",
    [
        # empty history
        (["history", "exit"], ["No calculations in history", "Goodbye!"], []),
        # history with one entry
        (["history", "exit"], ["Calculation History:", "1. add(2, 3) = 5", "Goodbye!"],
         ["add(2, 3) = 5"]),
        # history with multiple entries
        (["history", "exit"], ["Calculation History:", "1. add(2, 3) = 5", "2. multiply(4, 6) = 24", "Goodbye!"],
         ["add(2, 3) = 5", "multiply(4, 6) = 24"]),
    ]
)
def test_calculator_repl_history_block(user_inputs, expected_prints, history_list):
    # Patch input and print
    with patch("builtins.input", side_effect=user_inputs), \
         patch("builtins.print") as mock_print, \
         patch("app.calculator.Calculator.show_history", return_value=history_list):

        try:
            calculator_repl()
        except (SystemExit, EOFError):
            pass

        # Capture all printed lines
        printed_lines = [str(call.args[0]).strip() for call in mock_print.call_args_list if call.args]

        # Assert each expected output is in the printed lines
        for expected in expected_prints:
            assert any(expected in line for line in printed_lines), \
                f"Expected '{expected}' not found in printed lines: {printed_lines}"


# ----------------------------------------------------------------------
# REPL HISTORY CLEAR TEST
# ----------------------------------------------------------------------
# Verify REPL clears calculation history and prints confirmation.
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "user_inputs, expected_prints",
    [
        # Clear history command
        (["clear", "exit"], ["History cleared", "Goodbye!"]),
    ]
)
def test_calculator_repl_clear_block(user_inputs, expected_prints):
    # Patch input, print, and clear_history method
    with patch("builtins.input", side_effect=user_inputs), \
         patch("builtins.print") as mock_print, \
         patch("app.calculator.Calculator.clear_history") as mock_clear:

        calculator_repl()

        # Ensure clear_history was called
        mock_clear.assert_called_once()

        # Capture all printed lines
        printed_lines = [str(call.args[0]).strip() for call in mock_print.call_args_list if call.args]

        # Assert each expected output is in the printed lines
        for expected in expected_prints:
            assert any(expected in line for line in printed_lines), \
                f"Expected '{expected}' not found in printed lines: {printed_lines}"




# ----------------------------------------------------------------------
# REPL UNDO/REDO TESTS
# ----------------------------------------------------------------------
# Verify undo/redo commands print correct messages based on availability.
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "user_inputs, undo_return, expected_prints",
    [
        # Undo with something to undo
        (["undo", "exit"], True, ["Operation undone", "Goodbye!"]),
        # Undo with nothing to undo
        (["undo", "exit"], False, ["Nothing to undo", "Goodbye!"]),
    ]
)
def test_calculator_repl_undo_block(user_inputs, undo_return, expected_prints):
    # Patch input, print, and undo method
    with patch("builtins.input", side_effect=user_inputs), \
         patch("builtins.print") as mock_print, \
         patch("app.calculator.Calculator.undo", return_value=undo_return):

        calculator_repl()

        # Capture all printed lines
        printed_lines = [str(call.args[0]).strip() for call in mock_print.call_args_list if call.args]

        # Assert expected outputs are present
        for expected in expected_prints:
            assert any(expected in line for line in printed_lines), \
                f"Expected '{expected}' not found in printed lines: {printed_lines}"


@pytest.mark.parametrize(
    "user_inputs, redo_return, expected_prints",
    [
        # Redo with something to redo
        (["redo", "exit"], True, ["Operation redone", "Goodbye!"]),
        # Redo with nothing to redo
        (["redo", "exit"], False, ["Nothing to redo", "Goodbye!"]),
    ]
)
def test_calculator_repl_redo_block(user_inputs, redo_return, expected_prints):
    # Patch input, print, and redo method
    with patch("builtins.input", side_effect=user_inputs), \
         patch("builtins.print") as mock_print, \
         patch("app.calculator.Calculator.redo", return_value=redo_return):

        calculator_repl()

        # Capture all printed lines
        printed_lines = [str(call.args[0]).strip() for call in mock_print.call_args_list if call.args]

        # Assert expected outputs are present
        for expected in expected_prints:
            assert any(expected in line for line in printed_lines), \
                f"Expected '{expected}' not found in printed lines: {printed_lines}"








# ----------------------------------------------------------------------
# REPL SAVE/LOAD HISTORY TESTS
# ----------------------------------------------------------------------
# Verify REPL prints correct success messages when save/load history.
# ----------------------------------------------------------------------


def test_calculator_repl_save_block_success():
    user_inputs = ["save", "exit"]

    # Patch input, print, and save_history
    with patch("builtins.input", side_effect=user_inputs), \
         patch("builtins.print") as mock_print, \
         patch("app.calculator.Calculator.save_history") as mock_save:

        # Ensure save_history does not raise an exception
        mock_save.return_value = None

        calculator_repl()

        # Collect printed lines
        printed_lines = [str(call.args[0]).strip() for call in mock_print.call_args_list if call.args]

        # Check that "History saved successfully" was printed
        assert any("History saved successfully" in line for line in printed_lines), \
            f"'History saved successfully' not found in printed lines: {printed_lines}"


def test_calculator_repl_load_block_success():
    user_inputs = ["load", "exit"]

    # Patch input, print, and load_history
    with patch("builtins.input", side_effect=user_inputs), \
         patch("builtins.print") as mock_print, \
         patch("app.calculator.Calculator.load_history") as mock_load:

        # Ensure load_history does not raise an exception
        mock_load.return_value = None

        calculator_repl()

        # Collect printed lines
        printed_lines = [str(call.args[0]).strip() for call in mock_print.call_args_list if call.args]

        # Check that "History loaded successfully" was printed
        assert any("History loaded successfully" in line for line in printed_lines), \
            f"'History loaded successfully' not found in printed lines: {printed_lines}"


# ----------------------------------------------------------------------
# REPL OPERATION CANCELLATION TEST
# ----------------------------------------------------------------------
# Verify REPL prints 'Operation cancelled' when user cancels input.
# ----------------------------------------------------------------------

def test_calculator_repl_cancel_second_operand():
    # Simulate user entering an operation, then first number, then 'cancel' for second number, then exit
    user_inputs = ["add", "10", "cancel", "exit"]

    with patch("builtins.input", side_effect=user_inputs), \
         patch("builtins.print") as mock_print, \
         patch("app.calculator.Calculator.set_operation") as mock_set_op, \
         patch("app.calculator.Calculator.perform_operation") as mock_perform:

        calculator_repl()

        # Collect all printed lines
        printed_lines = [str(call.args[0]).strip() for call in mock_print.call_args_list if call.args]

        # Check that "Operation cancelled" was printed
        assert any("Operation cancelled" in line for line in printed_lines), \
            f"'Operation cancelled' not found in printed lines: {printed_lines}"
        



# ----------------------------------------------------------------------
# REPL KNOWN EXCEPTIONS TEST
# ----------------------------------------------------------------------
# Verify REPL prints correct error messages for known exceptions
# such as ValidationError and OperationError.
# ----------------------------------------------------------------------



@pytest.mark.parametrize(
    "exception, expected_message",
    [
        (ValidationError("Invalid input"), "Error: Invalid input"),
        (OperationError("Operation failed"), "Error: Operation failed")
    ]
)
def test_calculator_repl_known_exceptions(exception, expected_message):
    # Simulate user entering an operation and numbers
    user_inputs = ["add", "10", "20", "exit"]

    with patch("builtins.input", side_effect=user_inputs), \
         patch("builtins.print") as mock_print, \
         patch("app.calculator.Calculator.set_operation") as mock_set_op, \
         patch("app.calculator.Calculator.perform_operation", side_effect=exception):

        calculator_repl()

        printed_lines = [str(call.args[0]).strip() for call in mock_print.call_args_list if call.args]

        # Check that the error message was printed
        assert any(expected_message in line for line in printed_lines), \
            f"Expected '{expected_message}' not found in printed lines: {printed_lines}"
        





# ----------------------------------------------------------------------
# REPL ARITHMETIC OPERATIONS TESTS
# ----------------------------------------------------------------------
# Verify valid arithmetic operations trigger correct perform_operation
# and output, and correct operation instances are passed to set_operation.
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "operation, operand1, operand2, operation_class, mock_result, expected_print",
    [
        ("add", "2", "3", operations.Addition, "Result: 5", "Result: 5"),
        ("subtract", "10", "4", operations.Subtraction, "Result: 6", "Result: 6"),
        ("multiply", "3", "5", operations.Multiplication, "Result: 15", "Result: 15"),
        ("divide", "8", "2", operations.Division, "Result: 4", "Result: 4"),
        ("modulus", "10", "3", operations.Modulus, "Result: 1", "Result: 1"),
        ("int_divide", "10", "3", operations.Int_division, "Result: 3", "Result: 3"),
        ("power", "2", "3", operations.Power, "Result: 8", "Result: 8"),
        ("root", "16", "2", operations.Root, "Result: 4", "Result: 4"),
        ("percentage", "3", "4", operations.Percentage, "Result: 0.12", "Result: 0.12"),
        ("abs_diff", "10", "4", operations.Abs_difference, "Result: 6", "Result: 6"),
    ],
)
def test_calculator_repl_operations(operation, operand1, operand2, operation_class, mock_result, expected_print):
    """
    Test that valid arithmetic operations trigger perform_operation()
    and print the correct result in the REPL.
    """
    user_inputs = [operation, operand1, operand2, "exit"]

    with patch("builtins.input", side_effect=user_inputs), \
         patch("builtins.print") as mock_print, \
         patch("app.calculator.Calculator.set_operation") as mock_set_op, \
         patch("app.calculator.Calculator.perform_operation", return_value=mock_result):

        calculator_repl()

        # Ensure set_operation() received the correct *type* of operation instance
        assert mock_set_op.call_count == 1
        op_arg = mock_set_op.call_args[0][0]
        assert isinstance(op_arg, operation_class), \
            f"Expected {operation_class.__name__}, got {type(op_arg).__name__}"

        # Verify the printed result
        printed_lines = [str(call.args[0]) for call in mock_print.call_args_list if call.args]
        assert any(expected_print in line for line in printed_lines), \
            f"Expected print '{expected_print}' not found in {printed_lines}"




# ----------------------------------------------------------------------
# REPL QUEUE COMMANDS TESTS
# ----------------------------------------------------------------------
# Thoroughly test REPL queue commands using actual operation classes.
# Covers: add, run, show, clear, cancel, unknown operation, and empty queue.
# ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "user_inputs, expected_prints",
    [
        # queue add a valid operation and run
        (["queue add", "add", "4", "7", "queue run", "exit"],
         ["Operation queued", "1. 11", "History saved successfully", "Goodbye!"]),

        # queue add multiple operations and run
        (["queue add", "add", "1", "3", "queue add", "multiply", "2", "5", "queue run", "exit"],
         ["Operation queued", "Operation queued", "1. 4", "2. 10", "History saved successfully", "Goodbye!"]),

        # queue run with empty queue
        (["queue run", "exit"],
         ["Queue is empty", "History saved successfully", "Goodbye!"]),

        # queue show with one operation
        (["queue add", "add", "9", "1", "queue show", "exit"],
         ["Operation queued", "1. Addition(9, 1)", "History saved successfully", "Goodbye!"]),

        # queue show with empty queue
        (["queue show", "exit"],
         ["Queue is empty", "History saved successfully", "Goodbye!"]),

        # queue clear with operations
        (["queue add", "add", "7", "3", "queue clear", "queue show", "exit"],
         ["Operation queued", "Queue cleared", "Queue is empty", "History saved successfully", "Goodbye!"]),

        # queue incomplete command
        (["queue", "exit"],
         ["Queue commands: add, run, show, clear", "History saved successfully", "Goodbye!"]),

        # queue clear with empty queue
        (["queue clear", "exit"],
         ["Queue cleared", "History saved successfully", "Goodbye!"]),

        # queue add cancelled at operation name
        (["queue add", "cancel", "exit"],
         ["Queue add cancelled", "Goodbye!"]),

        # queue add cancelled at first operand
        (["queue add", "add", "cancel", "exit"],
         ["Queue add cancelled", "Goodbye!"]),

        # queue add cancelled at second operand
        (["queue add", "add", "5", "cancel", "exit"],
         ["Queue add cancelled", "Goodbye!"]),

        # queue add unknown operation
        (["queue add", "foobar", "exit"],
         ["Unknown operation: foobar", "Goodbye!"]),
    ],
)
def test_calculator_repl_queue_commands_real_operations(user_inputs, expected_prints):
    """
    Thoroughly test REPL queue commands using actual operation classes.
    Covers: add, run, show, clear, cancel, unknown operation, and empty queue.
    """
    with patch("builtins.input", side_effect=user_inputs), \
         patch("builtins.print") as mock_print:

        # Patch Calculator save/load to avoid file operations
        with patch("app.calculator.Calculator.save_history"), \
             patch("app.calculator.Calculator.load_history"):

            try:
                calculator_repl()
            except (SystemExit, EOFError):
                pass

    printed_lines = [str(call.args[0]).strip() for call in mock_print.call_args_list if call.args]

    # Ensure all expected prints are in the output
    for expected in expected_prints:
        assert any(expected in line for line in printed_lines), \
            f"Expected '{expected}' not found in printed lines: {printed_lines}"

