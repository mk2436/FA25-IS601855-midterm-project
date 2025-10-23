import pytest
from decimal import Decimal
from datetime import datetime
from app.calculation import Calculation
from app.exceptions import OperationError, ValidationError
import logging
# ------------------------------------------------------------
# ADDITION EDGE CASES (mirroring Abs_difference style)
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("5"), Decimal("3"), Decimal("8")),       # Normal positive numbers
        (Decimal("3"), Decimal("5"), Decimal("8")),       # Reversed operands
        (Decimal("-5"), Decimal("-3"), Decimal("-8")),    # Both negative
        (Decimal("-3"), Decimal("-5"), Decimal("-8")),    # Reversed negatives
        (Decimal("5.5"), Decimal("3.3"), Decimal("8.8")), # Decimal numbers
        (Decimal("0"), Decimal("0"), Decimal("0")),       # Both operands zero
        (Decimal("0"), Decimal("5"), Decimal("5")),       # Zero vs positive
        (Decimal("-5"), Decimal("0"), Decimal("-5")),     # Negative vs zero
        (Decimal("1E-10"), Decimal("0"), Decimal("1E-10")), # Very small numbers
        (Decimal("1E+10"), Decimal("1E+9"), Decimal("1.1E+10")), # Large numbers
    ],
)
def test_addition_edge_cases(a, b, expected):
    """Test addition with edge cases including negatives, zeros, decimals, and very large/small numbers."""
    calc = Calculation(operation="Addition", operand1=a, operand2=b)
    assert calc.result == expected


# ------------------------------------------------------------
# SUBTRACTION EDGE CASES
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("5"), Decimal("3"), Decimal("2")),          # Normal positive numbers
        (Decimal("3"), Decimal("5"), Decimal("-2")),         # Reversed operands
        (Decimal("-5"), Decimal("-3"), Decimal("-2")),       # Both negative
        (Decimal("-3"), Decimal("-5"), Decimal("2")),        # Reversed negatives
        (Decimal("0"), Decimal("0"), Decimal("0")),          # Both zero
        (Decimal("0"), Decimal("5"), Decimal("-5")),         # Zero minus positive
        (Decimal("5"), Decimal("0"), Decimal("5")),          # Positive minus zero
        (Decimal("1E+10"), Decimal("1E+9"), Decimal("9E+9")), # Large numbers
        (Decimal("1E-10"), Decimal("0"), Decimal("1E-10")),  # Very small numbers
    ],
)
def test_subtraction_edge_cases(a, b, expected):
    """Test subtraction with edge cases including negatives, zeros, and very large/small numbers."""
    calc = Calculation(operation="Subtraction", operand1=a, operand2=b)
    assert calc.result == expected


# ------------------------------------------------------------
# MULTIPLICATION EDGE CASES
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
    ],
)
def test_multiplication_edge_cases(a, b, expected):
    """Test multiplication with edge cases including negatives, zeros, decimals, and extreme values."""
    calc = Calculation(operation="Multiplication", operand1=a, operand2=b)
    assert calc.result == expected


# ------------------------------------------------------------
# DIVISION EDGE CASES
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
    ],
)
def test_division_edge_cases(a, b, expected):
    """Test division with edge cases including negatives, zero dividend, and very large/small numbers."""
    calc = Calculation(operation="Division", operand1=a, operand2=b)
    assert calc.result == expected


# ------------------------------------------------------------
# POWER EDGE CASES
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("2"), Decimal("3"), Decimal("8")),          # Normal positive exponent
        (Decimal("5"), Decimal("0"), Decimal("1")),          # Any number to power 0
        (Decimal("0"), Decimal("5"), Decimal("0")),          # Zero to positive power
        (Decimal("0"), Decimal("0"), Decimal("1")),          # 0**0 special case
        (Decimal("1E2"), Decimal("3"), Decimal("1E6")),      # Large numbers
    ],
)
def test_power_edge_cases(a, b, expected):
    """Test exponentiation with edge cases including zero, large numbers, and 0**0."""
    calc = Calculation(operation="Power", operand1=a, operand2=b)
    assert calc.result == expected


# ------------------------------------------------------------
# ROOT EDGE CASES
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("16"), Decimal("2"), Decimal("4")),         # Square root
        (Decimal("27"), Decimal("3"), Decimal("3")),         # Cube root
        (Decimal("1E8"), Decimal("4"), Decimal("1E2")),     # Large number root
        (Decimal("1E-8"), Decimal("4"), Decimal("0.01000000000000000020816681711721685132943093776702880859375")),   # Small number root
    ],
)
def test_root_edge_cases(a, b, expected):
    """Test root extraction including square/cube roots, very large and very small numbers."""
    calc = Calculation(operation="Root", operand1=a, operand2=b)
    assert calc.result == expected


# ------------------------------------------------------------
# MODULUS EDGE CASES
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("10"), Decimal("3"), Decimal("1")),         # Basic modulus
        (Decimal("10"), Decimal("-3"), Decimal("1")),        # Negative divisor
        (Decimal("-10"), Decimal("3"), Decimal("-1")),       # Negative dividend
        (Decimal("-10"), Decimal("-3"), Decimal("-1")),      # Both negative
        (Decimal("0"), Decimal("3"), Decimal("0")),          # Zero dividend
    ],
)
def test_modulus_edge_cases(a, b, expected):
    """Test modulus operation including positive/negative operands and zero dividend."""
    calc = Calculation(operation="Modulus", operand1=a, operand2=b)
    assert calc.result == expected


# ------------------------------------------------------------
# INTEGER DIVISION EDGE CASES
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("10"), Decimal("3"), Decimal("3")),         # Normal positive
        (Decimal("10"), Decimal("-3"), Decimal("-3")),       # Negative divisor
        (Decimal("-10"), Decimal("3"), Decimal("-3")),       # Negative dividend
        (Decimal("-10"), Decimal("-3"), Decimal("3")),       # Both negative
        (Decimal("0"), Decimal("5"), Decimal("0")),          # Zero dividend
    ],
)
def test_integer_division_edge_cases(a, b, expected):
    """Test integer division including negative numbers, zero dividend, and reversed operands."""
    calc = Calculation(operation="Int_division", operand1=a, operand2=b)
    assert calc.result == expected


# ------------------------------------------------------------
# PERCENTAGE EDGE CASES
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Decimal("50"), Decimal("10"), Decimal("5")),         # Normal percentage
        (Decimal("100"), Decimal("0"), Decimal("0")),         # Zero percentage
        (Decimal("75.5"), Decimal("20"), Decimal("15.1")),   # Decimal percentage
        (Decimal("1E6"), Decimal("25"), Decimal("250000")),  # Large numbers
        (Decimal("0"), Decimal("100"), Decimal("0")),         # Zero base
    ],
)
def test_percentage_edge_cases(a, b, expected):
    """Test percentage calculations including zeros, decimals, and large numbers."""
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
# FORMAT RESULT TEST
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
# Calculation method TESTS
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

