import math

import pytest

import autoshop


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
