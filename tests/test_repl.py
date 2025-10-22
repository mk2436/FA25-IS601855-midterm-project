import pytest
from unittest.mock import patch
from app.calculator_repl import calculator_repl
from app.exceptions import ValidationError, OperationError

@pytest.mark.parametrize(
    "user_inputs, expected_prints",
    [
        # help command
        (["help", "exit"], ["Available commands:", "Goodbye!"]),
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