import autoshop
import pandas as pd


def test_get_groceries():
    df = autoshop.google.get_groceries()
    assert df.columns.to_list() == ["type", "nameFood", "url", "amount", "unit", "notRequired"]
    assert len(df) > 0
