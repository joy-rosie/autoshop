import getpass
import re
import time
import urllib.parse
from collections import namedtuple
from typing import NoReturn, Optional

from autoshop.environment import get as get_env
from autoshop.selenium import (
    by,
    wait_and_check_exists,
    wait_and_click,
    wait_and_delete_and_send_keys,
    wait_and_execute_click,
    wait_and_get,
    wait_and_get_all,
    wait_and_send_keys,
)
from autoshop.util.logging import logger as get_logger
from autoshop.util.typing import WebDriver, WebElement

__all__ = [
    "Quantity",
    "add_food_to_basket",
    "add_food_to_basket_with_retry",
    "checkout",
    "empty_basket",
    "get_food_elements",
    "get_food_url",
    "get_image_url",
    "get_price",
    "get_quantity_from_description",
    "go_to_delivery_slots",
    "go_to_orders",
    "login",
    "make_changes_to_nth_order",
    "pay",
]


URL_LOGIN_DEFAULT = "https://www.tesco.com/account/login/en-GB?from=/"
EMAIL_LOGIN = "EMAIL_LOGIN"
PASSWORD_LOGIN = "PASSWORD_LOGIN"

URL_ORDERS = "https://www.tesco.com/groceries/en-GB/orders"
URL_DELIVERY_SLOTS = "https://www.tesco.com/groceries/en-GB/slots/delivery"

LOGGER = get_logger(__name__)


