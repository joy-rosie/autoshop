import functools
from typing import Optional

import pint

__all__ = [
    "parse_to",
    "parse_to_grams",
    "parse_to_milliliters",
]


@functools.cache
def registry() -> pint.UnitRegistry:
    unit_registry = pint.UnitRegistry()
    unit_registry.define("ltr = liter")
    return unit_registry


def parse_to(
    amount: float,
    unit_from: str,
    unit_to: str,
    unit_registry: Optional[pint.UnitRegistry] = None,
) -> float:
    if unit_registry is None:
        unit_registry = registry()
    try:
        return (
            (amount * unit_registry.parse_units(unit_from.casefold()))
            .to(unit_to.casefold())
            .magnitude
        )
    except Exception:
        return float("nan")


def parse_to_grams(
    amount: float,
    unit: str,
    unit_registry: Optional[pint.UnitRegistry] = None,
) -> float:
    return parse_to(
        amount=amount,
        unit_from=unit,
        unit_to="g",
        unit_registry=unit_registry,
    )


def parse_to_milliliters(
    amount: float,
    unit: str,
    unit_registry: Optional[pint.UnitRegistry] = None,
) -> float:
    return parse_to(
        amount=amount,
        unit_from=unit,
        unit_to="ml",
        unit_registry=unit_registry,
    )
