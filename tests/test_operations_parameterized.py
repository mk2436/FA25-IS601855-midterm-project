"""
tests/test_operations_parameterized.py

This module provides parameterized test cases for all calculator operations using pytest.mark.parametrize.
It complements test_operations.py by focusing on data-driven testing with multiple test scenarios.

Key features:
1. Tests all arithmetic and special operations with varied inputs
2. Uses pytest's parametrize decorator for concise test definitions
3. Covers edge cases and precision testing with Decimal numbers
4. Validates both successful operations and error conditions
5. Tests with:
   - Positive/negative numbers
   - Zero and near-zero values
   - Large numbers and exponents
   - Decimal precision cases
   - Invalid inputs and error handling

Each operation section is clearly marked with headers and includes both valid and invalid test cases
where applicable. The precision is set to 28 digits for high-accuracy decimal calculations.
"""

import pytest
from decimal import Decimal, getcontext
from app.operations import (
    Abs_difference,
    Addition,
    Percentage,
    Subtraction,
    Multiplication,
    Division,
    Power,
    Root,
    Modulus,
    Int_division,
)
from app.exceptions import ValidationError

getcontext().prec = 28


# ---------------------------------------------------------
# Addition
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("5"), Decimal("3"), Decimal("8")),
        (Decimal("-5"), Decimal("-3"), Decimal("-8")),
        (Decimal("-5"), Decimal("3"), Decimal("-2")),
        (Decimal("5.5"), Decimal("3.3"), Decimal("8.8")),
        (Decimal("1e10"), Decimal("1e10"), Decimal("20000000000")),
    ],
)
def test_addition(a, b, expected):
    op = Addition()
    assert op.execute(a, b) == expected


# ---------------------------------------------------------
# Subtraction
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("5"), Decimal("3"), Decimal("2")),
        (Decimal("-5"), Decimal("-3"), Decimal("-2")),
        (Decimal("-5"), Decimal("3"), Decimal("-8")),
        (Decimal("5.5"), Decimal("3.3"), Decimal("2.2")),
        (Decimal("1e10"), Decimal("1e9"), Decimal("9000000000")),
    ],
)
def test_subtraction(a, b, expected):
    op = Subtraction()
    assert op.execute(a, b) == expected


# ---------------------------------------------------------
# Multiplication
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("5"), Decimal("3"), Decimal("15")),
        (Decimal("-5"), Decimal("-3"), Decimal("15")),
        (Decimal("-5"), Decimal("3"), Decimal("-15")),
        (Decimal("5"), Decimal("0"), Decimal("0")),
        (Decimal("5.5"), Decimal("3.3"), Decimal("18.15")),
        (Decimal("1e5"), Decimal("1e5"), Decimal("10000000000")),
    ],
)
def test_multiplication(a, b, expected):
    op = Multiplication()
    assert op.execute(a, b) == expected


# ---------------------------------------------------------
# Division
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("6"), Decimal("2"), Decimal("3")),
        (Decimal("-6"), Decimal("-2"), Decimal("3")),
        (Decimal("-6"), Decimal("2"), Decimal("-3")),
        (Decimal("5.5"), Decimal("2"), Decimal("2.75")),
        (Decimal("0"), Decimal("5"), Decimal("0")),
        (Decimal("1.0000000000000001"), Decimal("0.0000000000000001"), Decimal("10000000000000001")),
   ],
)
def test_division_valid(a, b, expected):
    op = Division()
    assert op.execute(a, b) == expected


@pytest.mark.parametrize(
    "a, b",
    [
        (Decimal("5"), Decimal("0")),
        (Decimal("-10"), Decimal("0")),
        (Decimal("3.14159"), Decimal("0")),
        (Decimal("2"), Decimal("0.0000000000000000000000001")),  # near-zero divisor (allowed)
    ],
)
def test_division_zero_and_near_zero(a, b):
    op = Division()
    if b == 0:
        with pytest.raises(ValidationError, match="Division by zero is not allowed"):
            op.execute(a, b)
    else:
        result = op.execute(a, b)
        assert isinstance(result, Decimal)
        assert result == a / b


