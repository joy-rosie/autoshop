import pytest

import autoshop


@pytest.mark.parametrize(
    "args, kwargs, expected",
    [
        (
            [],
            dict(
                description="Yorkshire Provender Tomato & Red Pepper Soup & Wensleydale 560G"
            ),
            autoshop.tesco.Quantity(amount=560, unit="g"),
        ),
        (
            [],
            dict(
                description="Tesco Reduced Sugar And Salt Baked Beans In Tomato Sauce 420G"
            ),
            autoshop.tesco.Quantity(amount=420, unit="g"),
        ),
        (
            [],
            dict(description="Tesco Sieved Tomatoes Passata 500G Ce"),
            autoshop.tesco.Quantity(amount=500, unit="g"),
        ),
        (
            [],
            dict(
                description="Organix 5 Sunshine Veggies with Red Lentils Organic Baby Food 190g"
            ),
            autoshop.tesco.Quantity(amount=190, unit="g"),
        ),
        (
            [],
            dict(description="Birds Eye Original 10 Beef Burgers With Onion 567G"),
            autoshop.tesco.Quantity(amount=567, unit="g"),
        ),
        (
            [],
            dict(description="Tesco Garlic Powder 45G .."),
            autoshop.tesco.Quantity(amount=45, unit="g"),
        ),
        (
            [],
            dict(description="Highland Spring Still Bottled Water 12 X 500Ml"),
            autoshop.tesco.Quantity(amount=12 * 500, unit="ml"),
        ),
        (
            [],
            dict(
                description="Tesco Apple & Raspberry No Added Sugar Sparkling Water 4X500ml"
            ),
            autoshop.tesco.Quantity(amount=4 * 500, unit="ml"),
        ),
        (
            [],
            dict(description="Highland Spring Still Water 6 X 1.5L"),
            autoshop.tesco.Quantity(amount=6 * 1.5, unit="l"),
        ),
        (
            [],
            dict(description="Tesco Strawberry Still Flavoured Water 1Ltr"),
            autoshop.tesco.Quantity(amount=1, unit="ltr"),
        ),
        (
            [],
            dict(description="Redmere Farms Garlic 4 Pack"),
            autoshop.tesco.Quantity(amount=4, unit="medium"),
        ),
        (
            [],
            dict(description="Tesco Red Onions 3Pack Minimum"),
            autoshop.tesco.Quantity(amount=3, unit="medium"),
        ),
        (
            [],
            dict(description="Tesco Cauliflower Rice 4 Pack 600G"),
            autoshop.tesco.Quantity(amount=600, unit="g"),
        ),
        (
            [],
            dict(description="Tesco Red Split Lentils 1Kg"),
            autoshop.tesco.Quantity(amount=1, unit="kg"),
        ),
    ],
)
def test_get_quantity_from_description(args, kwargs, expected):
    actual = autoshop.tesco.get_quantity_from_description(*args, **kwargs)
    assert expected == actual
