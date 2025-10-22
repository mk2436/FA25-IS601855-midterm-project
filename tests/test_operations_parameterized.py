import pytest
from decimal import Decimal, getcontext
from app.operations import (
    Addition,
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
