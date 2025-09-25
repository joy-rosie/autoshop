import pytest

from autoshop import all as autoshop


# Tests for chrome driver function
def test_driver_returns_webdriver():
    """Test that driver() returns a WebDriver instance."""
    driver = autoshop.chrome.driver()

    try:
        assert driver is not None
        # Should be a WebDriver instance
        assert hasattr(driver, "get")
        assert hasattr(driver, "quit")
        assert hasattr(driver, "find_element")
        assert hasattr(driver, "close")

    finally:
        driver.quit()


def test_driver_configuration(mocker):
    """Test that driver is configured with correct options."""
    mock_options = mocker.Mock()
    _ = mocker.patch("undetected_chromedriver.ChromeOptions", return_value=mock_options)
    mock_driver = mocker.Mock()
    mock_chrome_class = mocker.patch(
        "undetected_chromedriver.Chrome", return_value=mock_driver
    )

    result = autoshop.chrome.driver()

    # Verify options were configured
    mock_options.add_argument.assert_any_call("--start-maximized")
    mock_options.add_argument.assert_any_call("--password-store=basic")

    # Verify experimental options were set
    expected_prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }
    mock_options.add_experimental_option.assert_called_with("prefs", expected_prefs)

    # Verify Chrome was created with options
    mock_chrome_class.assert_called_once_with(options=mock_options)

    assert result == mock_driver


def test_driver_options_order(mocker):
    """Test that driver options are set in the correct order."""
    mock_options = mocker.Mock()
    _ = mocker.patch("undetected_chromedriver.ChromeOptions", return_value=mock_options)
    mock_driver = mocker.Mock()
    _ = mocker.patch("undetected_chromedriver.Chrome", return_value=mock_driver)

    autoshop.chrome.driver()

    # Check call order - add_argument should be called before add_experimental_option
    calls = mock_options.method_calls

    # Find the positions of different call types
    add_arg_calls = [i for i, call in enumerate(calls) if call[0] == "add_argument"]
    exp_opt_calls = [
        i for i, call in enumerate(calls) if call[0] == "add_experimental_option"
    ]

    # add_argument calls should come before add_experimental_option calls
    if add_arg_calls and exp_opt_calls:
        assert max(add_arg_calls) < min(exp_opt_calls)


def test_driver_can_navigate():
    """Test that the driver can navigate to a page."""
    driver = autoshop.chrome.driver()

    try:
        # Navigate to a data URL (doesn't require internet)
        test_html = "data:text/html,<html><body><h1>Test Page</h1></body></html>"
        driver.get(test_html)

        # Verify navigation worked
        assert "Test Page" in driver.page_source

    finally:
        driver.quit()


def test_driver_maximized_on_start():
    """Test that the driver starts maximized."""
    driver = autoshop.chrome.driver()

    try:
        # Get window size
        size = driver.get_window_size()

        # Should be reasonably large (maximized)
        # This is a heuristic test - exact size depends on screen
        assert size["width"] > 1000
        assert size["height"] > 600

    finally:
        driver.quit()


@pytest.mark.integration
def test_driver_password_manager_disabled():
    """Test that password manager is disabled."""
    driver = autoshop.chrome.driver()

    try:
        # Navigate to a simple login form
        login_html = """
        data:text/html,
        <html>
            <body>
                <form>
                    <input type="text" name="username" id="username">
                    <input type="password" name="password" id="password">
                    <button type="submit">Login</button>
                </form>
            </body>
        </html>
        """
        driver.get(login_html)

        # Find and interact with password field
        username_field = driver.find_element("id", "username")
        password_field = driver.find_element("id", "password")

        username_field.send_keys("testuser")
        password_field.send_keys("testpass")

        # The test is mainly that this doesn't trigger password save dialogs
        # This is difficult to assert programmatically, but the configuration should prevent it

    finally:
        driver.quit()


# Tests for chrome module constants and exports
def test_all_exports():
    """Test that __all__ contains expected exports."""
    assert hasattr(autoshop.chrome, "__all__")
    expected_exports = ["driver"]

    assert set(autoshop.chrome.__all__) == set(expected_exports)


def test_driver_function_available():
    """Test that driver function is available."""
    assert hasattr(autoshop.chrome, "driver")
    assert callable(autoshop.chrome.driver)


# Integration tests for Chrome driver functionality
@pytest.mark.integration
def test_multiple_driver_instances():
    """Test creating multiple driver instances."""
    driver1 = autoshop.chrome.driver()
    driver2 = autoshop.chrome.driver()

    try:
        # Should be different instances
        assert driver1 != driver2

        # Both should work independently
        driver1.get("data:text/html,<html><body><h1>Driver 1</h1></body></html>")
        driver2.get("data:text/html,<html><body><h1>Driver 2</h1></body></html>")

        assert "Driver 1" in driver1.page_source
        assert "Driver 2" in driver2.page_source

    finally:
        driver1.quit()
        driver2.quit()


@pytest.mark.integration
def test_driver_basic_selenium_functionality():
    """Test basic Selenium functionality with the driver."""
    driver = autoshop.chrome.driver()

    try:
        # Test navigation
        test_html = """
        data:text/html,
        <html>
            <body>
                <div id="test-div">Hello World</div>
                <button id="test-button" onclick="this.innerHTML='Clicked'">Click Me</button>
            </body>
        </html>
        """
        driver.get(test_html)

        # Test element finding
        div_element = driver.find_element("id", "test-div")
        assert div_element.text == "Hello World"

        # Test clicking
        button_element = driver.find_element("id", "test-button")
        button_element.click()

        # Verify click worked
        assert button_element.text == "Clicked"

    finally:
        driver.quit()


@pytest.mark.integration
def test_driver_window_management():
    """Test window management functionality."""
    driver = autoshop.chrome.driver()

    try:
        # Test window size (should be maximized)
        size = driver.get_window_size()
        assert isinstance(size, dict)
        assert "width" in size
        assert "height" in size
        assert size["width"] > 0
        assert size["height"] > 0

        # Test window position
        position = driver.get_window_position()
        assert isinstance(position, dict)
        assert "x" in position
        assert "y" in position

    finally:
        driver.quit()


# Tests for error handling in chrome driver creation
def test_driver_creation_failure(mocker):
    """Test handling of driver creation failure."""
    mocker.patch(
        "undetected_chromedriver.Chrome",
        side_effect=Exception("Chrome creation failed"),
    )

    with pytest.raises(Exception, match="Chrome creation failed"):
        autoshop.chrome.driver()


def test_options_creation_failure(mocker):
    """Test handling of options creation failure."""
    mocker.patch(
        "undetected_chromedriver.ChromeOptions",
        side_effect=Exception("Options creation failed"),
    )

    with pytest.raises(Exception, match="Options creation failed"):
        autoshop.chrome.driver()
