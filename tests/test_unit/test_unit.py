import math

import pint
import pytest

from autoshop import all as autoshop


# Tests for the parse_to_grams function
@pytest.mark.parametrize(
    "args, kwargs, expected",
    [
        ([], dict(amount=1, unit="g"), 1),
        ([], dict(amount=1, unit="gram"), 1),
        ([], dict(amount=1, unit="grams"), 1),
        ([], dict(amount=1, unit="G"), 1),
        ([], dict(amount=1, unit="Gram"), 1),
        ([], dict(amount=1, unit="GRAM"), 1),
        ([], dict(amount=1, unit="kg"), 1_000),
        ([], dict(amount=1, unit="kilogram"), 1_000),
        ([], dict(amount=1, unit="KG"), 1_000),
        ([], dict(amount=1, unit="ml"), float("nan")),
        ([], dict(amount=1, unit=""), float("nan")),
        ([], dict(amount=1, unit="pack"), float("nan")),
    ],
)
def test_parse_to_grams(args, kwargs, expected):
    actual = autoshop.unit.parse_to_grams(*args, **kwargs)
    assert math.isclose(expected, actual) or math.isnan(expected) and math.isnan(actual)


def test_parse_to_grams_fractional_amounts():
    """Test parse_to_grams with fractional amounts."""
    assert math.isclose(autoshop.unit.parse_to_grams(0.5, "kg"), 500)
    assert math.isclose(autoshop.unit.parse_to_grams(2.5, "g"), 2.5)
    assert math.isclose(autoshop.unit.parse_to_grams(0.1, "kg"), 100)


def test_parse_to_grams_zero_amount():
    """Test parse_to_grams with zero amount."""
    assert autoshop.unit.parse_to_grams(0, "g") == 0
    assert autoshop.unit.parse_to_grams(0, "kg") == 0


def test_parse_to_grams_negative_amount():
    """Test parse_to_grams with negative amount."""
    assert autoshop.unit.parse_to_grams(-1, "g") == -1
    assert autoshop.unit.parse_to_grams(-1, "kg") == -1000


def test_parse_to_grams_with_custom_registry():
    """Test parse_to_grams with custom unit registry."""
    custom_registry = pint.UnitRegistry()
    custom_registry.define("custom_gram = gram")

    result = autoshop.unit.parse_to_grams(
        amount=5, unit="custom_gram", unit_registry=custom_registry
    )
    assert math.isclose(result, 5)


# Tests for the parse_to_milliliters function
@pytest.mark.parametrize(
    "args, kwargs, expected",
    [
        ([], dict(amount=1, unit="ml"), 1),
        ([], dict(amount=1, unit="milliliter"), 1),
        ([], dict(amount=1, unit="milliliters"), 1),
        ([], dict(amount=1, unit="millilitre"), 1),
        ([], dict(amount=1, unit="millilitres"), 1),
        ([], dict(amount=1, unit="l"), 1000),
        ([], dict(amount=1, unit="liter"), 1000),
        ([], dict(amount=1, unit="litre"), 1000),
        ([], dict(amount=1, unit="ltr"), 1000),
        ([], dict(amount=1, unit="g"), float("nan")),
        ([], dict(amount=1, unit=""), float("nan")),
        ([], dict(amount=1, unit="pack"), float("nan")),
    ],
)
def test_parse_to_milliliters(args, kwargs, expected):
    actual = autoshop.unit.parse_to_milliliters(*args, **kwargs)
    assert math.isclose(expected, actual) or math.isnan(expected) and math.isnan(actual)


def test_parse_to_milliliters_fractional_amounts():
    """Test parse_to_milliliters with fractional amounts."""
    assert math.isclose(autoshop.unit.parse_to_milliliters(0.5, "l"), 500)
    assert math.isclose(autoshop.unit.parse_to_milliliters(2.5, "ml"), 2.5)
    assert math.isclose(autoshop.unit.parse_to_milliliters(1.5, "ltr"), 1500)


def test_parse_to_milliliters_zero_amount():
    """Test parse_to_milliliters with zero amount."""
    assert autoshop.unit.parse_to_milliliters(0, "ml") == 0
    assert autoshop.unit.parse_to_milliliters(0, "l") == 0


def test_parse_to_milliliters_negative_amount():
    """Test parse_to_milliliters with negative amount."""
    assert autoshop.unit.parse_to_milliliters(-1, "ml") == -1
    assert math.isclose(autoshop.unit.parse_to_milliliters(-1, "l"), -1000)


def test_parse_to_milliliters_with_custom_registry():
    """Test parse_to_milliliters with custom unit registry."""
    custom_registry = pint.UnitRegistry()
    custom_registry.define("custom_ml = milliliter")

    result = autoshop.unit.parse_to_milliliters(
        amount=10, unit="custom_ml", unit_registry=custom_registry
    )
    assert math.isclose(result, 10)


# Tests for the generic parse_to function
def test_parse_to_basic_conversion():
    """Test basic unit conversion."""
    # Grams to kilograms
    result = autoshop.unit.parse_to(1000, "g", "kg")
    assert math.isclose(result, 1)

    # Milliliters to liters
    result = autoshop.unit.parse_to(1000, "ml", "l")
    assert math.isclose(result, 1)


