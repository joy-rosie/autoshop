import unittest.mock

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from autoshop import all as autoshop


# Tests for wait_and_check_exists function
def test_wait_and_check_exists_found(mocker):
    """Test that wait_and_check_exists returns True when element exists."""
    mock_driver = mocker.Mock()
    mock_wait = mocker.Mock()
    mock_element = mocker.Mock()

    mocker.patch("autoshop.selenium.WebDriverWait", return_value=mock_wait)
    mock_wait.until.return_value = mock_element

    result = autoshop.selenium.wait_and_check_exists(
        driver=mock_driver,
        value="//test",
    )

    assert result is True
    mock_wait.until.assert_called_once()


def test_wait_and_check_exists_not_found(mocker):
    """Test that wait_and_check_exists returns False when element doesn't exist."""
    mock_driver = mocker.Mock()
    mock_wait = mocker.Mock()

    mocker.patch("autoshop.selenium.WebDriverWait", return_value=mock_wait)
    mock_wait.until.side_effect = TimeoutException()

    result = autoshop.selenium.wait_and_check_exists(
        driver=mock_driver,
        value="//nonexistent",
    )

    assert result is False


def test_wait_and_check_exists_custom_timeout(mocker):
    """Test wait_and_check_exists with custom timeout."""
    mock_driver = mocker.Mock()

    mock_wait_class = mocker.patch("autoshop.selenium.WebDriverWait")
    mock_wait = mocker.Mock()
    mock_wait_class.return_value = mock_wait
    mock_wait.until.return_value = mocker.Mock()

    autoshop.selenium.wait_and_check_exists(
        driver=mock_driver, value="//test", timeout=20
    )

    mock_wait_class.assert_called_with(mock_driver, 20)


# Tests for wait_and_get function
def test_wait_and_get_success(mocker):
    """Test successful element retrieval."""
    mock_driver = mocker.Mock()
    mock_wait = mocker.Mock()
    mock_element = mocker.Mock()

    mocker.patch("autoshop.selenium.WebDriverWait", return_value=mock_wait)
    mock_wait.until.return_value = True  # Just indicates the wait was successful
    mock_driver.find_element.return_value = mock_element
    mocker.patch("time.sleep")  # Mock the sleep call

    result = autoshop.selenium.wait_and_get(driver=mock_driver, value="//button")

    assert result == mock_element
    mock_driver.find_element.assert_called_with(by=By.XPATH, value="//button")


def test_wait_and_get_timeout(mocker):
    """Test wait_and_get with timeout exception."""
    mock_driver = mocker.Mock()
    mock_wait = mocker.Mock()

    mocker.patch("autoshop.selenium.WebDriverWait", return_value=mock_wait)
    mock_wait.until.side_effect = TimeoutException()

    with pytest.raises(TimeoutException):
        autoshop.selenium.wait_and_get(driver=mock_driver, value="//nonexistent")


def test_wait_and_get_with_by_parameter(mocker):
    """Test wait_and_get with custom By parameter."""
    mock_driver = mocker.Mock()
    mock_wait = mocker.Mock()
    mock_element = mocker.Mock()

    mocker.patch("autoshop.selenium.WebDriverWait", return_value=mock_wait)
    mock_condition = mocker.patch(
        "selenium.webdriver.support.expected_conditions.presence_of_element_located"
    )
    mock_wait.until.return_value = True  # Just indicates wait was successful
    mock_condition.return_value = mocker.Mock()
    mock_driver.find_element.return_value = mock_element
    mocker.patch("time.sleep")  # Mock the sleep call

    result = autoshop.selenium.wait_and_get(
        driver=mock_driver, value="test-id", by=By.ID
    )

    mock_condition.assert_called_with((By.ID, "test-id"))
    assert result == mock_element
    mock_driver.find_element.assert_called_with(by=By.ID, value="test-id")


