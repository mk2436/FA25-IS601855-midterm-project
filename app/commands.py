from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List

from app.operations import Operation


class Command(ABC):
    """Abstract Command interface for the Command design pattern."""

    @abstractmethod
    def execute(self, receiver: Any) -> Any:
        """Execute the command against the given receiver (e.g., Calculator)."""
        raise NotImplementedError()


class OperationCommand(Command):
    """Concrete Command that wraps an Operation and its operands.

    The command does not perform validation itself; it delegates execution to
    the Calculator instance, which already handles validation, history, and
    observer notification.
    """

    def __init__(self, operation: Operation, a: Any, b: Any) -> None:
        self.operation = operation
        self.a = a
        self.b = b

    def execute(self, receiver: Any) -> Any:
        """Execute by setting the operation on the receiver and delegating.

        Args:
            receiver: Expected to be a Calculator instance with
                      set_operation and perform_operation methods.
        """
        # Set the current operation strategy on the receiver
        receiver.set_operation(self.operation)
        # Delegate execution to the Calculator (it will validate inputs)
        return receiver.perform_operation(self.a, self.b)


class CommandQueue:
    """Simple invoker that stores commands and can execute them sequentially."""

    def __init__(self) -> None:
        self._queue: List[Command] = []

    def add(self, command: Command) -> None:
        self._queue.append(command)

    def execute_all(self, receiver: Any) -> List[Any]:
        results: List[Any] = []
        while self._queue:
            cmd = self._queue.pop(0)
            results.append(cmd.execute(receiver))
        return results

    def list_commands(self) -> List[Command]:
        """Return a shallow copy of queued Command objects."""
        return list(self._queue)

    def clear(self) -> None:
        """Clear all queued commands."""
        self._queue.clear()