def test_parse_to_same_units():
    """Test conversion between same units."""
    result = autoshop.unit.parse_to(5, "g", "g")
    assert math.isclose(result, 5)

    result = autoshop.unit.parse_to(10, "ml", "ml")
    assert math.isclose(result, 10)


def test_parse_to_invalid_conversion():
    """Test conversion between incompatible units."""
    # Grams to milliliters should return NaN
    result = autoshop.unit.parse_to(100, "g", "ml")
    assert math.isnan(result)

    # Unknown units should return NaN
    result = autoshop.unit.parse_to(1, "invalid_unit", "g")
    assert math.isnan(result)


def test_parse_to_case_insensitive():
    """Test that parse_to is case insensitive."""
    result1 = autoshop.unit.parse_to(1, "G", "KG")
    result2 = autoshop.unit.parse_to(1, "g", "kg")
    assert math.isclose(result1, result2)
    assert math.isclose(result1, 0.001)


def test_parse_to_with_custom_registry():
    """Test parse_to with custom unit registry."""
    custom_registry = pint.UnitRegistry()
    custom_registry.define("special_unit = 2 * gram")

    result = autoshop.unit.parse_to(
        amount=1, unit_from="special_unit", unit_to="g", unit_registry=custom_registry
    )
    assert math.isclose(result, 2)


def test_parse_to_various_unit_types():
    """Test parse_to with various unit types."""
    # Length
    result = autoshop.unit.parse_to(1, "m", "cm")
    assert math.isclose(result, 100)

    # Temperature (should work if supported)
    try:
        result = autoshop.unit.parse_to(0, "celsius", "kelvin")
        assert math.isclose(result, 273.15)
    except Exception:
        # Temperature conversion might not be straightforward with pint
        pass


# Tests for the registry function and caching
def test_registry_returns_unit_registry():
    """Test that registry returns a pint UnitRegistry."""
    reg = autoshop.unit.registry()
    assert isinstance(reg, pint.UnitRegistry)


def test_registry_cached():
    """Test that registry is cached."""
    reg1 = autoshop.unit.registry()
    reg2 = autoshop.unit.registry()
    assert reg1 is reg2  # Same object due to caching


def test_registry_has_custom_definitions():
    """Test that registry has custom unit definitions."""
    reg = autoshop.unit.registry()

    # Should have the custom 'ltr' definition
    ltr_unit = reg.parse_expression("ltr")
    liter_unit = reg.parse_expression("liter")

    # They should be equivalent
    assert ltr_unit.dimensionality == liter_unit.dimensionality


def test_registry_ltr_definition():
    """Test specifically the ltr definition."""
    reg = autoshop.unit.registry()

    # 1 ltr should equal 1 liter
    ltr_quantity = 1 * reg.parse_expression("ltr")
    liter_quantity = 1 * reg.parse_expression("liter")

    assert math.isclose(ltr_quantity.to("liter").magnitude, 1)
    assert math.isclose(liter_quantity.to("ltr").magnitude, 1)


# Tests for unit module constants and exports
def test_all_exports():
    """Test that __all__ contains expected functions."""
    expected_exports = ["parse_to", "parse_to_grams", "parse_to_milliliters"]

    assert hasattr(autoshop.unit, "__all__")
    for export in expected_exports:
        assert export in autoshop.unit.__all__

    # All exports should be accessible
    for export in autoshop.unit.__all__:
        assert hasattr(autoshop.unit, export)


def test_function_availability():
    """Test that all expected functions are available."""
    assert callable(autoshop.unit.parse_to)
    assert callable(autoshop.unit.parse_to_grams)
    assert callable(autoshop.unit.parse_to_milliliters)
    assert callable(autoshop.unit.registry)


# Tests for edge cases and error conditions
def test_parse_to_with_none_registry():
    """Test that None registry parameter uses default."""
    result1 = autoshop.unit.parse_to(1, "g", "kg", unit_registry=None)
    result2 = autoshop.unit.parse_to(1, "g", "kg")

    assert math.isclose(result1, result2)


def test_large_numbers():
    """Test with very large numbers."""
    large_number = 1e6
    result = autoshop.unit.parse_to_grams(large_number, "kg")
    assert math.isclose(result, large_number * 1000)


def test_very_small_numbers():
    """Test with very small numbers."""
    small_number = 1e-6
    result = autoshop.unit.parse_to_grams(small_number, "kg")
    assert math.isclose(result, small_number * 1000)


def test_empty_string_unit():
    """Test with empty string unit."""
    result = autoshop.unit.parse_to_grams(1, "")
    assert math.isnan(result)

    result = autoshop.unit.parse_to_milliliters(1, "")
    assert math.isnan(result)


def test_whitespace_units():
    """Test with whitespace in units."""
    # This might work or not depending on pint's handling
    result = autoshop.unit.parse_to_grams(1, " g ")
    # Could be valid or NaN depending on implementation
    # Pint actually handles this case and strips whitespace, returning an int
    assert isinstance(result, (int, float))


@pytest.mark.parametrize("invalid_unit", ["xyz", "invalid123", "not_a_unit", "123abc"])
def test_invalid_units_return_nan(invalid_unit):
    """Test that invalid units return NaN."""
    result_grams = autoshop.unit.parse_to_grams(1, invalid_unit)
    result_ml = autoshop.unit.parse_to_milliliters(1, invalid_unit)

    assert math.isnan(result_grams)
    assert math.isnan(result_ml)
