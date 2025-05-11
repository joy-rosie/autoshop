import time
from typing import NoReturn, Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from autoshop.util.logging import logger as get_logger
from autoshop.util.typing import WebDriver, WebElement

__all__ = [
    "wait_and_check_exists",
    "wait_and_click",
    "wait_and_delete_and_send_keys",
    "wait_and_execute_click",
    "wait_and_get",
    "wait_and_get_all",
    "wait_and_select_all_and_send_keys",
    "wait_and_send_keys",
]

TIMEOUT_DEFAULT = 10
LOGGER = get_logger(__name__)


def wait_and_check_exists(
    driver: WebDriver,
    value: str,
    by: Optional[By] = None,
    timeout: Optional[int] = None,
    log: Optional[bool] = None,
) -> bool:
    """
    Waits and checks if element exists.
    """

    if by is None:
        by = By.XPATH

    if timeout is None:
        timeout = TIMEOUT_DEFAULT

    if log is None:
        log = True

    if log:
        LOGGER.debug(f"{wait_and_check_exists.__name__} {by=}, {value=}, {timeout=}")

    try:
        wait = expected_conditions.presence_of_element_located((by, value))
        WebDriverWait(driver, timeout).until(wait)
    except (NoSuchElementException, TimeoutException):
        return False
    return True


def wait_and_get(
    driver: WebDriver,
    value: str,
    by: Optional[By] = None,
    timeout: Optional[int] = None,
    log: Optional[bool] = None,
) -> WebElement:
    """
    Waits and gets the first element found.
    """

    if by is None:
        by = By.XPATH

    if timeout is None:
        timeout = TIMEOUT_DEFAULT

    if log is None:
        log = True

    if log:
        LOGGER.debug(f"{wait_and_get.__name__} {by=}, {value=}, {timeout=}")

    wait = expected_conditions.presence_of_element_located((by, value))
    WebDriverWait(driver, timeout).until(wait)

    if log:
        LOGGER.debug(f"Waited for: {by=}, {value=}")

    time.sleep(1)

    return driver.find_element(by=by, value=value)


def wait_and_get_all(
    driver: WebDriver,
    value: str,
    by: Optional[By] = None,
    timeout: Optional[int] = None,
    log: Optional[bool] = None,
) -> list[WebElement]:
    """
    Waits and gets all elements found.
    """

    if by is None:
        by = By.XPATH

    if timeout is None:
        timeout = TIMEOUT_DEFAULT

    if log is None:
        log = True

    if log:
        LOGGER.debug(f"{wait_and_get_all.__name__} {by=}, {value=}, {timeout=}")

    wait = expected_conditions.presence_of_element_located((by, value))
    WebDriverWait(driver, timeout).until(wait)

    if log:
        LOGGER.debug(f"Waited to get all for: {by=}, {value=}")

    time.sleep(1)

    return driver.find_elements(by=by, value=value)


def wait_and_click(
    driver: WebDriver,
    value: str,
    by: Optional[By] = None,
    timeout: Optional[int] = None,
    log: Optional[bool] = None,
) -> NoReturn:
    """
    Waits and clicks the first element found via itself.
    """

    element = wait_and_get(driver=driver, value=value, by=by, timeout=timeout, log=log)
    element.click()

    if log is None:
        log = True

    if log:
        LOGGER.debug(f"{wait_and_click.__name__} {value=}")


def wait_and_execute_click(
    driver: WebDriver,
    value: str,
    by: Optional[By] = None,
    timeout: Optional[int] = None,
    log: Optional[bool] = None,
) -> NoReturn:
    """
    Waits and clicks the first element found via javascript.
    """

    element = wait_and_get(driver=driver, value=value, by=by, timeout=timeout, log=log)
    driver.execute_script("arguments[0].click();", element)

    if log is None:
        log = True

    if log:
        LOGGER.debug(f"wait_and_execute_click via script {value=}")


def wait_and_send_keys(
    driver: WebDriver,
    value: str,
    keys: str,
    by: Optional[By] = None,
    timeout: Optional[int] = None,
    log: Optional[bool] = None,
) -> NoReturn:
    """
    Waits and sends keys to the first element found.
    """

    element = wait_and_get(driver=driver, value=value, by=by, timeout=timeout, log=log)
    element.send_keys(keys)

    if log is None:
        log = True

    if log:
        LOGGER.debug(f"{wait_and_send_keys.__name__}: {keys=} into {value=}")


def wait_and_select_all_and_send_keys(
    driver: WebDriver,
    value: str,
    keys: str,
    by: Optional[By] = None,
    timeout: Optional[int] = None,
    log: Optional[bool] = None,
) -> NoReturn:
    """
    Waits, selects all in the first element found and then sends keys to the same element.
    """

    element = wait_and_get(driver=driver, value=value, by=by, timeout=timeout)
    element.send_keys(Keys.CONTROL + "a")
    element.send_keys(keys)

    if log is None:
        log = True

    if log:
        LOGGER.debug(
            f"{wait_and_select_all_and_send_keys.__name__}: {keys=} into {value=}"
        )


def wait_and_delete_and_send_keys(
    driver: WebDriver,
    value: str,
    keys: str,
    by: Optional[By] = None,
    timeout: Optional[int] = None,
    log: Optional[bool] = None,
) -> NoReturn:
    """
    Waits, sends keys to the first element found then sends a single delete to the same element.
    """

    element = wait_and_get(driver=driver, value=value, by=by, timeout=timeout)

    for _ in range(5):
        element.send_keys(Keys.DELETE)
    element.send_keys(keys)

    if log is None:
        log = True

    if log:
        LOGGER.debug(f"{wait_and_delete_and_send_keys.__name__}: {keys=}, {value=}")
