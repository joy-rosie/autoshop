import pytest

from autoshop import all as autoshop


@pytest.mark.integration
def test_get_groceries():
    df = autoshop.google.get_groceries()
    assert df.columns.to_list() == [
        "type",
        "nameFood",
        "url",
        "amount",
        "unit",
        "notRequired",
    ]
    assert len(df) > 0


@pytest.mark.integration
def test_get_all_food():
    df = autoshop.google.get_all_food()
    assert df.columns.to_list() == [
        "food",
        "name",
        "idCofid",
        "specific",
        "search",
    ]
    assert len(df) > 0


@pytest.mark.integration
def test_get_shop():
    df = autoshop.google.get_shop()
    assert df.columns.to_list() == [
        "food",
        "nameFood",
        "unit",
        "amount",
    ]
    assert len(df) > 0


@pytest.mark.integration
def test_get_food_conversion():
    df = autoshop.google.get_food_conversion()
    assert df.columns.to_list() == [
        "food",
        "unit",
        "toGram",
    ]
    assert len(df) > 0


@pytest.mark.integration
def test_get_tesco_food_map():
    df = autoshop.google.get_tesco_food_map()
    assert df.columns.to_list() == [
        "food",
        "name",
        "search",
        "description",
        "link",
        "amount",
        "unit",
        "price",
        "datetime",
        "order",
    ]
    assert len(df) > 0
