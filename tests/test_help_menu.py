import pytest
from app.help_menu import BasicHelp, OperationsHelpDecorator, build_help_menu, HelpDecorator
from app.operations import OperationFactory


@pytest.fixture(autouse=True)
def reset_operations_registry():
    """Ensure OperationFactory._operations is reset cleanly for each test."""
    original_ops = OperationFactory._operations.copy()
    OperationFactory._operations.clear()
    yield
    OperationFactory._operations.clear()
    OperationFactory._operations.update(original_ops)


# --------------------------------------------------------------------
# BASIC HELP TESTS
# --------------------------------------------------------------------

@pytest.mark.parametrize(
    "expected_substring",
    [
        "Available commands:",
        "history - Show calculation history",
        "clear - Clear calculation history",
        "undo - Undo the last calculation",
        "redo - Redo the last undone calculation",
        "save - Save calculation history to file",
        "load - Load calculation history from file",
        "exit - Exit the calculator",
    ],
)
def test_basic_help_contains_expected_text(expected_substring):
    """Ensure BasicHelp.render() outputs all core help lines."""
    help_text = BasicHelp().render()
    assert expected_substring in help_text


def test_basic_help_structure_and_placeholder():
    """Verify BasicHelp uses the <operations> placeholder properly."""
    help_text = BasicHelp().render()
    assert "<operations>" in help_text
    assert help_text.startswith("Available commands:")
    assert help_text.endswith("exit - Exit the calculator\n")


# --------------------------------------------------------------------
# OPERATIONS DECORATOR TESTS
# --------------------------------------------------------------------
@pytest.mark.parametrize(
    "ops_dict, expected_fragment",
    [
        # Basic empty case
        ({}, "(no operations available)"),

        # Simple two operations
        ({"add": "AddOperation", "sub": "SubtractOperation"}, "add, sub - Perform calculations"),

        # Three operations, unsorted input → sorted output check
        ({"mul": "MultiplyOperation", "add": "AddOperation", "div": "DivideOperation"}, 
         "add, div, mul - Perform calculations"),

        # Mixed case operation names
        ({"Sub": "SubtractOperation", "ADD": "AddOperation"}, 
         "ADD, Sub - Perform calculations"),

        # Symbolic and non-alphabetic operation keys
        ({"+": "AdditionOp", "-": "SubtractionOp"}, 
         "+, - - Perform calculations"),

        # Long operation names for formatting robustness
        ({"power": "PowerOperation", "square_root": "SquareRootOperation"}, 
         "power, square_root - Perform calculations"),

        # Keys with numbers
        ({"log10": "Log10Operation", "exp2": "Exp2Operation"}, 
         "exp2, log10 - Perform calculations"),

        # Ten operations (tests join and sorting stability)
        (
            {
                "a": "AOp",
                "b": "BOp",
                "c": "COp",
                "d": "DOp",
                "e": "EOp",
                "f": "FOp",
                "g": "GOp",
                "h": "HOp",
                "i": "IOp",
                "j": "JOp",
            },
            "a, b, c, d, e, f, g, h, i, j - Perform calculations",
        ),

        # Operations with underscores and uppercase
        ({"Add_Int": "AddIntOperation", "Sub_Float": "SubFloatOperation"},
         "Add_Int, Sub_Float - Perform calculations"),

        # Single operation for minimal valid case
        ({"sqrt": "SquareRootOperation"}, "sqrt - Perform calculations"),
    ],
)
def test_operations_help_dynamic_operations(ops_dict, expected_fragment):
    """Ensure OperationsHelpDecorator dynamically generates correct help text."""
    OperationFactory._operations = ops_dict.copy()
    decorated = OperationsHelpDecorator(BasicHelp())
    result = decorated.render()

    assert "Available commands:" in result
    assert expected_fragment in result
    assert "<operations>" not in result



# --------------------------------------------------------------------
# DECORATOR CHAINING TESTS
# --------------------------------------------------------------------

def test_decorator_chaining_multiple_wrappers():
    """Ensure multiple decorator layers delegate correctly."""
    OperationFactory._operations = {"add": "AddOperation"}
    base = BasicHelp()
    level1 = OperationsHelpDecorator(base)
    level2 = HelpDecorator(level1)  # double wrap (noop but tests chainability)

    result = level2.render()

    assert "Available commands:" in result
    assert "add - Perform calculations" in result


# --------------------------------------------------------------------
# INTEGRATION TESTS
# --------------------------------------------------------------------

@pytest.mark.parametrize(
    "operations_dict",
    [
        {},
        {"mul": "MultiplyOperation", "div": "DivideOperation"},
        {"exp": "ExponentOperation", "log": "LogOperation", "tan": "TangentOperation"},
    ],
)
def test_build_help_menu_integration(operations_dict):
    """Integration test for build_help_menu() using current registry."""
    OperationFactory._operations = operations_dict.copy()

    result = build_help_menu()
    assert "Available commands:" in result

    if operations_dict:
        for op_name in operations_dict.keys():
            assert op_name in result
        assert "<operations>" not in result
    else:
        assert "(no operations available)" in result


def test_build_help_menu_idempotent_output():
    """Ensure repeated calls to build_help_menu() produce consistent results."""
    OperationFactory._operations = {"add": "AddOperation"}
    first = build_help_menu()
    second = build_help_menu()
    assert first == second
