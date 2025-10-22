import pytest
from decimal import Decimal
from datetime import datetime
from app.calculation import Calculation
from app.exceptions import OperationError
import logging
from decimal import InvalidOperation

# ------------------------------------------------------------
# ADDITION TESTS
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "operand1, operand2, expected_result",
    [
        (Decimal("2"), Decimal("3"), Decimal("5")),         # Simple positive numbers
        (Decimal("10.5"), Decimal("4.5"), Decimal("15")),   # Decimal numbers    
        (Decimal("-2"), Decimal("3"), Decimal("1")),        # Negative and positive
        (Decimal("0"), Decimal("0"), Decimal("0")),         # Both operands zero
    ],
)
def test_addition(operand1, operand2, expected_result):
    """Test various valid addition scenarios."""
    # Arrange & Act
    calc = Calculation(operation="Addition", operand1=operand1, operand2=operand2)

    # Assert
    assert calc.result == expected_result


# ------------------------------------------------------------
# SUBTRACTION TESTS
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "operand1, operand2, expected_result",
    [
        (Decimal("5"), Decimal("3"), Decimal("2")),
        (Decimal("3"), Decimal("5"), Decimal("-2")),
        (Decimal("0"), Decimal("7"), Decimal("-7")),
    ],
)
def test_subtraction(operand1, operand2, expected_result):
    """Test valid subtraction scenarios including negatives."""
    calc = Calculation(operation="Subtraction", operand1=operand1, operand2=operand2)
    assert calc.result == expected_result


# ------------------------------------------------------------
# MULTIPLICATION TESTS
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "operand1, operand2, expected_result",
    [
        (Decimal("4"), Decimal("2"), Decimal("8")),
        (Decimal("-4"), Decimal("2"), Decimal("-8")),
        (Decimal("0"), Decimal("5"), Decimal("0")),
    ],
)
def test_multiplication(operand1, operand2, expected_result):
    """Test valid multiplication cases including zero and negatives."""
    calc = Calculation(operation="Multiplication", operand1=operand1, operand2=operand2)
    assert calc.result == expected_result


# ------------------------------------------------------------
# DIVISION TESTS
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "operand1, operand2, expected_result",
    [
        (Decimal("8"), Decimal("2"), Decimal("4")),
        (Decimal("9"), Decimal("3"), Decimal("3")),
        (Decimal("-8"), Decimal("2"), Decimal("-4")),
    ],
)
def test_division(operand1, operand2, expected_result):
    """Test valid division operations."""
    calc = Calculation(operation="Division", operand1=operand1, operand2=operand2)
    assert calc.result == expected_result


@pytest.mark.parametrize(
    "operand1, operand2",
    [(Decimal("8"), Decimal("0")), (Decimal("0"), Decimal("0"))],
)
def test_division_by_zero(operand1, operand2):
    """Test division by zero raises an OperationError."""
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation(operation="Division", operand1=operand1, operand2=operand2)


# ------------------------------------------------------------
# POWER TESTS
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "operand1, operand2, expected_result",
    [
        (Decimal("2"), Decimal("3"), Decimal("8")),
        (Decimal("5"), Decimal("0"), Decimal("1")),
    ],
)
def test_power(operand1, operand2, expected_result):
    """Test exponentiation for positive exponents."""
    calc = Calculation(operation="Power", operand1=operand1, operand2=operand2)
    assert calc.result == expected_result


@pytest.mark.parametrize(
    "operand1, operand2",
    [
        (Decimal("2"), Decimal("-3")),
        (Decimal("10"), Decimal("-1")),
    ],
)
def test_negative_power(operand1, operand2):
    """Test that negative exponents raise an OperationError."""
    with pytest.raises(OperationError, match="Negative exponents are not supported"):
        Calculation(operation="Power", operand1=operand1, operand2=operand2)


# ------------------------------------------------------------
# ROOT TESTS
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "operand1, operand2, expected_result",
    [
        (Decimal("16"), Decimal("2"), Decimal("4")),
        (Decimal("27"), Decimal("3"), Decimal("3")),
    ],
)
def test_root(operand1, operand2, expected_result):
    """Test root extraction for valid inputs."""
    calc = Calculation(operation="Root", operand1=operand1, operand2=operand2)
    assert calc.result == expected_result


@pytest.mark.parametrize(
    "operand1, operand2",
    [
        (Decimal("-16"), Decimal("2")),
        (Decimal("-27"), Decimal("3")),
    ],
)
def test_invalid_root(operand1, operand2):
    """Test that invalid roots (negative numbers) raise an OperationError."""
    with pytest.raises(OperationError, match="Cannot calculate root of negative number"):
        Calculation(operation="Root", operand1=operand1, operand2=operand2)


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

