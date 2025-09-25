import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from autoshop import all as autoshop
from autoshop.util import typing as autoshop_typing


# Tests for typing module imports
def test_webdriver_import():
    """Test that WebDriver is correctly imported."""
    assert hasattr(autoshop_typing, "WebDriver")
    assert autoshop_typing.WebDriver == WebDriver


def test_webelement_import():
    """Test that WebElement is correctly imported."""
    assert hasattr(autoshop_typing, "WebElement")
    assert autoshop_typing.WebElement == WebElement


def test_all_exports():
    """Test that __all__ contains expected exports."""
    assert hasattr(autoshop_typing, "__all__")
    expected_exports = ["WebDriver", "WebElement"]

    for export in expected_exports:
        assert export in autoshop_typing.__all__

    # Test that no unexpected exports are included
    assert set(autoshop_typing.__all__) == set(expected_exports)


# Tests for typing usage
def test_webdriver_type_annotation():
    """Test that WebDriver can be used for type annotations."""

    # This is more of a static test, but we can check the class
    def sample_function(driver: autoshop_typing.WebDriver) -> None:
        pass

    # Check that the annotation is accessible
    annotations = sample_function.__annotations__
    assert annotations["driver"] == autoshop_typing.WebDriver
    # In Python, -> None annotation is stored as None, not type(None)
    assert annotations["return"] is None


def test_webelement_type_annotation():
    """Test that WebElement can be used for type annotations."""

    def sample_function(element: autoshop_typing.WebElement) -> str:
        return element.text

    # Check that the annotation is accessible
    annotations = sample_function.__annotations__
    assert annotations["element"] == autoshop_typing.WebElement
    assert annotations["return"] is str


@pytest.mark.integration
def test_webdriver_isinstance_check():
    """Test isinstance check with WebDriver type."""
    # Create a real driver for testing
    driver = autoshop.chrome.driver()

    try:
        # Test isinstance check
        assert isinstance(driver, autoshop_typing.WebDriver)
        assert isinstance(driver, WebDriver)

    finally:
        driver.quit()


@pytest.mark.integration
def test_webelement_isinstance_check():
    """Test isinstance check with WebElement type."""
    # Create a real driver and element for testing
    driver = autoshop.chrome.driver()

    try:
        # Navigate to a simple page with an element
        driver.get(
            "data:text/html,<html><body><div id='test'>Hello World</div></body></html>"
        )

        # Get the element
        element = driver.find_element("id", "test")

        # Test isinstance check
        assert isinstance(element, autoshop_typing.WebElement)
        assert isinstance(element, WebElement)

    finally:
        driver.quit()


# Tests for typing availability through main autoshop module
def test_typing_available_in_autoshop_all():
    """Test that typing is available in autoshop.all."""
    assert hasattr(autoshop, "typing")
    assert autoshop.typing == autoshop_typing


def test_webdriver_available_through_autoshop():
    """Test that WebDriver is accessible through autoshop.typing."""
    assert hasattr(autoshop.typing, "WebDriver")
    assert autoshop.typing.WebDriver == WebDriver


def test_webelement_available_through_autoshop():
    """Test that WebElement is accessible through autoshop.typing."""
    assert hasattr(autoshop.typing, "WebElement")
    assert autoshop.typing.WebElement == WebElement


# Tests for typing module documentation
def test_module_has_all():
    """Test that the module defines __all__."""
    assert hasattr(autoshop_typing, "__all__")
    assert isinstance(autoshop_typing.__all__, list)
    assert len(autoshop_typing.__all__) > 0


def test_webdriver_class_info():
    """Test WebDriver class information."""
    webdriver_class = autoshop_typing.WebDriver

    # Should be a class
    assert isinstance(webdriver_class, type)

    # Should have expected methods (from selenium)
    expected_methods = ["get", "find_element", "quit", "close"]
    for method in expected_methods:
        assert hasattr(webdriver_class, method)


def test_webelement_class_info():
    """Test WebElement class information."""
    webelement_class = autoshop_typing.WebElement

    # Should be a class
    assert isinstance(webelement_class, type)

    # Should have expected methods (from selenium)
    expected_methods = ["click", "send_keys", "clear", "text"]
    for method in expected_methods:
        assert hasattr(webelement_class, method)


# Tests for edge cases and error handling
def test_typing_module_imports():
    """Test that the typing module can be imported independently."""
    # Test direct import
    from autoshop.util.typing import WebDriver, WebElement

    assert WebDriver == autoshop_typing.WebDriver
    assert WebElement == autoshop_typing.WebElement


def test_no_extra_attributes():
    """Test that the module doesn't expose unexpected attributes."""
    # Get all public attributes
    public_attrs = [attr for attr in dir(autoshop_typing) if not attr.startswith("_")]

    # Should only have WebDriver, WebElement, and __all__
    expected_attrs = set(["WebDriver", "WebElement"])
    actual_attrs = set(public_attrs) - {"__all__"}  # Exclude __all__ from comparison

    assert actual_attrs == expected_attrs


def test_module_level_consistency():
    """Test consistency between __all__ and actual exports."""
    # All items in __all__ should be accessible
    for item in autoshop_typing.__all__:
        assert hasattr(autoshop_typing, item)

    # All public items should be in __all__
    public_items = [
        name
        for name in dir(autoshop_typing)
        if not name.startswith("_") and name != "__all__"
    ]

    for item in public_items:
        assert item in autoshop_typing.__all__
