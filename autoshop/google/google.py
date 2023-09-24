from typing import Optional

import pandas as pd
import requests

import autoshop

LOGGER = autoshop.logging.logger(__name__)
URL_BASE = "https://sheets.googleapis.com/v4/spreadsheets"
ID_SHEET_INFORMATION_RECIPE = "1qMt1jKFf3OVILmA-MsQ8Ga-8vsYLsCX0ky00zairf9M"


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
        url=f"{URL_BASE}/{ID_SHEET_INFORMATION_RECIPE}/values/groceries!A1:G80",
        google_api_key=google_api_key,
    )


def get_all_food(
    google_api_key: Optional[str] = None,
) -> pd.DataFrame:
    return get(
        url=f"{URL_BASE}/{ID_SHEET_INFORMATION_RECIPE}/values/food!A1:F1000",
        google_api_key=google_api_key,
    )
