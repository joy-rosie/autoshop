import chromedriver_binary
import undetected_chromedriver

from autoshop.util.typing import WebDriver as TypeDriver


def driver() -> TypeDriver:
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