# ---------------------------------------------------------
# Power
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("2"), Decimal("3"), Decimal("8")),
        (Decimal("5"), Decimal("0"), Decimal("1")),
        (Decimal("5"), Decimal("1"), Decimal("5")),
        (Decimal("2.5"), Decimal("2"), Decimal("6.25")),
        (Decimal("0"), Decimal("5"), Decimal("0")),
        (Decimal("2"), Decimal("10"), Decimal("1024")),  # big exponent
        (Decimal("1.5"), Decimal("20"), Decimal("3325.256730079651")),  # precision/big exponent
    ],
)
def test_power_valid(a, b, expected):
    op = Power()
    result = op.execute(a, b)
    assert round(result, 10) == round(expected, 10)


@pytest.mark.parametrize(
    "a, b",
    [
        (Decimal("2"), Decimal("-3")),
        (Decimal("5"), Decimal("-1")),
    ],
)
def test_power_invalid(a, b):
    op = Power()
    with pytest.raises(ValidationError, match="Negative exponents not supported"):
        op.execute(a, b)


# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("9"), Decimal("2"), Decimal("3")),
        (Decimal("27"), Decimal("3"), Decimal("3")),
        (Decimal("16"), Decimal("4"), Decimal("2")),
        (Decimal("2.25"), Decimal("2"), Decimal("1.5")),
        (Decimal("1e10"), Decimal("5"), Decimal("100")),  # big exponent
    ],
)
def test_root_valid(a, b, expected):
    op = Root()
    assert round(op.execute(a, b), 10) == round(expected, 10)


@pytest.mark.parametrize(
    "a, b, message",
    [
        (Decimal("-9"), Decimal("2"), "Cannot calculate root of negative number"),  # negative root
        (Decimal("9"), Decimal("0"), "Zero root is undefined"),
    ],
)
def test_root_invalid(a, b, message):
    op = Root()
    with pytest.raises(ValidationError, match=message):
        op.execute(a, b)


# ---------------------------------------------------------
# Modulus
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("10"), Decimal("3"), Decimal("1")),
        (Decimal("10"), Decimal("5"), Decimal("0")),
        (Decimal("0"), Decimal("3"), Decimal("0")),
        (Decimal("10"), Decimal("-3"), Decimal("1")), 
        (Decimal("-10"), Decimal("3"), Decimal("-1")), 
        (Decimal("-10"), Decimal("-3"), Decimal("-1")),
        (Decimal("10.75"), Decimal("2"), Decimal("0.75")),
        (Decimal("7.125"), Decimal("0.5"), Decimal("0.125")),
        (Decimal("5.123456789"), Decimal("0.001"), Decimal("0.000456789")),  # precision
        (Decimal("1e25"), Decimal("9"), Decimal("1")),  # large number
    ],
)
def test_modulus_valid(a, b, expected):
    op = Modulus()
    result = op.execute(a, b)
    assert result == expected


@pytest.mark.parametrize(
    "a, b",
    [
        (Decimal("5"), Decimal("0")),
        (Decimal("-1"), Decimal("0")),
        (Decimal("1"), Decimal("0.0000000000000000000000001")),  # near-zero divisor (allowed)
    ],
)
def test_modulus_zero_and_near_zero(a, b):
    op = Modulus()
    if b == 0:
        with pytest.raises(ValidationError, match="Division by zero is not allowed"):
            op.execute(a, b)
    else:
        result = op.execute(a, b)
        assert isinstance(result, Decimal)
        assert abs(result) < abs(b)


