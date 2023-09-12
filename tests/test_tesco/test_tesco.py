import pytest

import autoshop


@pytest.mark.parametrize("args, kwargs, expected", [
    (
        [],
        dict(description="Yorkshire Provender Tomato & Red Pepper Soup & Wensleydale 560G"),
        autoshop.tesco.Quantity(amount=560, unit="g"),
    ),
])
def test_get_quantity_from_description(args, kwargs, expected):
    actual = autoshop.tesco.get_quantity_from_description(*args, **kwargs)
    assert expected == actual
