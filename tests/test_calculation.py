"""
This module contains comprehensive tests for the Calculation class, covering:
1. Basic arithmetic operations (addition, subtraction, multiplication, division)
2. Advanced operations (power, root, modulus, integer division, percentage)
3. Edge cases for all operations
4. Input validation and error handling
5. Object serialization (to/from dict)
6. String representation and formatting
7. Object comparison and equality

Each test section uses parameterized tests to cover multiple scenarios efficiently.
All numeric operations use Decimal for exact arithmetic precision.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from app.calculation import Calculation
from app.exceptions import OperationError, ValidationError
import logging


# ------------------------------------------------------------
# ADDITION EDGE CASES
# Verifies addition behavior across a wide range of inputs:
# - positive and negative operands
# - zero handling (0 + x, x + 0)
# - decimal precision and very large/small magnitudes
# - special Decimal values (Infinity, -Infinity, NaN)
# This helps ensure addition is stable and matches mathematical
# expectations for edge inputs.
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("5"), Decimal("3"), Decimal("8")),                     # Normal positive numbers
        (Decimal("3"), Decimal("5"), Decimal("8")),                     # Reversed operands
        (Decimal("-5"), Decimal("-3"), Decimal("-8")),                  # Both negative
        (Decimal("-3"), Decimal("-5"), Decimal("-8")),                  # Reversed negatives
        (Decimal("5.5"), Decimal("3.3"), Decimal("8.8")),               # Decimal numbers
        (Decimal("0"), Decimal("0"), Decimal("0")),                     # Both operands zero
        (Decimal("0"), Decimal("5"), Decimal("5")),                     # Zero vs positive
        (Decimal("-5"), Decimal("0"), Decimal("-5")),                   # Negative vs zero
        (Decimal("1E-10"), Decimal("0"), Decimal("1E-10")),             # Very small numbers
        (Decimal("1E+10"), Decimal("1E+9"), Decimal("1.1E+10")),        # Large numbers
        (Decimal('Infinity'), Decimal('1'), Decimal('Infinity')),       # Positive infinity
        (Decimal('-Infinity'), Decimal('1'), Decimal('-Infinity')),     # Negative infinity
        (Decimal('NaN'), Decimal('1'), Decimal('NaN')),                 # Not a Number
        (Decimal('1E-100'), Decimal('1E-100'), Decimal('2E-100')),      # very small
        (Decimal('1E+100'), Decimal('1E+100'), Decimal('2E+100')),      # very large
    ],
)
def test_addition_edge_cases(a, b, expected):
    """Test addition with edge cases including negatives, zeros, decimals, and very large/small numbers."""
    calc = Calculation(operation="Addition", operand1=a, operand2=b)
    if expected.is_nan():
        assert calc.result.is_nan()
    else:
        assert calc.result == expected


# ------------------------------------------------------------
# SUBTRACTION EDGE CASES
# Verifies subtraction across edge scenarios:
# - order sensitivity (a - b vs b - a)
# - negative operands and sign correctness
# - zeros and very large/small magnitudes
# - special-case handling when infinities are involved
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("5"), Decimal("3"), Decimal("2")),                      # Normal positive numbers
        (Decimal("3"), Decimal("5"), Decimal("-2")),                     # Reversed operands
        (Decimal("-5"), Decimal("-3"), Decimal("-2")),                   # Both negative
        (Decimal("-3"), Decimal("-5"), Decimal("2")),                    # Reversed negatives
        (Decimal("0"), Decimal("0"), Decimal("0")),                      # Both zero
        (Decimal("0"), Decimal("5"), Decimal("-5")),                     # Zero minus positive
        (Decimal("5"), Decimal("0"), Decimal("5")),                      # Positive minus zero
        (Decimal("1E+10"), Decimal("1E+9"), Decimal("9E+9")),            # Large numbers
        (Decimal("1E-10"), Decimal("0"), Decimal("1E-10")),               # Very small numbers
        (Decimal('1E-100'), Decimal('2E-100'), Decimal('-1E-100')),       # very small
        (Decimal('1E+100'), Decimal('5E+99'), Decimal('5E+99')),         # very large
    ],
)
def test_subtraction_edge_cases(a, b, expected):
    """Test subtraction with edge cases including negatives, zeros, and very large/small numbers."""
    calc = Calculation(operation="Subtraction", operand1=a, operand2=b)
    if expected.is_nan():
        assert calc.result.is_nan()
    else:
        assert calc.result == expected



@pytest.mark.parametrize(
    "a, b",
    [
        (Decimal('Infinity'), Decimal('Infinity')),
        (Decimal('-Infinity'), Decimal('-Infinity')),
    ]
)
def test_subtraction_infinity_raises(a, b):
    """
    Test that subtracting infinities of the same sign raises OperationError,
    since Infinity - Infinity and -Infinity - -Infinity are invalid.
    """
    with pytest.raises(OperationError):
        Calculation(operation="Subtraction", operand1=a, operand2=b)


# ------------------------------------------------------------
# MULTIPLICATION EDGE CASES
# Covers multiplication properties and edge cases:
# - sign rules (negative * positive, negative * negative)
# - propagation of zero and identity elements
# - behaviour with extremely large or small values
# - how Infinity interacts with finite values
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("5"), Decimal("3"), Decimal("15")),        # Positive * positive
        (Decimal("-5"), Decimal("3"), Decimal("-15")),      # Negative * positive
        (Decimal("5"), Decimal("-3"), Decimal("-15")),      # Positive * negative
        (Decimal("-5"), Decimal("-3"), Decimal("15")),      # Negative * negative
        (Decimal("0"), Decimal("5"), Decimal("0")),         # Zero * positive
        (Decimal("5"), Decimal("0"), Decimal("0")),         # Positive * zero
        (Decimal("1E5"), Decimal("1E3"), Decimal("1E8")),   # Large numbers
        (Decimal("1E-5"), Decimal("1E-3"), Decimal("1E-8")), # Very small numbers
        (Decimal('1E-100'), Decimal('1E-100'), Decimal('1E-200')),
        (Decimal('-1E+100'), Decimal('2'), Decimal('-2E+100')),
        (Decimal('Infinity'), Decimal('2'), Decimal('Infinity')),
    ],
)
def test_multiplication_edge_cases(a, b, expected):
    """Test multiplication with edge cases including negatives, zeros, decimals, and extreme values."""
    calc = Calculation(operation="Multiplication", operand1=a, operand2=b)
    if expected.is_nan():
        assert calc.result.is_nan()
    else:
        assert calc.result == expected


@pytest.mark.parametrize(
    "a, b",
    [
        (Decimal('Infinity'), Decimal('0')),
        (Decimal('-Infinity'), Decimal('0')),
    ]
)
def test_multiplication_infinity_raises(a, b):
    """
    Test that multiplying infinities of the same sign raises OperationError,
    since Infinity * Infinity and -Infinity * -Infinity are invalid.
    """
    with pytest.raises(OperationError):
        Calculation(operation="Multiplication", operand1=a, operand2=b)



# ------------------------------------------------------------
# DIVISION EDGE CASES
# Tests division and its edge behavior:
# - correct quotient sign given operand signs
# - zero dividend vs zero divisor distinctions
# - behavior for very large/small magnitudes
# - interactions with Infinity and -Infinity
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("6"), Decimal("3"), Decimal("2")),          # Normal division
        (Decimal("-6"), Decimal("3"), Decimal("-2")),        # Negative dividend
        (Decimal("6"), Decimal("-3"), Decimal("-2")),        # Negative divisor
        (Decimal("-6"), Decimal("-3"), Decimal("2")),        # Both negative
        (Decimal("0"), Decimal("5"), Decimal("0")),          # Zero dividend
        (Decimal("1E10"), Decimal("1E5"), Decimal("1E5")),   # Large numbers
        (Decimal("1E-10"), Decimal("1E-5"), Decimal("1E-5")), # Very small numbers
        (Decimal('1E-100'), Decimal('1E-100'), Decimal('1')), # near-zero numbers
        (Decimal('Infinity'), Decimal('1'), Decimal('Infinity')),
        (Decimal('1'), Decimal('Infinity'), Decimal('0')),
    ],
)
def test_division_edge_cases(a, b, expected):
    """Test division with edge cases including negatives, zero dividend, and very large/small numbers."""
    calc = Calculation(operation="Division", operand1=a, operand2=b)
    assert calc.result == expected


@pytest.mark.parametrize(
    "a, b",
    [
        (Decimal('Infinity'), Decimal('0')),
        (Decimal('-Infinity'), Decimal('0')),
    ]
)
def test_division_by_zero_raises(a, b):
    """
    Test that dividing infinities of the same sign raises OperationError,
    since Infinity / Infinity and -Infinity / -Infinity are invalid.
    """
    with pytest.raises(OperationError):
        Calculation(operation="Division", operand1=a, operand2=b)

# ------------------------------------------------------------
# POWER EDGE CASES
# Validates exponentiation for:
# - integer exponents, including zero and negative bases
# - fractional exponents (e.g. sqrt via 0.5)
# - the special 0**0 handling used by this calculator
# - avoiding overflow by testing reduced large exponents
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("2"), Decimal("3"), Decimal("8")),          # Normal positive exponent
        (Decimal("5"), Decimal("0"), Decimal("1")),          # Any number to power 0
        (Decimal("0"), Decimal("5"), Decimal("0")),          # Zero to positive power
        (Decimal("0"), Decimal("0"), Decimal("1")),          # 0**0 special case
        (Decimal("1E2"), Decimal("3"), Decimal("1E6")),      # Large numbers
        (Decimal('9'), Decimal('0.5'), Decimal('3')),       # square root via power
        (Decimal('0'), Decimal('0'), Decimal('1')),         # 0**0
    ],
)
def test_power_edge_cases(a, b, expected):
    """Test exponentiation with edge cases including zero, large numbers, and 0**0."""
    calc = Calculation(operation="Power", operand1=a, operand2=b)
    assert calc.result == expected


# ------------------------------------------------------------
# ROOT EDGE CASES
# Tests n-th root extraction, covering:
# - standard integer roots (square, cube, etc.)
# - precision for very large and very small radicands
# - validation that even roots of negative numbers are rejected
# - consistency with power operation for reciprocal exponents
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("16"), Decimal("2"), Decimal("4")),         # Square root
        (Decimal("27"), Decimal("3"), Decimal("3")),         # Cube root
        (Decimal("1E8"), Decimal("4"), Decimal("1E2")),     # Large number root
        (Decimal("1E-8"), Decimal("4"), Decimal("0.01000000000000000020816681711721685132943093776702880859375")),   # Small number root
        (Decimal(81), Decimal("-4"), Decimal("0.333333333333333314829616256247390992939472198486328125")),  # Negative root (4th root of 81)
    ],
)
def test_root_edge_cases(a, b, expected):
    """Test root extraction including square/cube roots, very large and very small numbers."""
    calc = Calculation(operation="Root", operand1=a, operand2=b)
    assert calc.result == expected


@pytest.mark.parametrize(
    "a, b",
    [
        (Decimal('-16'), Decimal('2')),
        (Decimal('-27'), Decimal('4')),
        (Decimal('-64'), Decimal('3')),
    ],
)
def test_root_negative_base_raises(a, b):
    """Test that extracting even roots of negative numbers raises OperationError."""
    with pytest.raises(OperationError):
        Calculation(operation="Root", operand1=a, operand2=b)

# ------------------------------------------------------------
# MODULUS EDGE CASES
# Verifies remainder behavior for positive/negative operands:
# - sign handling of dividend/divisor
# - zero dividend returns zero
# - modulus by zero should raise an OperationError
# - tiny decimal values and edge rounding behavior
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("10"), Decimal("3"), Decimal("1")),         # Basic modulus
        (Decimal("10"), Decimal("-3"), Decimal("1")),        # Negative divisor
        (Decimal("-10"), Decimal("3"), Decimal("-1")),       # Negative dividend
        (Decimal("-10"), Decimal("-3"), Decimal("-1")),      # Both negative
        (Decimal("0"), Decimal("3"), Decimal("0")),          # Zero dividend
        (Decimal('10'), Decimal('0'), OperationError),      # modulus by zero
        (Decimal('1E-100'), Decimal('1E-100'), Decimal('0')), # tiny numbers
    ],
)
def test_modulus_edge_cases(a, b, expected):
    """Test modulus operation including positive/negative operands and zero dividend."""
    if expected is OperationError:
        with pytest.raises(OperationError):
            Calculation(operation="Modulus", operand1=a, operand2=b)
    else:
        calc = Calculation(operation="Modulus", operand1=a, operand2=b)
        assert calc.result == expected


# ------------------------------------------------------------
# INTEGER DIVISION EDGE CASES
# Tests integer (floor/truncating) division semantics:
# - sign rules for quotient with negative operands
# - division by zero should raise an error
# - behavior for tiny and very large values
# - ensures result is an integer-like Decimal consistent with semantics
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("10"), Decimal("3"), Decimal("3")),         # Normal positive
        (Decimal("10"), Decimal("-3"), Decimal("-3")),       # Negative divisor
        (Decimal("-10"), Decimal("3"), Decimal("-3")),       # Negative dividend
        (Decimal("-10"), Decimal("-3"), Decimal("3")),       # Both negative
        (Decimal("0"), Decimal("5"), Decimal("0")),          # Zero dividend
        (Decimal('10'), Decimal('0'), OperationError),
        (Decimal('1E-100'), Decimal('1E-100'), Decimal('1')),
        (Decimal('-10'), Decimal('3'), Decimal('-3')),
    ],
)
def test_integer_division_edge_cases(a, b, expected):
    """Test integer division including negative numbers, zero dividend, and reversed operands."""
    if expected is OperationError:
        with pytest.raises(OperationError):
            Calculation(operation="Int_division", operand1=a, operand2=b)
    else:
        calc = Calculation(operation="Int_division", operand1=a, operand2=b)
        assert calc.result == expected


# ------------------------------------------------------------
# PERCENTAGE EDGE CASES
# Covers percentage computations and validation rules:
# - standard percent-of calculations (a% of b)
# - zero base or zero percentage handling
# - rejects negative values where business rules disallow them
# - precision and rounding for decimal percentages
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("50"), Decimal("10"), Decimal("5")),         # Normal percentage
        (Decimal("100"), Decimal("0"), Decimal("0")),         # Zero percentage
        (Decimal("75.5"), Decimal("20"), Decimal("15.1")),   # Decimal percentage
        (Decimal("1E6"), Decimal("25"), Decimal("250000")),  # Large numbers
        (Decimal("0"), Decimal("100"), Decimal("0")),         # Zero base
        (Decimal('1E-10'), Decimal('50'), Decimal('5E-11')),
        (Decimal('50'), Decimal('-10'), OperationError),
        (Decimal('-50'), Decimal('10'), OperationError),
    ],
)
def test_percentage_edge_cases(a, b, expected):
    """Test percentage calculations including zeros, decimals, and large numbers."""
    if expected is OperationError:
        with pytest.raises(OperationError):
            Calculation(operation="Percentage", operand1=a, operand2=b)
    else:
        calc = Calculation(operation="Percentage", operand1=a, operand2=b)
        assert calc.result == expected

@pytest.mark.parametrize(
    "operand1, operand2, expected_message",
    [
        (Decimal("-50"), Decimal("10"), "Negative values are not allowed in percentage calculations"),
        (Decimal("50"), Decimal("-10"), "Negative values are not allowed in percentage calculations"),
        (Decimal("-5"), Decimal("-10"), "Negative values are not allowed in percentage calculations"),
    ],
)
def test_percentage_negative_values(operand1, operand2, expected_message):
    """Test that negative values in percentage calculation raise an OperationError."""
    with pytest.raises(OperationError, match=expected_message):
        Calculation(operation="Percentage", operand1=operand1, operand2=operand2)




# ------------------------------------------------------------
# ABSOLUTE DIFFERENCE TESTS
# Verifies absolute difference (|a - b|) correctness:
# - sign-agnostic results for operand ordering
# - correct handling for decimals and extreme magnitudes
# - identical operands should yield zero
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("5"), Decimal("3"), Decimal("2")),               # Normal positive
        (Decimal("3"), Decimal("5"), Decimal("2")),               # Reversed positive
        (Decimal("-5"), Decimal("-3"), Decimal("2")),             # Both negative
        (Decimal("-3"), Decimal("-5"), Decimal("2")),             # Reverse negatives
        (Decimal("5.5"), Decimal("3.3"), Decimal("2.2")),         # Decimals
        (Decimal("3.3"), Decimal("5.5"), Decimal("2.2")),         # Reverse decimals
        (Decimal("0"), Decimal("0"), Decimal("0")),               # Both zero
        (Decimal("0"), Decimal("5"), Decimal("5")),               # Zero vs positive
        (Decimal("5"), Decimal("0"), Decimal("5")),               # Positive vs zero
        (Decimal("-5"), Decimal("0"), Decimal("5")),              # Negative vs zero
        (Decimal("0"), Decimal("-5"), Decimal("5")),              # Zero vs negative
        (Decimal("1E-10"), Decimal("0"), Decimal("1E-10")),       # Very small difference
        (Decimal("1E+10"), Decimal("1E+9"), Decimal("9E+9")),     # Large numbers
        (Decimal("-1E+10"), Decimal("1E+10"), Decimal("2E+10")),  # Large neg vs pos
        (Decimal("123.456"), Decimal("123.456"), Decimal("0")),   # Identical decimals
    ],
)
def test_abs_difference_valid(a, b, expected):
    """Test valid absolute difference calculations, including edge cases."""
    calc = Calculation(operation="Abs_difference", operand1=a, operand2=b)
    assert calc.result == expected


# ------------------------------------------------------------
# UNKNOWN OPERATION TEST
# Ensures the Calculation class rejects unsupported operations:
# - raises OperationError with an informative message
# - protects against typos or unexpected input values
# ------------------------------------------------------------

@pytest.mark.parametrize(
    "operation, operand1, operand2",
    [
        ("Unknown", Decimal("5"), Decimal("3")),
        ("XYZ", Decimal("10"), Decimal("2")),
    ],
)
def test_unknown_operation(operation, operand1, operand2):
    """Test that unknown operations raise an OperationError."""
    with pytest.raises(OperationError, match="Unknown operation"):
        Calculation(operation=operation, operand1=operand1, operand2=operand2)


# ------------------------------------------------------------
# TO_DICT TEST
# Validates object serialization via to_dict():
# - Decimal operands/results should be serialized as strings
# - timestamp should be ISO formatted string
# - output dictionary structure must match storage expectations
# ------------------------------------------------------------

def test_to_dict():
    """Test converting a Calculation object to a dictionary representation."""
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    result_dict = calc.to_dict()
    assert result_dict == {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": calc.timestamp.isoformat(),
    }


# ------------------------------------------------------------
# FROM_DICT TESTS
# Tests deserialization and validation when loading saved data:
# - correctly parses decimals and timestamps
# - logs a warning if stored result disagrees with computed result
# - raises OperationError for malformed input
# ------------------------------------------------------------

@pytest.mark.parametrize(
    "data, expect_error",
    [
        (
            {
                "operation": "Addition",
                "operand1": "2",
                "operand2": "3",
                "result": "5",
                "timestamp": datetime.now().isoformat(),
            },
            False,
        ),
        (
            {
                "operation": "Addition",
                "operand1": "invalid",
                "operand2": "3",
                "result": "5",
                "timestamp": datetime.now().isoformat(),
            },
            True,
        ),
    ],
)
def test_from_dict(data, expect_error):
    """Test creating Calculation from dictionary, valid and invalid."""
    if expect_error:
        with pytest.raises(OperationError, match="Invalid calculation data"):
            Calculation.from_dict(data)
    else:
        calc = Calculation.from_dict(data)
        assert calc.operation == "Addition"
        assert calc.operand1 == Decimal("2")
        assert calc.operand2 == Decimal("3")
        assert calc.result == Decimal("5")



# ------------------------------------------------------------
# FORMAT_RESULT METHOD TESTS
# Ensures user-facing numeric formatting is correct:
# - respects requested precision and rounds appropriately
# - returns string names for NaN/Infinity rather than raising
# - trims unnecessary trailing zeros when appropriate
# ------------------------------------------------------------

@pytest.mark.parametrize(
    "operand1, operand2, precision, expected_output",
    [
        (Decimal("1"), Decimal("3"), 2, "0.33"),
        (Decimal("1"), Decimal("3"), 10, "0.3333333333"),
    ],
)
def test_format_result(operand1, operand2, precision, expected_output):
    """Test formatted decimal output for various precision levels."""
    calc = Calculation(operation="Division", operand1=operand1, operand2=operand2)
    assert calc.format_result(precision=precision) == expected_output


# ------------------------------------------------------------
# EQUALITY TEST
# Confirms object equality semantics for Calculation:
# - equality requires operation, operands, result, and timestamp to match
# - inequality when any key attribute differs
# - comparisons with unrelated types should be handled gracefully
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "calc1_params, calc2_params, expected_equal",
    [
        (("Addition", Decimal("2"), Decimal("3")), ("Addition", Decimal("2"), Decimal("3")), True),
        (("Addition", Decimal("2"), Decimal("3")), ("Subtraction", Decimal("5"), Decimal("3")), False),
    ],
)
def test_equality(calc1_params, calc2_params, expected_equal):
    """Test equality and inequality between Calculation instances."""
    calc1 = Calculation(*calc1_params)
    calc2 = Calculation(*calc2_params)
    if expected_equal:
        assert calc1 == calc2
    else:
        assert calc1 != calc2


# ------------------------------------------------------------
# LOGGING WARNING TEST
# Verifies that loading a Calculation from dict logs a WARNING when the
# stored result differs from the recomputed value. This prevents silent
# data corruption and helps debugging saved history issues.
# ------------------------------------------------------------
def test_from_dict_result_mismatch(caplog):
    """Test that mismatched saved vs computed results trigger a logging warning."""
    data = {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "10",  # Incorrect result
        "timestamp": datetime.now().isoformat(),
    }

    with caplog.at_level(logging.WARNING):
        Calculation.from_dict(data)

    assert "Loaded calculation result 10 differs from computed result 5" in caplog.text



# ------------------------------------------------------------
# __str__ METHOD TESTS
# Verifies the concise human-readable string returned by __str__:
# - format: Operation(operand1, operand2) = result
# - intended for display in CLIs or logs where brevity is desired
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "operation, operand1, operand2, expected_str",
    [
        ("Addition", Decimal("2"), Decimal("3"), "Addition(2, 3) = 5"),
        ("Subtraction", Decimal("10"), Decimal("4"), "Subtraction(10, 4) = 6"),
        ("Multiplication", Decimal("2.5"), Decimal("4"), "Multiplication(2.5, 4) = 10.0"),
    ],
)
def test_str_representation(operation, operand1, operand2, expected_str):
    """
    Test the __str__ method returns a human-readable calculation summary.
    """
    # Arrange & Act
    calc = Calculation(operation=operation, operand1=operand1, operand2=operand2)

    # Assert
    assert str(calc) == expected_str


# ------------------------------------------------------------
# __repr__ METHOD TESTS
# Tests the developer-focused representation produced by __repr__:
# - Should include class name and key attributes
# - Must be unambiguous and suitable for debugging/logs
# - Ensures timestamp and Decimal values are represented clearly
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "operation, operand1, operand2",
    [
        ("Addition", Decimal("2"), Decimal("3")),
        ("Division", Decimal("8"), Decimal("2")),
    ],
)
def test_repr_representation(operation, operand1, operand2):
    """
    Test the __repr__ method returns a detailed unambiguous string with all attributes.
    """
    # Arrange
    calc = Calculation(operation=operation, operand1=operand1, operand2=operand2)

    # Act
    repr_str = repr(calc)

    # Assert
    assert repr_str.startswith("Calculation(")
    assert f"operation='{operation}'" in repr_str
    assert f"operand1={operand1}" in repr_str
    assert f"operand2={operand2}" in repr_str
    assert f"result={calc.result}" in repr_str
    assert f"timestamp='{calc.timestamp.isoformat()}'" in repr_str


# ------------------------------------------------------------
# __eq__ METHOD TESTS
# Tests the equality operator (__eq__) behaviour:
# - Equality when all relevant attributes match
# - Inequality for differing operation, operands, or result
# - Comparison with non-Calculation types should return NotImplemented
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "calc1_params, calc2_params, expected_equal",
    [
        # Identical calculations (should be equal)
        (("Addition", Decimal("2"), Decimal("3")), ("Addition", Decimal("2"), Decimal("3")), True),

        # Different operations (should not be equal)
        (("Addition", Decimal("2"), Decimal("3")), ("Subtraction", Decimal("2"), Decimal("3")), False),

        # Different operands (should not be equal)
        (("Addition", Decimal("5"), Decimal("3")), ("Addition", Decimal("2"), Decimal("3")), False),

        # Different results (should not be equal)
        (("Addition", Decimal("2"), Decimal("3")), ("Addition", Decimal("2"), Decimal("4")), False),
    ],
)
def test_equality_method(calc1_params, calc2_params, expected_equal):
    """
    Test equality operator (__eq__) compares all relevant attributes correctly.
    """
    # Arrange
    calc1 = Calculation(*calc1_params)
    calc2 = Calculation(*calc2_params)

    # Act & Assert
    if expected_equal:
        assert calc1 == calc2
    else:
        assert calc1 != calc2


def test_equality_with_non_calculation_type():
    """
    Test that equality comparison with non-Calculation object returns NotImplemented.
    """
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    assert calc.__eq__("not a calculation") is NotImplemented


# ------------------------------------------------------------
# format_result METHOD TESTS
# Tests the format_result method for various scenarios:
# - Different precision levels
# - Rounding behavior
# - Handling of invalid Decimal values (NaN, Infinity)  
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "operand1, operand2, precision, expected_output",
    [
        (Decimal("1"), Decimal("3"), 2, "0.33"),
        (Decimal("1"), Decimal("3"), 10, "0.3333333333"),
        (Decimal("2.50000"), Decimal("1"), 5, "2.5"),
        (Decimal("123.456789"), Decimal("1"), 3, "123.457"),  # rounding check
    ],
)
def test_format_result_valid_cases(operand1, operand2, precision, expected_output):
    """
    Test format_result outputs the correct decimal string based on precision.
    """
    # Arrange
    calc = Calculation(operation="Division", operand1=operand1, operand2=operand2)

    # Act
    formatted = calc.format_result(precision)

    # Assert
    assert formatted == expected_output


@pytest.mark.parametrize(
    "invalid_value, expected_output",
    [
        (Decimal("NaN"), "NaN"),             # Not a number
        (Decimal("Infinity"), "Infinity"),   # Infinite value
        (Decimal("-Infinity"), "-Infinity"), # Negative infinity
    ],
)
def test_format_result_invalid_operation(invalid_value, expected_output):
    """
    Test that format_result handles invalid or non-finite Decimal values gracefully.

    This test ensures that if the result cannot be quantized (e.g., NaN, Infinity),
    the method returns the string representation of the result instead of raising an error.
    """
    # Arrange
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc.result = invalid_value

    # Act
    formatted = calc.format_result(precision=5)

    # Assert
    assert formatted == expected_output



# ------------------------------------------------------------
# CALCULATION METHOD TESTS
# High-level integration tests for the Calculation class:
# - Verifies each supported operation returns the correct Decimal result
# - Covers a representative set of valid inputs for each operation
# - Acts as a sanity check that operation dispatch and core logic are intact
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "operation, operand1, operand2, expected_result",
    [
        ("Addition", Decimal("2"), Decimal("3"), Decimal("5")),         
        ("Subtraction", Decimal("10.5"), Decimal("4.5"), Decimal("6")),    
        ("Division", Decimal("6"), Decimal("3"), Decimal("2")),        
        ("Multiplication", Decimal("1"), Decimal("0"), Decimal("0")),
        ("Power", Decimal("2"), Decimal("3"), Decimal("8")),         
        ("Root", Decimal("16"), Decimal("2"), Decimal("4")),        
    ],
)
def test_calculation(operation, operand1, operand2, expected_result):
    """Test various valid calculation scenarios."""
    # Arrange & Act
    calc = Calculation(operation=operation, operand1=operand1, operand2=operand2)

    # Assert
    assert calc.result == expected_result

