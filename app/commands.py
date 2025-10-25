########################
# Command Module       #
########################
"""
This module implements the Command design pattern for the calculator application,
allowing operations to be encapsulated as command objects and executed
independently of the calculator's internal implementation.

Key Features:

1. Command Interface:
   - Defines an abstract Command class with an execute(receiver) method.
   - Decouples operation invocation from the Calculator.

2. Concrete Command:
   - OperationCommand wraps an Operation and its operands.
   - Delegates validation, execution, history management, and observer
     notification to the Calculator.
   
3. Command Queue:
   - Stores a list of Command objects for sequential execution.
   - Provides methods to add commands, execute all queued commands,
     list current commands, and clear the queue.
   - Supports batch operations and deferred execution.

4. Design Pattern Integration:
   - Implements the Command pattern for clean separation of concerns.
   - Facilitates undo/redo, queuing, and flexible operation scheduling.
   - Promotes scalability and maintainability of calculator operations.

5. Integration Features:
   - Works seamlessly with Calculator and Operation classes.
   - Enables consistent handling of multiple operation types.
   - Supports extensibility for future custom commands.

The module provides a structured approach to encapsulating calculator
operations, allowing flexible execution strategies and improved maintainability.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List

from app.operations import Operation


class Command(ABC):
    """
    Abstract Command interface for the Command design pattern.

    Defines the contract for command objects that encapsulate an action
    and its parameters. Concrete commands implement the execute() method
    to perform the action on a given receiver (e.g., Calculator).
    """

    @abstractmethod
    def execute(self, receiver: Any) -> Any:
        """
        Execute the command against the given receiver.

        Args:
            receiver (Any): The target object on which the command operates,
                            typically a Calculator instance.

        Returns:
            Any: The result of executing the command.
        """
        raise NotImplementedError()  # pragma: no cover - abstract method


class OperationCommand(Command):
    """
    Concrete Command that wraps an Operation and its operands.

    Delegates execution to the Calculator instance, which handles input
    validation, history recording, and observer notifications.
    """

    def __init__(self, operation: Operation, a: Any, b: Any) -> None:
        """
        Initialize an OperationCommand.

        Args:
            operation (Operation): The operation strategy to execute.
            a (Any): First operand for the operation.
            b (Any): Second operand for the operation.
        """
        self.operation = operation
        self.a = a
        self.b = b

    def execute(self, receiver: Any) -> Any:
        """
        Execute the operation command against the receiver.

        Sets the operation on the receiver and delegates execution to it.

        Args:
            receiver (Any): Expected to be a Calculator instance with
                            set_operation() and perform_operation() methods.

        Returns:
            Any: Result of the operation execution.
        """
        # Set the current operation strategy on the receiver
        receiver.set_operation(self.operation)
        # Delegate execution to the Calculator (it will validate inputs)
        return receiver.perform_operation(self.a, self.b)


class CommandQueue:
    """
    Simple invoker that stores commands and executes them sequentially.

    Implements the invoker part of the Command design pattern.
    """

    def __init__(self) -> None:
        """
        Initialize an empty command queue.
        """
        self._queue: List[Command] = []

    def add(self, command: Command) -> None:
        """
        Add a command to the queue.

        Args:
            command (Command): The command to enqueue.
        """
        self._queue.append(command)

    def execute_all(self, receiver: Any) -> List[Any]:
        """
        Execute all queued commands sequentially.

        Args:
            receiver (Any): The target object to execute the commands on,
                            typically a Calculator instance.

        Returns:
            List[Any]: A list of results from executing each command.
        """
        results: List[Any] = []
        while self._queue:
            cmd = self._queue.pop(0)
            results.append(cmd.execute(receiver))
        return results

    def list_commands(self) -> List[Command]:
        """
        Return a shallow copy of the queued commands.

        Returns:
            List[Command]: List of commands currently in the queue.
        """
        return list(self._queue)

    def clear(self) -> None:
        """
        Clear all commands from the queue.
        """
        self._queue.clear()
