from collections import namedtuple
import getpass
import re
import time
from typing import NoReturn, Optional
import urllib.parse

import autoshop

URL_LOGIN_DEFAULT = "https://www.tesco.com/account/login/en-GB?from=/"
EMAIL_LOGIN = "EMAIL_LOGIN"
PASSWORD_LOGIN = "PASSWORD_LOGIN"

URL_ORDERS = "https://www.tesco.com/groceries/en-GB/orders"
URL_DELIVERY_SLOTS =  "https://www.tesco.com/groceries/en-GB/slots/delivery"

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
    autoshop.selenium.wait_and_execute_click(
        driver=driver,
        value=xpath_cookies_accept,
    )

    time.sleep(5)

    xpath_email = "//input[@id='email']"
    _ = autoshop.selenium.wait_and_send_keys(
        driver=driver,
        value=xpath_email,
        keys=email,
    )

    xpath_password = "//input[@id='password']"
    _ = autoshop.selenium.wait_and_send_keys(
        driver=driver,
        value=xpath_password,
        keys=password,
        log=False,
    )

    xpath_remember_me = "//input[@id='rememberMe']"
    _ = autoshop.selenium.wait_and_click(
        driver=driver,
        value=xpath_remember_me,
    )

    xpath_sign_in = "//button[@id='signin-button']"
    _ = autoshop.selenium.wait_and_click(
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
    elements = [element for element in elements if element.children()[0].text == ""]

    # Don't want the sponsored items
    elements = [
        element
        for element in elements
        if not (
            element.find_element(
                by=autoshop.selenium.by.XPATH, value=".."
            ).text.startswith("Sponsored")
        )
    ]
    return elements


def get_price(
    element: autoshop.typing.WebElement,
) -> float:
    try:
        return float(
            element.find_element(
                by=autoshop.selenium.by.XPATH,
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
    value: Optional[autoshop.typing.WebElement],
) -> str:
    if value is None:
        return "NA"
    try:
        return (
            value.find_element(by=autoshop.selenium.by.XPATH, value=".//img")
            .get_attribute("srcset")
            .split(" ")[0]
        )
    except Exception:
        return "NA"


def go_to_orders(
    driver: autoshop.typing.WebDriver,
) -> NoReturn:
    time.sleep(1)
    driver.get(URL_ORDERS)


def go_to_delivery_slots(
    driver: autoshop.typing.WebDriver,
) -> NoReturn:
    time.sleep(1)
    driver.get(URL_DELIVERY_SLOTS)

    
def make_changes_to_nth_order(
    driver: autoshop.typing.WebDriver,
    n: int,
) -> NoReturn:
    go_to_orders(driver=driver)
    xpath_make_changes = "//span[text()='Make changes']/.."
    elements = autoshop.selenium.wait_and_get_all(
        driver=driver,
        value=xpath_make_changes,
    )

    # Need to make this a bit better
    elements[n].click()


def empty_basket(
    driver: autoshop.typing.WebDriver,
) -> NoReturn:
    xpath_view_full_basket = "//a//span[text()='View full basket']/../.."
    autoshop.selenium.wait_and_click(driver=driver, value=xpath_view_full_basket)
    
    xpath_your_basket_empty = "//h3[text()='Your basket is empty']"
    basket_empty = autoshop.selenium.wait_and_check_exists(
        driver=driver,
        value=xpath_your_basket_empty,
    )
    if not basket_empty:
        xpath_empty_basket = "//button//span[text()='Empty Basket']/.."
        autoshop.selenium.wait_and_execute_click(driver=driver, value=xpath_empty_basket)

        xpath_empty_button = "//button//span[text()='Empty basket']/.."
        autoshop.selenium.wait_and_click(driver=driver, value=xpath_empty_button)

        _ = autoshop.selenium.wait_and_get(driver=driver, value=xpath_your_basket_empty)


def add_food_to_basket(
    driver: autoshop.typing.WebDriver,
    url: str,
    amount: int,
    info: str,
    xpath_check_done: Optional[str] = None,
) -> NoReturn:
    xpath_product_input_amount = "//input[@type='number']"
    xpath_add = "//span[text()='Add']/.."
    if xpath_check_done is None:
        xpath_check_done = "//span[text()='Checkout to confirm changes']"

    autoshop.logger.debug(f"Trying to add {amount=} for {url=}, {info}")
    driver.get(url)
    time.sleep(1)
    autoshop.selenium.wait_and_delete_and_send_keys(
        driver=driver,
        value=xpath_product_input_amount,
        keys=amount,
    )
    time.sleep(1)
    autoshop.selenium.wait_and_click(driver=driver, value=xpath_add)
    # This checks that the action has been done
    _ = autoshop.selenium.wait_and_get(driver=driver, value=xpath_check_done)



def check_if_out_of_stock(
    driver: autoshop.typing.WebDriver,
) -> bool:
    try:
        xpath_out_of_stock = "//div[contains(text(),'currently out of stock')]"
        autoshop.selenium.wait_and_get(
            driver=driver,
            value=xpath_out_of_stock,
            by=autoshop.selenium.by.XPATH,
            timeout=1,
        )
        return True
    except:
        return False


def add_food_to_basket_with_retry(
    driver: autoshop.typing.WebDriver,
    url: str,
    amount: int,
    info: str,
    max_retries: Optional[int] = None,
) -> NoReturn:
    if max_retries is None:
        max_retries = 1
    
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
                autoshop.logger.warning(f"Out of stock - {info}")
                return
            if num_retries >= max_retries:
                autoshop.logger.error(f"Failed - {info}, {exception=}")
                done = True
            time.sleep(1)
            autoshop.logger.debug("Refreshing")
            driver.refresh()
        

def checkout(
    driver: autoshop.typing.WebDriver,
    to_confirm_changes: bool = False,
) -> NoReturn:
    checkout_str = "Checkout" + (" to confirm changes" if to_confirm_changes else "")
    xpath_span_checkout = f"//span[text()='{checkout_str}']"
    autoshop.selenium.wait_and_execute_click(driver=driver, value=xpath_span_checkout)

    xpath_a_checkout = f"//a//span[text()='{checkout_str}']"
    autoshop.selenium.wait_and_execute_click(driver=driver, value=xpath_a_checkout)
    
    if to_confirm_changes:
        xpath_a_continue_checkout = "//button//span[text()='Continue checkout']"
        autoshop.selenium.wait_and_execute_click(driver=driver, value=xpath_a_continue_checkout)
    else:
        xpath_a_continue_checkout = "//a//span[text()='Continue checkout']"
        autoshop.selenium.wait_and_execute_click(driver=driver, value=xpath_a_continue_checkout)

        xpath_span_continue_to_payment = "//span[text()='Continue to payment']"
        autoshop.selenium.wait_and_execute_click(driver=driver, value=xpath_span_continue_to_payment)


def pay(
    driver: autoshop.typing.WebDriver,
) -> NoReturn:
    driver.switch_to.frame("bounty-iframe")

    xpath_cvc = "//input[@id='card-cvc']"
    autoshop.selenium.wait_and_send_keys(
        driver=driver, 
        value=xpath_cvc,
        keys=getpass.getpass(),
        log=False,
    )

    xpath_confirm_order = "//input[@value='Confirm order']"
    autoshop.selenium.wait_and_click(driver=driver, value=xpath_confirm_order)
