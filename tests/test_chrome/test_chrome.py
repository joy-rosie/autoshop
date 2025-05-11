from autoshop import all as autoshop


def test_driver():
    driver = autoshop.chrome.driver()
    assert driver is not None
