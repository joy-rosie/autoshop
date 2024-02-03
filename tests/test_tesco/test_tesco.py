import pytest

import autoshop


TEST_URL = "https://www.tesco.com/groceries/en-GB/products/254656543"


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
        (
            [],
            dict(description="Cauldron 6 Lincolnshire Sausages 276G"),
            autoshop.tesco.Quantity(amount=276, unit="g"),
        ),
    ],
)
def test_get_quantity_from_description(args, kwargs, expected):
    actual = autoshop.tesco.get_quantity_from_description(*args, **kwargs)
    assert expected == actual


@pytest.fixture(scope="module")
def driver() -> autoshop.typing.WebDriver:
    yield autoshop.chrome.driver()


@pytest.mark.integration
def test_login(driver):
    autoshop.tesco.login(driver=driver)
    element = autoshop.selenium.wait_and_get(
        driver=driver,
        value="//h1[contains(text(), 'Good morning') or contains(text(), ', here’s your account overview')]",
    )
    assert element is not None


@pytest.fixture(scope="module")
def driver_logged_in(driver: autoshop.typing.WebDriver) -> autoshop.typing.WebDriver:
    autoshop.tesco.login(driver=driver)
    yield driver


@pytest.mark.integration
def test_go_to_orders(driver_logged_in):
    autoshop.tesco.go_to_orders(driver=driver_logged_in)
    element = autoshop.selenium.wait_and_get_all(
        driver=driver_logged_in,
        value="//h1[text()='My orders']",
    )
    assert element is not None
    

@pytest.fixture
def driver_empty_basket(driver_logged_in: autoshop.typing.WebDriver) -> autoshop.typing.WebDriver:
    driver_logged_in.get(TEST_URL)
    autoshop.tesco.empty_basket(driver=driver_logged_in)
    yield driver_logged_in
    autoshop.tesco.empty_basket(driver=driver_logged_in)


@pytest.mark.integration
def test_add_food_to_basket(driver_empty_basket):
    url = TEST_URL
    xpath_check_done = f"//div//ul//li//a[@href='{url}']"
    amount = 2
    autoshop.tesco.add_food_to_basket(
        driver=driver_empty_basket,
        url=url,
        amount=amount,
        info="test",
        xpath_check_done=xpath_check_done,
    )
    xpath_quantity = f"{xpath_check_done}/../..//h5[text()='{amount}']"
    element = autoshop.selenium.wait_and_get(
        driver=driver_empty_basket,
        value=xpath_quantity,
    )
    assert element is not None
