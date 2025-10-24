"""
tests/test_help_menu.py

Unit and integration tests for the Help Menu system using the Decorator pattern.

These tests verify:
- BasicHelp outputs core static help lines correctly.
- OperationsHelpDecorator dynamically appends operations from OperationFactory.
- Decorator chaining works correctly at multiple levels.
- build_help_menu() integrates decorators and operation registry properly.
- Edge cases, idempotence, and registry safety are handled.
- Output formatting, indentation, and placeholder text behave as expected.
"""

import pytest
from app.help_menu import BasicHelp, OperationsHelpDecorator, build_help_menu, HelpDecorator
from app.operations import OperationFactory


# ----------------------------------------------------------------------
# Helper: _norm
# ----------------------------------------------------------------------
# Normalizes whitespace in strings to single spaces for stable assertion
# comparisons across multi-line help text.
# ----------------------------------------------------------------------
def _norm(s: str) -> str:
    """Normalize whitespace in a string to single spaces for stable comparisons."""
    return " ".join(s.split())


# ----------------------------------------------------------------------
# Fixture: reset_operations_registry
# ----------------------------------------------------------------------
# Ensures OperationFactory._operations is cleared before and restored after
# each test, preventing cross-test contamination.
# ----------------------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_operations_registry():
    original_ops = OperationFactory._operations.copy()
    OperationFactory._operations.clear()
    yield
    OperationFactory._operations.clear()
    OperationFactory._operations.update(original_ops)


# ----------------------------------------------------------------------
# BASIC HELP TESTS
# ----------------------------------------------------------------------
# Verify static help menu rendering: content, structure, indentation, and placeholders.
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
# OPERATIONS HELP DECORATOR TESTS
# ----------------------------------------------------------------------
# Test dynamic help rendering from OperationFactory, including edge cases.
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
# DECORATOR CHAINING TESTS
# ----------------------------------------------------------------------
# Verify that multiple layers of OperationsHelpDecorator and HelpDecorator
# correctly aggregate help content.
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
# BUILD HELP MENU INTEGRATION TESTS
# ----------------------------------------------------------------------
# Full integration of decorators with OperationFactory registry using
# build_help_menu() for various operation sets and edge cases.
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
# ADDITIONAL EDGE CASE TESTS
# ----------------------------------------------------------------------
# Test special characters in operation names, empty DESCRIPTION/doc,
# long names/descriptions, mixed-case names, nested decorators, placeholder
# replacement, and exit line position.
# ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "ops_dict",
    [
        {"add 123": type("AddOp", (), {"DESCRIPTION": "Adds numbers"})},
        {"sub-ops": type("SubOp", (), {"DESCRIPTION": "Subtracts numbers"})},
        {"√root": type("RootOp", (), {"DESCRIPTION": "Root operation"})},
    ],
)
def test_operations_help_special_char_names(ops_dict):
    """Ensure operations with special characters render correctly."""
    OperationFactory._operations = ops_dict.copy()
    rendered = OperationsHelpDecorator(BasicHelp()).render()
    for name, cls in ops_dict.items():
        assert name in rendered
        assert cls.DESCRIPTION in rendered



@pytest.mark.parametrize(
    "ops_dict",
    [
        {"empty_desc": type("EmptyOp", (), {"DESCRIPTION": ""})},
        {"empty_doc": type("DocOp", (), {"__doc__": ""})},
    ],
)
def test_operations_help_empty_description_or_doc(ops_dict):
    """Fallback to class name when DESCRIPTION and docstring are empty."""
    OperationFactory._operations = ops_dict.copy()
    rendered = OperationsHelpDecorator(BasicHelp()).render()
    for name, cls in ops_dict.items():
        assert name in rendered
        assert cls.__name__ in rendered  # should fallback to class name



def test_operations_help_long_names_and_descriptions():
    """Test rendering of operations with extremely long names and descriptions."""
    OperationFactory._operations = {
        "super_long_operation_name_exceeding_typical_length": type(
            "LongOp", (), {"DESCRIPTION": "A very long description to test formatting and line wrapping in help menu output"}
        )
    }
    rendered = OperationsHelpDecorator(BasicHelp()).render()
    assert "super_long_operation_name_exceeding_typical_length" in rendered
    assert "A very long description to test formatting" in rendered


def test_operations_help_mixed_case_names():
    OperationFactory._operations = {
        "ADD": type("AddOp", (), {"DESCRIPTION": "Uppercase add"}),
        "add": type("AddOp", (), {"DESCRIPTION": "Lowercase add"})
    }
    rendered = OperationsHelpDecorator(BasicHelp()).render()
    assert "ADD" in rendered
    assert "add" in rendered
    assert "Uppercase add" in rendered
    assert "Lowercase add" in rendered


def test_operations_help_empty_registry_multiple_decorators():
    OperationFactory._operations.clear()
    component = BasicHelp()
    component = OperationsHelpDecorator(OperationsHelpDecorator(component))
    rendered = component.render()
    assert "(no operations available)" in rendered
    assert "<operations>" not in rendered


def test_operations_help_nested_decorators_mixed_content():
    OperationFactory._operations = {
        "op1": type("Op1", (), {"DESCRIPTION": "Desc1"}),
        "op2": type("Op2", (), {"__doc__": "Doc2"}),
        "op3": type("Op3", (), {})  # fallback to class name
    }
    component = BasicHelp()
    for _ in range(3):
        component = OperationsHelpDecorator(component)
    rendered = HelpDecorator(component).render()

    assert "op1" in rendered and "Desc1" in rendered
    assert "op2" in rendered and "Doc2" in rendered
    assert "op3" in rendered and "Op3" in rendered


def test_operations_help_placeholder_replacement():
    OperationFactory._operations = {}
    rendered = OperationsHelpDecorator(BasicHelp()).render()
    assert "<operations>" not in rendered
    assert "(no operations available)" in rendered


@pytest.mark.parametrize(
    "ops_dict",
    [
        {"add": type("AddOp", (), {"DESCRIPTION": "Adds"})},
        {},  # empty registry
    ],
)
def test_help_menu_exit_always_last(ops_dict):
    OperationFactory._operations = ops_dict.copy()
    result = build_help_menu()
    assert result.strip().endswith("exit        - Exit the calculator")