# Tests for wait_and_click function
def test_wait_and_click_success(mocker):
    """Test successful click operation."""
    mock_driver = mocker.Mock()
    mock_element = mocker.Mock()

    # Mock wait_and_get to return our mock element
    mocker.patch("autoshop.selenium.wait_and_get", return_value=mock_element)

    autoshop.selenium.wait_and_click(driver=mock_driver, value="//button")

    mock_element.click.assert_called_once()


def test_wait_and_click_timeout(mocker):
    """Test wait_and_click with timeout."""
    mock_driver = mocker.Mock()

    # Mock wait_and_get to raise TimeoutException
    mocker.patch("autoshop.selenium.wait_and_get", side_effect=TimeoutException())

    # Should raise exception since wait_and_click doesn't catch it
    with pytest.raises(TimeoutException):
        autoshop.selenium.wait_and_click(driver=mock_driver, value="//nonexistent")


# Tests for send keys functions
def test_wait_and_send_keys_success(mocker):
    """Test successful send keys operation."""
    mock_driver = mocker.Mock()
    mock_element = mocker.Mock()

    # Mock wait_and_get to return our mock element
    mocker.patch("autoshop.selenium.wait_and_get", return_value=mock_element)

    autoshop.selenium.wait_and_send_keys(
        driver=mock_driver, value="//input", keys="test text"
    )

    mock_element.send_keys.assert_called_once_with("test text")


def test_wait_and_delete_and_send_keys(mocker):
    """Test delete and send keys operation."""
    mock_driver = mocker.Mock()
    mock_element = mocker.Mock()

    # Mock wait_and_get to return our mock element
    mocker.patch("autoshop.selenium.wait_and_get", return_value=mock_element)

    autoshop.selenium.wait_and_delete_and_send_keys(
        driver=mock_driver, value="//input", keys="new text"
    )

    # Should send DELETE 5 times, then send the new text
    expected_calls = [unittest.mock.call(Keys.DELETE)] * 5 + [
        unittest.mock.call("new text")
    ]
    assert mock_element.send_keys.call_args_list == expected_calls


def test_wait_and_select_all_and_send_keys(mocker):
    """Test select all and send keys operation."""
    mock_driver = mocker.Mock()
    mock_element = mocker.Mock()

    # Mock wait_and_get to return our mock element
    mocker.patch("autoshop.selenium.wait_and_get", return_value=mock_element)

    autoshop.selenium.wait_and_select_all_and_send_keys(
        driver=mock_driver, value="//input", keys="replacement text"
    )

    # Should send Ctrl+A then the new text
    expected_calls = [
        unittest.mock.call(Keys.CONTROL + "a"),
        unittest.mock.call("replacement text"),
    ]
    assert mock_element.send_keys.call_args_list == expected_calls


# Tests for selenium module constants
def test_by_constant():
    """Test that 'by' constant is accessible."""
    assert autoshop.selenium.by == By


def test_keys_constant():
    """Test that 'keys' constant is accessible."""
    assert autoshop.selenium.keys == Keys


def test_timeout_exception():
    """Test that TimeoutException is accessible."""
    assert autoshop.selenium.TimeoutException == TimeoutException


# Integration tests that require a real driver
@pytest.fixture
def driver():
    """Provide a real Chrome driver for integration tests."""
    driver = autoshop.chrome.driver()
    yield driver
    driver.quit()


@pytest.mark.integration
def test_wait_and_get_real_element(driver):
    """Test wait_and_get with a real page."""
    driver.get("data:text/html,<html><body><div id='test'>Hello</div></body></html>")

    element = autoshop.selenium.wait_and_get(driver=driver, value="test", by=By.ID)

    assert element is not None
    assert element.text == "Hello"


@pytest.mark.integration
def test_wait_and_click_real_element(driver):
    """Test wait_and_click with a real clickable element."""
    driver.get(
        "data:text/html,<html><body><button id='btn' onclick='this.innerHTML=\"Clicked\"'>Click Me</button></body></html>"
    )

    autoshop.selenium.wait_and_click(driver=driver, value="btn", by=By.ID)

    # Verify the click worked
    element = driver.find_element(By.ID, "btn")
    assert element.text == "Clicked"
