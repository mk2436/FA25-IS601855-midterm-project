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
from app.commands import OperationCommand, CommandQueue
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

        # Initialize a command queue for batching/enqueuing operations
        queue = CommandQueue()

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
                    continue

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

                # Queue management commands
                if command.startswith('queue'):
                    parts = command.split()
                    # Usage: queue add | queue run | queue show | queue clear
                    if len(parts) == 1:
                        print(formatter.info("Queue commands: add, run, show, clear"))
                        continue

                    sub = parts[1]
                    if sub == 'add':
                        # Interactive add: ask for operation and operands
                        op_name = input(formatter.prompt("Operation name: ")).strip()
                        if op_name.lower() == 'cancel':
                            print(formatter.info("Queue add cancelled"))
                            continue
                        if op_name not in OperationFactory._operations:
                            print(formatter.error(f"Unknown operation: {op_name}"))
                            continue
                        a = input(formatter.prompt("First number: ")).strip()
                        if a.lower() == 'cancel':
                            print(formatter.info("Queue add cancelled"))
                            continue
                        b = input(formatter.prompt("Second number: ")).strip()
                        if b.lower() == 'cancel':
                            print(formatter.info("Queue add cancelled"))
                            continue

                        try:
                            operation = OperationFactory.create_operation(op_name)
                            cmd = OperationCommand(operation, a, b)
                            queue.add(cmd)
                            print(formatter.success("Operation queued"))
                        except Exception as e:  # pragma: no cover
                            print(formatter.error(f"Could not queue operation: {e}")) # pragma: no cover
                        continue

                    if sub == 'run':
                        # Execute all queued commands
                        if not queue.list_commands():
                            print(formatter.info("Queue is empty"))
                            continue
                        try:
                            results = queue.execute_all(calc)
                            for i, r in enumerate(results, 1):
                                print(formatter.result(f"{i}. {r}"))
                        except Exception as e:  # pragma: no cover
                            print(formatter.error(f"Error executing queue: {e}")) # pragma: no cover
                        continue

                    if sub == 'show':
                        cmds = queue.list_commands()
                        if not cmds:
                            print(formatter.info("Queue is empty"))
                        else:
                            for i, c in enumerate(cmds, 1):
                                # Show operation class name and raw operands
                                print(formatter.info(f"{i}. {type(c.operation).__name__}({c.a}, {c.b})"))
                        continue

                    if sub == 'clear':
                        queue.clear()
                        print(formatter.success("Queue cleared"))
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

                        # Wrap it in a Command object and execute via the Calculator immediately
                        # (Note: to queue operations use the 'queue add' command)
                        cmd = OperationCommand(operation, a, b)
                        result = calc.execute_command(cmd)

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
                continue
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