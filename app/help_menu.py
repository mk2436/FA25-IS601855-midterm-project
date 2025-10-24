from abc import ABC, abstractmethod
from app.operations import OperationFactory


class HelpComponent(ABC):
    """Component interface for help menu pieces."""

    @abstractmethod
    def render(self) -> str:
        """Render the help text for this component."""


class BasicHelp(HelpComponent):
    """Concrete component that provides the base help text (non-operation commands)."""

    def render(self) -> str:
        return (
            "Available commands:\n"
            "  Operations:\n"
            "   <operations>\n"
            "\n"
            " Queuing Operations:\n"
            "   queue add <operation> <operand1> <operand2>     - Add operation to queue\n"
            "   queue run                                       - Execute all queued operations\n"
            "   queue show                                      - Show all queued operations\n"
            "   queue clear                                     - Clear the operation queue\n\n"
            " Other Commands:\n"
            "   history     - Show calculation history\n"
            "   clear       - Clear calculation history\n"
            "   undo        - Undo the last calculation\n"
            "   redo        - Redo the last undone calculation\n"
            "   save        - Save calculation history to file\n"
            "   load        - Load calculation history from file\n"
            "   exit        - Exit the calculator\n"
        )


class HelpDecorator(HelpComponent):
    """Base decorator that forwards render() to the wrapped component."""

    def __init__(self, component: HelpComponent) -> None:
        self._component = component

    def render(self) -> str:  # pragma: no cover - trivial forwarding
        return self._component.render()


class OperationsHelpDecorator(HelpDecorator):
    """Decorator that appends dynamically generated operations list.

    This class queries OperationFactory to build the list of available
    operation commands. Adding new operations to the factory will automatically
    appear in the rendered help text.
    """

    def render(self) -> str:
        base = super().render()

        # Pull operation mapping from the factory. Use the mapping keys as the
        # command names users type, and include the class name for clarity.
        ops = OperationFactory._operations  # read-only access to registry

        if not ops:
            operations_text = "  (no operations available)\n"
        else:
            lines = []
            # Detailed listing (one per line) with short descriptions when available
            for name in ops.keys():
                cls = ops[name]
                # Prefer DESCRIPTION attribute, fall back to first docstring line or class name
                desc = getattr(cls, 'DESCRIPTION', None)
                if not desc:
                    doc = (cls.__doc__ or "").strip().splitlines()
                    desc = doc[0] if doc else cls.__name__
                lines.append(f"     {name.ljust(12)} - {desc}")
            operations_text = "\n".join(lines) + "\n"

        # Replace placeholder in base help with generated operations text
        return base.replace("   <operations>\n", operations_text)


def build_help_menu() -> str:
    """Build the full help menu string.

    Args:
        color_fore: Optional colorama.Fore module/object to color headers.
        color_style: Optional colorama.Style module/object to style output.

    Returns:
        str: The rendered help menu (may include color sequences if color args provided).
    """
    component: HelpComponent = BasicHelp()
    component = OperationsHelpDecorator(component)

    rendered = component.render()

    return rendered
