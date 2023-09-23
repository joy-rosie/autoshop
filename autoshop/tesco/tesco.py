from collections import namedtuple
import re
import time
from typing import NoReturn, Optional
import urllib.parse

import autoshop

URL_LOGIN_DEFAULT = "https://www.tesco.com/account/login/en-GB?from=/"
EMAIL_LOGIN = "EMAIL_LOGIN"
PASSWORD_LOGIN = "PASSWORD_LOGIN"

LOGGER = autoshop.logging.logger(__name__)


def login(
    driver: autoshop.typing.WebDriver,
    url: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
) -> NoReturn:
    
    if url is None:
        url = URL_LOGIN_DEFAULT
        
    if email is None:
        email = autoshop.env.get(key=EMAIL_LOGIN)
        
    if password is None:
        password = autoshop.env.get(key=PASSWORD_LOGIN)
        
    driver.get(url)
    
    LOGGER.info(f"Logging into via {url=} with {email=}")
    
    xpath_cookies_accept = "//button[@type='submit']//span[text()='Accept all cookies']"
    autoshop.selenium.wait_and_click(
        driver=driver,
        value=xpath_cookies_accept,
    )
    
    time.sleep(5)

    xpath_email = "//input[@id='email']"
    element_email = autoshop.selenium.wait_and_send_keys(
        driver=driver,
        value=xpath_email, 
        keys=email,
    )

    xpath_password = "//input[@id='password']"
    element_email = autoshop.selenium.wait_and_send_keys(
        driver=driver,
        value=xpath_password,
        keys=password,
        log=False,
    )

    xpath_sign_in = "//button[@id='signin-button']"
    element_sign_in = autoshop.selenium.wait_and_click(
        driver=driver,
        value=xpath_sign_in,
    )
    LOGGER.debug(f"Clicked {xpath_sign_in=}")
    
    return driver


URL_FOOD_TEMPLATE = "https://www.tesco.com/groceries/en-GB/search?query={query}&page={page}&count={count}"


def get_food_url(
    query: str,
    page: int = 1,
    count: int = 24,
    url_template: str = URL_FOOD_TEMPLATE,
) -> str:
    return url_template.format(
        query=urllib.parse.quote_plus(query),
        page=page,
        count=count,
    )


def get_food_elements(
    driver: autoshop.typing.WebDriver,
) -> list[autoshop.typing.WebElement]:
    try:
        elements = autoshop.selenium.wait_and_get_all(
            driver=driver,
            value=(
                "//ul[@class = 'product-list grid']"
                "//li"
                "//a[starts-with(@href, '/groceries/en-GB/products/')]"
            ),
        )
    except KeyboardInterrupt as e:
        raise e
    except Exception:
        elements = []

    # Don't want the elements where the text is empty
    elements = [
        element
        for element in elements 
        if element.children()[0].text == ""
    ]

    # Don't want the sponsored items
    elements = [
        element
        for element in elements 
        if not (
            element
            .find_element(by=autoshop.selenium.by.XPATH, value="..")
            .text.startswith("Sponsored")
        )
    ]
    return elements


def get_price(
    element: autoshop.typing.WebElement,
) -> float:
    try:
        return float(
            element
            .find_element(
                by=autoshop.selenium.by.XPATH, 
                value=(
                    ".//p[contains(text(), '£') "
                    "and not(contains(text(), '/each')) "
                    "and @class != 'product-info-message']"
                ),
            )
            .text.replace("£", "")
        )
    except KeyboardInterrupt as e:
        raise e
    except Exception:
        return float("nan")


PATTERN_DESCRIPTION = re.compile(
    pattern="\s+([0-9]+\s*(x|pack)\s*)?([0-9]+[.]?[0-9]*)\s*(kg|grams|gram|g|litres|litre|ltr|l|ml|pack).*", 
    flags=re.IGNORECASE,
)
Quantity = namedtuple("Quantity", field_names=["amount", "unit"])
QUANTITY_NA = Quantity(amount=float("nan"), unit=None)


def get_quantity_from_description(description: Optional[str]) -> Quantity:
    if description is None:
        return QUANTITY_NA
    search = re.search(pattern=PATTERN_DESCRIPTION, string=description)
    if search is None:
        return QUANTITY_NA
    groups = search.groups()
    multiplier = validate_multiplier(groups[0])
    return Quantity(amount=multiplier * float(groups[2]), unit=groups[3].casefold())


def validate_multiplier(value: Optional[str]) -> float:
    return (
        1. if value is None 
        else float(
            value.casefold()
            .replace("x", "")
            .replace("pack", "")
            .strip()
        )
    )


def get_image_url(
    value: Optional[autoshop.typing.WebElement],
) -> str:
    if value is None:
        return "NA"
    try:
        return (
            value
            .find_element(by=autoshop.selenium.by.XPATH, value=".//img")
            .get_attribute("srcset")
            .split(" ")[0]
        )
    except Exception:
        return "NA"
