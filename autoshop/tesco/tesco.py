from collections import namedtuple
import re
import time
from typing import NoReturn, Optional

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


PATTERN_DESCRIPTION = re.compile(pattern="\s+((\d+)\s*x\s*)?(\d+)\s*(grams|gram|g|litres|litre|ltr|l)", flags=re.IGNORECASE)
Quantity = namedtuple("Quantity", field_names=["amount", "unit"])


def get_quantity_from_description(description: str) -> Quantity:
    groups = (
        re.search(
            pattern=PATTERN_DESCRIPTION,
            string=description,
        )
        .groups()
    )
    multiplier = 1 if groups[0] is None else groups[0]
    return Quantity(amount=float(multiplier) * float(groups[2]), unit=groups[-1].lower())
