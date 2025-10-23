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
from app.ui_color import ColorFormatter


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
        formatter = ColorFormatter()

        print(formatter.success("Calculator started. Type 'help' for commands."))

        while True:
            try:
                # Prompt the user for a command
                command = input(formatter.prompt("\nEnter command: ")).lower().strip()

                if command == 'help':
                    # Display available commands
                    from app.help_menu import build_help_menu

                    help_text = build_help_menu()
                    # Use the project's ColorFormatter for consistent styling
                    print(formatter.info(f"\n{help_text}"))

                if command == 'exit':
                    # Attempt to save history before exiting
                    try:
                        calc.save_history()
                        print(formatter.success("History saved successfully."))
                    except Exception as e:
                        print(formatter.error(f"Warning: Could not save history: {e}"))
                    print(formatter.info("Goodbye!"))
                    break

                if command == 'history':
                    # Display calculation history
                    history = calc.show_history()
                    if not history:
                        print(formatter.info("No calculations in history"))
                    else:
                        print(formatter.info("\nCalculation History:"))
                        for i, entry in enumerate(history, 1):
                            print(formatter.info(f"{i}. {entry}"))
                    continue

                if command == 'clear':
                    # Clear calculation history
                    calc.clear_history()
                    print(formatter.success("History cleared"))
                    continue

                if command == 'undo':
                    # Undo the last calculation
                    if calc.undo():
                        print(formatter.success("Operation undone"))
                    else:
                        print(formatter.warning("Nothing to undo"))
                    continue

                if command == 'redo':
                    # Redo the last undone calculation
                    if calc.redo():
                        print(formatter.success("Operation redone"))
                    else:
                        print(formatter.warning("Nothing to redo"))
                    continue

                if command == 'save':
                    # Save calculation history to file
                    try:
                        calc.save_history()
                        print(formatter.success("History saved successfully"))
                    except Exception as e:
                        print(formatter.error(f"Error saving history: {e}"))
                    continue

                if command == 'load':
                    # Load calculation history from file
                    try:
                        calc.load_history()
                        print(formatter.success("History loaded successfully"))
                    except Exception as e:
                        print(formatter.error(f"Error loading history: {e}"))    
                    continue

                if command in ['add', 'subtract', 'multiply', 'divide', 'power', 'root', 'modulus', 'int_divide', 'percentage', 'abs_diff']:
                    # Perform the specified arithmetic operation
                    try:
                        print(formatter.prompt("\nEnter numbers (or 'cancel' to abort):"))
                        a = input(formatter.prompt("First number: "))
                        if a.lower() == 'cancel':
                            print(formatter.info("Operation cancelled"))
                            continue
                        b = input(formatter.prompt("Second number: "))
                        if b.lower() == 'cancel':
                            print(formatter.info("Operation cancelled"))
                            continue

                        # Create the appropriate operation instance using the Factory pattern
                        operation = OperationFactory.create_operation(command)
                        calc.set_operation(operation)

                        # Perform the calculation
                        result = calc.perform_operation(a, b)

                        # Normalize the result if it's a Decimal
                        if isinstance(result, Decimal):
                            result = result.normalize()

                        print(formatter.result(f"\nResult: {result}"))
                    except (ValidationError, OperationError) as e:
                        # Handle known exceptions related to validation or operation errors
                        print(formatter.error(f"Error: {e}"))
                    except Exception as e: # pragma: no cover
                        # Handle any unexpected exceptions
                        print(formatter.error(f"Unexpected error: {e}")) # pragma: no cover
                    continue

                # Handle unknown commands
                print(formatter.warning(f"Unknown command: '{command}'. Type 'help' for available commands."))
            except KeyboardInterrupt:
                # Handle Ctrl+C interruption gracefully
                print(formatter.error("\nOperation cancelled")) # pragma: no cover
                continue # pragma: no cover
            except EOFError:
                # Handle end-of-file (e.g., Ctrl+D) gracefully
                print(formatter.error("\nInput terminated. Exiting..."))
                break
            except Exception as e: # pragma: no cover
                # Handle any other unexpected exceptions
                print(formatter.error(f"Error: {e}")) # pragma: no cover
                continue # pragma: no cover

    except Exception as e: # pragma: no cover
        # Handle fatal errors during initialization
        print(formatter.error(f"Fatal error: {e}")) # pragma: no cover
        logging.error(f"Fatal error in calculator REPL: {e}") # pragma: no cover
        raise