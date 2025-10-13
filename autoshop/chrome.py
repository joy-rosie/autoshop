import undetected_chromedriver

from autoshop.util.typing import WebDriver

__all__ = ["driver"]


def driver() -> WebDriver:
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
    driver = undetected_chromedriver.Chrome(options=options)
    driver.delete_all_cookies()
    return driver