def login(
    driver: WebDriver,
    url: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
) -> NoReturn:
    if url is None:
        url = URL_LOGIN_DEFAULT

    if email is None:
        email = get_env(key=EMAIL_LOGIN)

    if password is None:
        password = get_env(key=PASSWORD_LOGIN)

    driver.get(url)

    LOGGER.info(f"Logging into via {url=} with {email=}")

    xpath_cookies_accept = "//button[@type='submit']//span[text()='Accept all cookies']"
    wait_and_execute_click(
        driver=driver,
        value=xpath_cookies_accept,
    )

    time.sleep(5)

    xpath_email = "//input[@id='email']"
    _ = wait_and_send_keys(
        driver=driver,
        value=xpath_email,
        keys=email,
    )

    xpath_next = "//button/span[text()='Next']"
    next_exists = wait_and_check_exists(
        driver=driver,
        value=xpath_next,
    )
    if next_exists:
        xpath_remember_me = "//input[@id='rememberMe']"
        _ = wait_and_click(
            driver=driver,
            value=xpath_remember_me,
        )
        _ = wait_and_execute_click(
            driver=driver,
            value=xpath_next,
        )
    else:
        xpath_remember_me = "//input[@id='rememberMe']"
        _ = wait_and_click(
            driver=driver,
            value=xpath_remember_me,
        )

    xpath_password = "//input[@id='password']"
    _ = wait_and_send_keys(
        driver=driver,
        value=xpath_password,
        keys=password,
        log=False,
    )

    xpath_sign_in = "//button[@id='signin-button']"
    _ = wait_and_click(
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
    driver: WebDriver,
) -> list[WebElement]:
    try:
        elements = wait_and_get_all(
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
    elements = [element for element in elements if element.children()[0].text == ""]

    # Don't want the sponsored items
    elements = [
        element
        for element in elements
        if not (
            element.find_element(by=by.XPATH, value="..").text.startswith("Sponsored")
        )
    ]
    return elements


def get_price(
    element: WebElement,
) -> float:
    try:
        return float(
            element.find_element(
                by=by.XPATH,
                value=(
                    ".//p[contains(text(), '£') "
                    "and not(contains(text(), '/each')) "
                    "and @class != 'product-info-message']"
                ),
            ).text.replace("£", "")
        )
    except KeyboardInterrupt as e:
        raise e
    except Exception:
        return float("nan")


X = "x"
PACK = "pack"
PATTERN_MULTIPLIER = f"(?P<multiplier>[0-9]+)\s*(?P<x_pack>{X}|{PACK})\s*"
PATTERN_AMOUNT = "?P<amount>[0-9]+[.]?[0-9]*"
PATTERN_UNIT = f"?P<unit>kg|grams|gram|g|litres|litre|ltr|l|ml|{PACK}"
PATTERN_SUFFIX = "(ce|minimum|\.\.)"
PATTERN_DESCRIPTION = re.compile(
    pattern=f"\s+({PATTERN_MULTIPLIER})?({PATTERN_AMOUNT})\s*({PATTERN_UNIT})\s*{PATTERN_SUFFIX}?\s*$",
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
    groups = search.groupdict()
    # We want to ignore if pack is in the first bit because there is another unit after
    multiplier = (
        1.0
        if groups["multiplier"] is None or PACK in groups["x_pack"].casefold()
        else float(groups["multiplier"])
    )
    return Quantity(
        amount=multiplier * float(groups["amount"]),
        unit="medium" if (unit := groups["unit"].casefold()) == PACK else unit,
    )


def validate_multiplier(value: Optional[str]) -> float:
    return (
        1.0
        if value is None or PACK in value
        else float(value.casefold().replace(X, "").strip())
    )


def get_image_url(
    value: Optional[WebElement],
) -> str:
    if value is None:
        return "NA"
    try:
        return (
            value.find_element(by=by.XPATH, value=".//img")
            .get_attribute("srcset")
            .split(" ")[0]
        )
    except Exception:
        return "NA"


def go_to_orders(
    driver: WebDriver,
) -> NoReturn:
    time.sleep(1)
    driver.get(URL_ORDERS)


def go_to_delivery_slots(
    driver: WebDriver,
) -> NoReturn:
    time.sleep(1)
    driver.get(URL_DELIVERY_SLOTS)


def make_changes_to_nth_order(
    driver: WebDriver,
    n: int,
) -> NoReturn:
    go_to_orders(driver=driver)
    xpath_make_changes = "//span[text()='Make changes']/.."
    elements = wait_and_get_all(
        driver=driver,
        value=xpath_make_changes,
    )

    # Need to make this a bit better
    elements[n].click()


def empty_basket(
    driver: WebDriver,
) -> NoReturn:
    xpath_view_full_basket = "//a//span[text()='View full basket']/../.."
    wait_and_click(driver=driver, value=xpath_view_full_basket)

    xpath_your_basket_empty = "//h3[text()='Your basket is empty']"
    basket_empty = wait_and_check_exists(
        driver=driver,
        value=xpath_your_basket_empty,
    )
    if not basket_empty:
        xpath_empty_basket = "//button//span[text()='Empty Basket']/.."
        wait_and_execute_click(driver=driver, value=xpath_empty_basket)

        xpath_empty_button = "//button//span[text()='Empty basket']/.."
        wait_and_click(driver=driver, value=xpath_empty_button)

        _ = wait_and_get(driver=driver, value=xpath_your_basket_empty)


def add_food_to_basket(
    driver: WebDriver,
    url: str,
    amount: int,
    info: str,
    xpath_check_done: Optional[str] = None,
) -> NoReturn:
    xpath_product_input_amount = "//input[@type='number']"
    xpath_add = "//span[text()='Add']/.."
    if xpath_check_done is None:
        xpath_check_done = "//span[text()='Checkout to confirm changes']"

    LOGGER.debug(f"Trying to add {amount=} for {url=}, {info}")
    driver.get(url)
    time.sleep(2)
    wait_and_delete_and_send_keys(
        driver=driver,
        value=xpath_product_input_amount,
        keys=amount,
    )
    time.sleep(1)
    wait_and_click(driver=driver, value=xpath_add)
    # This checks that the action has been done
    _ = wait_and_get(driver=driver, value=xpath_check_done)


def check_if_out_of_stock(
    driver: WebDriver,
) -> bool:
    try:
        xpath_out_of_stock = "//div[contains(text(),'currently out of stock')]"
        wait_and_get(
            driver=driver,
            value=xpath_out_of_stock,
            by=by.XPATH,
            timeout=1,
        )
        return True
    except Exception:
        return False


def add_food_to_basket_with_retry(
    driver: WebDriver,
    url: str,
    amount: int,
    info: str,
    max_retries: Optional[int] = None,
) -> NoReturn:
    if max_retries is None:
        max_retries = 0

    num_retries = -1
    done = False
    while not done:
        try:
            num_retries += 1
            add_food_to_basket(
                driver=driver,
                url=url,
                amount=amount,
                info=info,
            )
            done = True
        except Exception as exception:
            if check_if_out_of_stock(driver=driver):
                LOGGER.warning(f"Out of stock - {info}")
                return
            if num_retries >= max_retries:
                LOGGER.error(f"Failed - {info}, {exception=}")
                done = True
            time.sleep(1)
            LOGGER.debug("Refreshing")
            driver.refresh()


def checkout(
    driver: WebDriver,
    to_confirm_changes: bool = False,
) -> NoReturn:
    if to_confirm_changes:
        try:
            checkout_str = "Check out to confirm changes"
            xpath_span_checkout = f"//span[text()='{checkout_str}']"
            wait_and_execute_click(driver=driver, value=xpath_span_checkout)
        except TimeoutError:
            checkout_str = "Checkout to confirm changes"
            xpath_span_checkout = f"//span[text()='{checkout_str}']"
            wait_and_execute_click(driver=driver, value=xpath_span_checkout)

        xpath_a_continue_checkout = "//a//span[text()='Continue checkout']"
        wait_and_execute_click(driver=driver, value=xpath_a_continue_checkout)
        wait_and_execute_click(driver=driver, value=xpath_a_continue_checkout)

        xpath_confirm_order = "//button//span[text()='Confirm order']"
        wait_and_execute_click(driver=driver, value=xpath_confirm_order)
    else:
        checkout_str = "Checkout"
        xpath_a_checkout = f"//a//span[text()='{checkout_str}']/.."
        wait_and_execute_click(driver=driver, value=xpath_a_checkout)

        checkout_again_str = "Check out"
        xpath_checkout_again = f"//a//span[text()='{checkout_again_str}']/.."
        wait_and_execute_click(driver=driver, value=xpath_checkout_again)

        xpath_a_continue_checkout = "//a//span[text()='Continue checkout']/.."
        wait_and_execute_click(driver=driver, value=xpath_a_continue_checkout)

        xpath_span_continue_to_payment = (
            "//button//span[text()='Continue to payment']/.."
        )
        wait_and_execute_click(driver=driver, value=xpath_span_continue_to_payment)


def pay(
    driver: WebDriver,
    cvc: bool = False,
) -> NoReturn:
    driver.switch_to.frame("bounty-iframe")
    if cvc:
        xpath_cvc = "//input[@id='card-cvc']"
        wait_and_send_keys(
            driver=driver,
            value=xpath_cvc,
            keys=getpass.getpass(),
            log=False,
        )

    xpath_confirm_order = "//input[@value='Confirm order']"
    wait_and_click(driver=driver, value=xpath_confirm_order)
