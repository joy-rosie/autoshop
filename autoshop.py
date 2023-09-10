import getpass
import logging
import sys
from typing import Optional, NoReturn
import time

import chromedriver_binary
import undetected_chromedriver
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import requests
from dotenv import dotenv_values


environment_variables = dotenv_values(".env")

logger = logging.Logger(__name__)

formatter = logging.Formatter(
    fmt="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

file_handler = logging.FileHandler("auto-shop.log", mode="w")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler(stream=sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


URL_LOGIN = "https://www.tesco.com/account/login/en-GB?from=/"
EMAIL_LOGIN = environment_variables["EMAIL_LOGIN"]
PASSWORD_LOGIN = environment_variables["PASSWORD_LOGIN"]
TIMEOUT = 10


def wait_and_get(
    driver: webdriver.Chrome,
    value: str,
    by: Optional[By] = None,
    timeout: Optional[int] = None,
    log: Optional[bool] = None,
) -> WebElement:
    
    if by is None:
        by = By.XPATH
        
    if timeout is None:
        timeout = TIMEOUT
        
    if log is None:
        log = True
        
    if log:
        logger.debug(f"{by=}, {value=}, {timeout=}")
    
    wait = expected_conditions.presence_of_element_located((by, value))
    WebDriverWait(driver, timeout).until(wait)
    
    if log:
        logger.debug(f"Waited for: {by=}, {value=}")

    time.sleep(1)

    return driver.find_element(by=by, value=value)


def wait_and_get_all(
    driver: webdriver.Chrome,
    value: str,
    by: Optional[By] = None,
    timeout: Optional[int] = None,
    log: Optional[bool] = None,
) -> WebElement:
    
    if by is None:
        by = By.XPATH
        
    if timeout is None:
        timeout = TIMEOUT
        
    if log is None:
        log = True
        
    if log:
        logger.debug(f"{by=}, {value=}, {timeout=}")
    
    wait = expected_conditions.presence_of_element_located((by, value))
    WebDriverWait(driver, timeout).until(wait)
    
    if log:
        logger.debug(f"Waited for: {by=}, {value=}")

    time.sleep(1)

    return driver.find_elements(by=by, value=value)
    

def wait_and_click(
    driver: webdriver.Chrome,
    value: str,
    by: Optional[By] = None,
    timeout: Optional[int] = None,
    log: Optional[bool] = None,
) -> NoReturn:
    
    element = wait_and_get(driver=driver, value=value, by=by, timeout=timeout, log=log)
    element.click()
    
    if log is None:
        log = True
        
    if log:
        logger.debug(f"Clicked: {value=}")


def wait_and_execute_click(
    driver: webdriver.Chrome,
    value: str,
    by: Optional[By] = None,
    timeout: Optional[int] = None,
    log: Optional[bool] = None,
) -> NoReturn:
    
    element = wait_and_get(driver=driver, value=value, by=by, timeout=timeout, log=log)
    driver.execute_script("arguments[0].click();", element)
    
    if log is None:
        log = True
        
    if log:
        logger.debug(f"Executed click via script: {value=}")
    
    
def wait_and_send_keys(
    driver: webdriver.Chrome,
    value: str,
    keys: str,
    by: Optional[By] = None,
    timeout: Optional[int] = None,
    log: Optional[bool] = None,
) -> NoReturn:
    
    element = wait_and_get(driver=driver, value=value, by=by, timeout=timeout, log=log)
    element.send_keys(keys)
    
    if log is None:
        log = True
        
    if log:
        logger.debug(f"Sent keys: {keys=} into {value=}")


def wait_and_select_all_and_send_keys(
    driver: webdriver.Chrome,
    value: str,
    keys: str,
    by: Optional[By] = None,
    timeout: Optional[int] = None,
    log: Optional[bool] = None,
) -> NoReturn:
    
    element = wait_and_get(driver=driver, value=value, by=by, timeout=timeout)
    element.send_keys(Keys.CONTROL + "a")
    element.send_keys(keys)
    
    if log is None:
        log = True
        
    if log:
        logger.debug(f"Selected all and then sent keys: {keys=} into {value=}")
        
        
def wait_and_send_keys_and_delete(
    driver: webdriver.Chrome,
    value: str,
    keys: str,
    by: Optional[By] = None,
    timeout: Optional[int] = None,
    log: Optional[bool] = None,
) -> NoReturn:
    
    element = wait_and_get(driver=driver, value=value, by=by, timeout=timeout)
    
    element.send_keys(keys)
    element.send_keys(Keys.DELETE)
    
    if log is None:
        log = True
        
    if log:
        logger.debug(f"Selected all and then sent keys: {keys=} into {value=}")


def get_driver() -> undetected_chromedriver.Chrome:
    options = undetected_chromedriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--password-store=basic")
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        },
    )
    return undetected_chromedriver.Chrome(options=options)


def login() -> undetected_chromedriver.Chrome:
    driver = get_driver()
    
    driver.get(URL_LOGIN)
    
    xpath_cookies_accept = "//button[@type='submit']//span[text()='Accept all cookies']"
    wait_and_click(driver=driver, value=xpath_cookies_accept)
    
    time.sleep(5)

    xpath_email = "//input[@id='email']"
    element_email = wait_and_send_keys(driver=driver, value=xpath_email, keys=EMAIL_LOGIN)

    xpath_password = "//input[@id='password']"
    element_email = wait_and_send_keys(driver=driver, value=xpath_password, keys=PASSWORD_LOGIN, log=False)

    xpath_sign_in = "//button[@id='signin-button']"
    element_sign_in = wait_and_click(driver=driver, value=xpath_sign_in)
    logger.debug(f"Clicked {xpath_sign_in=}")
    return driver


def get_groceries(google_api_key: Optional[str] = None) -> dict:
    if google_api_key is None:
        google_api_key = environment_variables["GOOGLE_API_KEY"]
    response = requests.get(f"https://sheets.googleapis.com/v4/spreadsheets/1qMt1jKFf3OVILmA-MsQ8Ga-8vsYLsCX0ky00zairf9M/values/groceries!A1:G80?key={google_api_key}")
    return response.json()


def get_all_food(google_api_key: Optional[str] = None) -> dict:
    if google_api_key is None:
        google_api_key = environment_variables["GOOGLE_API_KEY"]
    response = requests.get(f"https://sheets.googleapis.com/v4/spreadsheets/1qMt1jKFf3OVILmA-MsQ8Ga-8vsYLsCX0ky00zairf9M/values/food!A1:F1000?key={google_api_key}")
    return response.json()
