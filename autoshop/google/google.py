from typing import Optional

import requests

import autoshop


def get_groceries(
    google_api_key: Optional[str] = None,
) -> dict:
    if google_api_key is None:
        google_api_key = autoshop.env.get("GOOGLE_API_KEY")
    response = requests.get(f"https://sheets.googleapis.com/v4/spreadsheets/1qMt1jKFf3OVILmA-MsQ8Ga-8vsYLsCX0ky00zairf9M/values/groceries!A1:G80?key={google_api_key}")
    return response.json()


def get_all_food(
    google_api_key: Optional[str] = None,
) -> dict:
    if google_api_key is None:
        google_api_key = autoshop.env.get("GOOGLE_API_KEY")
    response = requests.get(f"https://sheets.googleapis.com/v4/spreadsheets/1qMt1jKFf3OVILmA-MsQ8Ga-8vsYLsCX0ky00zairf9M/values/food!A1:F1000?key={google_api_key}")
    return response.json()
