########################
# Calculator REPL       #
########################

from decimal import Decimal
import logging

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver
from app.logger import LoggingObserver
from app.operations import OperationFactory
from app.ui_color_factory import ColorFormatterFactory


def calculator_repl():
    """
    Command-line interface for the calculator.

    Implements a Read-Eval-Print Loop (REPL) that continuously prompts the user
    for commands, processes arithmetic operations, and manages calculation history.
    """
    try:
        # Initialize the Calculator instance
        calc = Calculator()

        # Register observers for logging and auto-saving history
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))

        # Initialise Color Formatter Instances
        success_formatter = ColorFormatterFactory.get_formatter("success")
        error_formatter = ColorFormatterFactory.get_formatter("error")
        info_formatter = ColorFormatterFactory.get_formatter("info")
        result_formatter = ColorFormatterFactory.get_formatter("result")
        warning_formatter = ColorFormatterFactory.get_formatter("warning")
        prompt_formatter = ColorFormatterFactory.get_formatter("prompt")

        print(info_formatter.format("Calculator started. Type 'help' for commands."))

        while True:
            try:
                # Prompt the user for a command
                command = input(prompt_formatter.format("\nEnter command: ")).lower().strip()

                if command == 'help':
                    # Display available commands
                    print(info_formatter.format("\nAvailable commands:"))
                    print(info_formatter.format("  add, subtract, multiply, divide, power, root, modulus, int_divide, percentage, abs_diff - Perform calculations"))
                    print(info_formatter.format("  history - Show calculation history"))
                    print(info_formatter.format("  clear - Clear calculation history"))
                    print(info_formatter.format("  undo - Undo the last calculation"))
                    print(info_formatter.format("  redo - Redo the last undone calculation"))
                    print(info_formatter.format("  save - Save calculation history to file"))
                    print(info_formatter.format("  load - Load calculation history from file"))
                    print(info_formatter.format("  exit - Exit the calculator"))
                    continue

                if command == 'exit':
                    # Attempt to save history before exiting
                    try:
                        calc.save_history()
                        print(success_formatter.format("History saved successfully."))
                    except Exception as e:
                        print(error_formatter.format(f"Warning: Could not save history: {e}"))
                    print(info_formatter.format("Goodbye!"))
                    break

                if command == 'history':
                    # Display calculation history
                    history = calc.show_history()
                    if not history:
                        print(info_formatter.format("No calculations in history"))
                    else:
                        print(info_formatter.format("\nCalculation History:"))
                        for i, entry in enumerate(history, 1):
                            print(info_formatter.format(f"{i}. {entry}"))
                    continue

                if command == 'clear':
                    # Clear calculation history
                    calc.clear_history()
                    print(success_formatter.format("History cleared"))
                    continue

                if command == 'undo':
                    # Undo the last calculation
                    if calc.undo():
                        print(success_formatter.format("Operation undone"))
                    else:
                        print(warning_formatter.format("Nothing to undo"))
                    continue

                if command == 'redo':
                    # Redo the last undone calculation
                    if calc.redo():
                        print(success_formatter.format("Operation redone"))
                    else:
                        print(warning_formatter.format("Nothing to redo"))
                    continue

                if command == 'save':
                    # Save calculation history to file
                    try:
                        calc.save_history()
                        print(success_formatter.format("History saved successfully"))
                    except Exception as e:
                        print(error_formatter.format(f"Error saving history: {e}"))
                    continue

                if command == 'load':
                    # Load calculation history from file
                    try:
                        calc.load_history()
                        print(success_formatter.format("History loaded successfully"))
                    except Exception as e:
                        print(error_formatter.format(f"Error loading history: {e}"))    
                    continue

                if command in ['add', 'subtract', 'multiply', 'divide', 'power', 'root', 'modulus', 'int_divide', 'percentage', 'abs_diff']:
                    # Perform the specified arithmetic operation
                    try:
                        print(prompt_formatter.format("\nEnter numbers (or 'cancel' to abort):"))
                        a = input(prompt_formatter.format("First number: "))
                        if a.lower() == 'cancel':
                            print(info_formatter.format("Operation cancelled"))
                            continue
                        b = input(prompt_formatter.format("Second number: "))
                        if b.lower() == 'cancel':
                            print(info_formatter.format("Operation cancelled"))
                            continue

                        # Create the appropriate operation instance using the Factory pattern
                        operation = OperationFactory.create_operation(command)
                        calc.set_operation(operation)

                        # Perform the calculation
                        result = calc.perform_operation(a, b)

                        # Normalize the result if it's a Decimal
                        if isinstance(result, Decimal):
                            result = result.normalize()

                        print(result_formatter.format(f"\nResult: {result}"))
                    except (ValidationError, OperationError) as e:
                        # Handle known exceptions related to validation or operation errors
                        print(error_formatter.format(f"Error: {e}"))
                    except Exception as e: # pragma: no cover
                        # Handle any unexpected exceptions
                        print(error_formatter.format(f"Unexpected error: {e}")) # pragma: no cover
                    continue

                # Handle unknown commands
                print(warning_formatter.format(f"Unknown command: '{command}'. Type 'help' for available commands."))
            except KeyboardInterrupt:
                # Handle Ctrl+C interruption gracefully
                print(error_formatter.format("\nOperation cancelled")) # pragma: no cover
                continue # pragma: no cover
            except EOFError:
                # Handle end-of-file (e.g., Ctrl+D) gracefully
                print(error_formatter.format("\nInput terminated. Exiting..."))
                break
            except Exception as e: # pragma: no cover
                # Handle any other unexpected exceptions
                print(error_formatter.format(f"Error: {e}")) # pragma: no cover
                continue # pragma: no cover

    except Exception as e: # pragma: no cover
        # Handle fatal errors during initialization
        print(error_formatter.format(f"Fatal error: {e}")) # pragma: no cover
        logging.error(f"Fatal error in calculator REPL: {e}") # pragma: no cover
        raise
