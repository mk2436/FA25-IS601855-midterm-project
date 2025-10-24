import pytest
from app.help_menu import BasicHelp, OperationsHelpDecorator, build_help_menu, HelpDecorator
from app.operations import OperationFactory


def _norm(s: str) -> str:
    """Normalize whitespace in a string to single spaces for stable comparisons."""
    return " ".join(s.split())


@pytest.fixture(autouse=True)
def reset_operations_registry():
    """Ensure OperationFactory._operations is reset cleanly for each test."""
    original_ops = OperationFactory._operations.copy()
    OperationFactory._operations.clear()
    yield
    OperationFactory._operations.clear()
    OperationFactory._operations.update(original_ops)


# --------------------------------------------------------------------
# BASIC HELP PARAMETERIZED TESTS
# --------------------------------------------------------------------

@pytest.mark.parametrize(
    "expected_substring",
    [
        "Available commands:",
        "history     - Show calculation history",
        "clear       - Clear calculation history",
        "undo        - Undo the last calculation",
        "redo        - Redo the last undone calculation",
        "save        - Save calculation history to file",
        "load        - Load calculation history from file",
        "exit        - Exit the calculator",
    ],
)
def test_basic_help_contains_expected_text(expected_substring):
    """Ensure BasicHelp.render() outputs all core help lines."""
    help_text = BasicHelp().render()
    assert _norm(expected_substring) in _norm(help_text)


@pytest.mark.parametrize(
    "assertion",
    [
        ("<operations>", True),
        ("Available commands:", True),
        ("exit        - Exit the calculator", True),
    ],
)
def test_basic_help_structure_and_placeholder(assertion):
    """Check key structure and placeholder presence in BasicHelp."""
    help_text = BasicHelp().render()
    target, expected = assertion
    assert (target in help_text) == expected


@pytest.mark.parametrize(
    "section_prefix",
    ["queue", "Operations:"],
)
def test_basic_help_indentation(section_prefix):
    """Ensure BasicHelp has consistent indentation for key sections."""
    lines = BasicHelp().render().splitlines()
    relevant_lines = [line for line in lines if section_prefix in line]
    assert relevant_lines, f"No lines found for section '{section_prefix}'"
    for line in relevant_lines:
        assert line.startswith("   ") or section_prefix == "Operations:", \
            f"Line not properly indented: {line}"


# --------------------------------------------------------------------
# OPERATIONS DECORATOR PARAMETERIZED TESTS
# --------------------------------------------------------------------

@pytest.mark.parametrize(
    "ops_dict",
    [
        {},  # No operations
        {"add": type("AddOp", (), {"DESCRIPTION": "Adds numbers"})},  # With DESCRIPTION
        {"sub": type("SubOp", (), {"__doc__": "Subtracts numbers"})},  # With docstring
        {"mystery": type("MysteryOp", (), {})},  # No docstring or DESCRIPTION
        {"blank": type("BlankOp", (), {"__doc__": ""})},  # Empty docstring
        {"long_operation_name": type("LongOp", (), {"DESCRIPTION": "Example description"})},
        {"ADD": type("AddOp", (), {"DESCRIPTION": "Uppercase add"})},
        {"sub": type("SubOp", (), {"DESCRIPTION": "Lowercase sub"})},
    ],
)
def test_operations_help_dynamic_and_edge_cases(ops_dict):
    """Test dynamic rendering, edge cases, and fallback behavior."""
    OperationFactory._operations = ops_dict.copy()
    rendered = OperationsHelpDecorator(BasicHelp()).render()

    assert "Available commands:" in rendered

    if not ops_dict:
        assert "(no operations available)" in rendered
    else:
        for name, cls in ops_dict.items():
            assert name in rendered
            desc = getattr(cls, "DESCRIPTION", None)
            if not desc:
                doc = (cls.__doc__ or "").strip().splitlines()
                desc = doc[0] if doc else cls.__name__
            assert desc in rendered

    assert "<operations>" not in rendered


@pytest.mark.parametrize(
    "ops_dict, expected_count",
    [
        ({"add": type("AddOp", (), {"DESCRIPTION": "Adds numbers"})}, 1),
        ({"add": type("AddOp", (), {"DESCRIPTION": "Adds numbers"})}, 1),  # Double decorator
    ],
)
def test_operations_help_double_decorator_idempotence(ops_dict, expected_count):
    """Ensure multiple decorator layers do not duplicate output."""
    OperationFactory._operations = ops_dict.copy()
    base = BasicHelp()
    decorated = OperationsHelpDecorator(OperationsHelpDecorator(base))
    rendered = decorated.render()
    desc = list(ops_dict.values())[0].DESCRIPTION
    assert rendered.count(desc) == expected_count


