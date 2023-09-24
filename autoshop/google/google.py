from typing import Optional

import pandas as pd
import requests

import autoshop

LOGGER = autoshop.logging.logger(__name__)
URL_BASE = "https://sheets.googleapis.com/v4/spreadsheets"
ID_INFORMATION_RECIPE = "1qMt1jKFf3OVILmA-MsQ8Ga-8vsYLsCX0ky00zairf9M"
ID_TESCO_FOOD = "1WVGEW5ni7xUs6o5Bs_8joM2iKZclX7hO3lTq2Wp8H-U"
MAX_SIZE = 1000


def get_raw(
    url: str,
    google_api_key: Optional[str] = None,
) -> dict:
    if google_api_key is None:
        google_api_key = autoshop.env.get("GOOGLE_API_KEY")
    LOGGER.info(f"Requesting from {url=}")
    response = requests.get(f"{url}?key={google_api_key}")
    return response.json()


def get(
    url: str,
    google_api_key: Optional[str] = None,
) -> pd.DataFrame:
    data = get_raw(url=url, google_api_key=google_api_key)
    return pd.DataFrame(data["values"][1:], columns=data["values"][0])


def get_groceries(
    google_api_key: Optional[str] = None,
) -> pd.DataFrame:
    return get(
        url=f"{URL_BASE}/{ID_INFORMATION_RECIPE}/values/groceries!A1:G{MAX_SIZE}",
        google_api_key=google_api_key,
    )


def get_all_food(
    google_api_key: Optional[str] = None,
) -> pd.DataFrame:
    return get(
        url=f"{URL_BASE}/{ID_INFORMATION_RECIPE}/values/food!A1:F{MAX_SIZE}",
        google_api_key=google_api_key,
    )


def get_shop(
    google_api_key: Optional[str] = None,
) -> pd.DataFrame:
    return (
        get(
            url=f"{URL_BASE}/{ID_INFORMATION_RECIPE}/values/thisWeekShop!A1:D{MAX_SIZE}",
            google_api_key=google_api_key,
        )
        # First row is empty as it is a pivot table
        .iloc[1:]
        .reset_index(drop=True)
        .rename(columns={"SUM of amount": "amount"})
        .assign(
            amount=lambda x: pd.to_numeric(x["amount"], errors="coerce"),
        )
    )
    

def get_food_conversion(
    google_api_key: Optional[str] = None,
) -> pd.DataFrame:
    return (
        get(
            url=f"{URL_BASE}/{ID_INFORMATION_RECIPE}/values/conversion_food!A1:C{MAX_SIZE}",
            google_api_key=google_api_key,
        )
        .rename(columns={"unitFrom": "unit"})
        .assign(
            toGram=lambda x: pd.to_numeric(x["toGram"], errors="coerce"),
        )
    )


def get_tesco_food_map(
    google_api_key: Optional[str] = None,
) -> pd.DataFrame:
    return (
        get(
            url=f"{URL_BASE}/{ID_TESCO_FOOD}/values/map!A1:L{10 * MAX_SIZE}",
            google_api_key=google_api_key,
        )
        .drop(columns=["raw", "image"])
        .dropna(subset=["order"])
        .assign(
            amount=lambda x: pd.to_numeric(x["amount"], errors="coerce"),
        )
    )