# ---------------------------------------------------------
# Integer Division
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("10"), Decimal("3"), Decimal("3")),
        (Decimal("10"), Decimal("5"), Decimal("2")),
        (Decimal("0"), Decimal("3"), Decimal("0")),
        (Decimal("-10"), Decimal("3"), Decimal("-3")),
        (Decimal("10"), Decimal("-3"), Decimal("-3")),
        (Decimal("-10"), Decimal("-3"), Decimal("3")),
        (Decimal("10.75"), Decimal("2"), Decimal("5")),
        (Decimal("7.125"), Decimal("0.5"), Decimal("14")),
        (Decimal("1e25"), Decimal("9"), Decimal("1111111111111111111111111")),  # big number
    ],
)
def test_int_division_valid(a, b, expected):
    op = Int_division()
    result = op.execute(a, b)
    assert result == expected


@pytest.mark.parametrize(
    "a, b",
    [
        (Decimal("5"), Decimal("0")),
        (Decimal("-10"), Decimal("0")),
        (Decimal("2"), Decimal("0.0000000000000000000000001")),  # near-zero divisor (allowed)
    ],
)
def test_int_division_zero_and_near_zero(a, b):
    op = Int_division()
    if b == 0:
        with pytest.raises(ValidationError, match="Division by zero is not allowed"):
            op.execute(a, b)
    else:
        result = op.execute(a, b)
        assert isinstance(result, Decimal)
        assert result == (a // b)


# ---------------------------------------------------------
# Percentage
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "a, b, expected",
    [
        ("50", "10", "5"),          # basic percentage
        ("100", "0", "0"),          # zero percentage
        ("1e6", "25", "250000"),    # large numbers
        ("75.5", "20", "15.1"),     # decimal percentage
    ],
)
def test_percentage_valid_cases(a, b, expected):
    """Test valid Percentage calculations."""
    op = Percentage()
    result = op.execute(Decimal(a), Decimal(b))
    # Compare as Decimals to avoid string formatting inconsistencies
    assert result == Decimal(expected), f"Expected {expected}, got {result}"


@pytest.mark.parametrize(
    "a, b, error, message",
    [
        ("-50", "10", ValidationError, "Percentage cannot be negative"),
        ("50", "-10", ValidationError, "Percentage cannot be negative"),
    ],
)
def test_percentage_invalid_cases(a, b, error, message):
    """Test invalid Percentage calculations raising ValidationError."""
    op = Percentage()
    with pytest.raises(error) as excinfo:
        op.execute(Decimal(a), Decimal(b))
    assert message in str(excinfo.value)


# ---------------------------------------------------------
# Absolute Difference
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("5"), Decimal("3"), Decimal("2")),              # Normal positive
        (Decimal("3"), Decimal("5"), Decimal("2")),              # Reverse order
        (Decimal("-5"), Decimal("-3"), Decimal("2")),            # Both negative
        (Decimal("-3"), Decimal("-5"), Decimal("2")),            # Reverse negatives
        (Decimal("5.5"), Decimal("3.3"), Decimal("2.2")),        # Decimal inputs
        (Decimal("3.3"), Decimal("5.5"), Decimal("2.2")),        # Reversed decimals
        (Decimal("0"), Decimal("0"), Decimal("0")),              # Both zero

        # --- Edge cases below ---
        (Decimal("1E-10"), Decimal("0"), Decimal("1E-10")),      # Very small decimal difference
        (Decimal("1E+10"), Decimal("1E+10"), Decimal("0")),      # Very large equal numbers
        (Decimal("1E+10"), Decimal("1E+9"), Decimal("9E+9")),    # Very large difference
        (Decimal("-1E+10"), Decimal("1E+10"), Decimal("2E+10")), # Large negative vs positive
        (Decimal("123.456"), Decimal("123.456"), Decimal("0")),  # Identical non-integer numbers
    ],
)
def test_abs_difference(a, b, expected):
    """Test absolute difference with normal and edge cases."""
    op = Abs_difference()
    assert op.execute(a, b) == expected