# --------------------------------------------------------------------
# DECORATOR CHAINING PARAMETERIZED TESTS
# --------------------------------------------------------------------

@pytest.mark.parametrize(
    "ops_dict, decorator_chain_depth",
    [
        ({"add": type("AddOp", (), {"DESCRIPTION": "Adds numbers"})}, 1),
        ({"sub": type("SubOp", (), {"DESCRIPTION": "Subtracts numbers"})}, 2),
        ({"mul": type("MulOp", (), {"DESCRIPTION": "Multiplies numbers"})}, 3),
    ],
)
def test_decorator_chaining_multiple_wrappers(ops_dict, decorator_chain_depth):
    """Ensure decorator chaining works at any depth."""
    OperationFactory._operations = ops_dict.copy()
    component = BasicHelp()
    for _ in range(decorator_chain_depth):
        component = OperationsHelpDecorator(component)
    result = HelpDecorator(component).render()

    for name, cls in ops_dict.items():
        assert name in result
        assert cls.DESCRIPTION in result
    assert "Available commands:" in result


# --------------------------------------------------------------------
# BUILD HELP MENU PARAMETERIZED INTEGRATION TESTS
# --------------------------------------------------------------------

@pytest.mark.parametrize(
    "operations_dict",
    [
        {},  # Empty registry
        {
            "mul": type("MulOp", (), {"DESCRIPTION": "Multiplies two numbers"}),
            "div": type("DivOp", (), {"__doc__": "Divides two numbers"}),
        },
        {
            "exp": type("ExpOp", (), {"DESCRIPTION": "Raises base to exponent"}),
            "log": type("LogOp", (), {"__doc__": "Computes logarithm"}),
            "tan": type("TanOp", (), {}),
        },
    ],
)
def test_build_help_menu_integration(operations_dict):
    """Integration test for build_help_menu() using various operation sets."""
    OperationFactory._operations = operations_dict.copy()
    result = build_help_menu()

    assert "Available commands:" in result

    if not operations_dict:
        assert "(no operations available)" in result
    else:
        for name, cls in operations_dict.items():
            assert name in result
            desc = getattr(cls, "DESCRIPTION", None)
            if not desc:
                doc = (cls.__doc__ or "").strip().splitlines()
                desc = doc[0] if doc else cls.__name__
            assert desc in result
        assert "<operations>" not in result


@pytest.mark.parametrize(
    "ops_dict",
    [
        {"add": type("AddOp", (), {"DESCRIPTION": "Adds two numbers"})},
        {"sub": type("SubOp", (), {"__doc__": "Subtracts two numbers"})},
    ],
)
def test_build_help_menu_idempotent_output(ops_dict):
    """Repeated calls to build_help_menu() should return the same string."""
    OperationFactory._operations = ops_dict.copy()
    first = build_help_menu()
    second = build_help_menu()
    assert first == second


@pytest.mark.parametrize(
    "ops_dict",
    [
        {"add": type("AddOp", (), {"DESCRIPTION": "Adds numbers"})},
        {},  # empty registry after clearing
    ],
)
def test_build_help_menu_registry_safety(ops_dict):
    """Ensure registry is not mutated and output remains valid."""
    OperationFactory._operations = ops_dict.copy()
    original = ops_dict.copy()
    result = build_help_menu()

    assert "Available commands:" in result
    assert OperationFactory._operations == original
    if not ops_dict:
        assert "(no operations available)" in result
    else:
        assert "Adds numbers" in result


@pytest.mark.parametrize(
    "ops_dict",
    [
        {"add": type("AddOp", (), {"DESCRIPTION": "Adds"})},
        {"mul": type("MulOp", (), {"DESCRIPTION": "Multiplies"})},
    ],
)
def test_help_menu_always_ends_with_exit(ops_dict):
    """Help menu should always end with the exit command line."""
    OperationFactory._operations = ops_dict.copy()
    result = build_help_menu()
    assert result.strip().endswith("exit        - Exit the calculator")
