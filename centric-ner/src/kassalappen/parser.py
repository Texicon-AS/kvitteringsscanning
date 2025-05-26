"""
@brief Simple parser for Kassalapp API, with exception handling and automatic filtering of useful data fields for training data.
"""

import json
import os
import time
import requests
from typing import Dict, List


def getKassalappData(
    url: str,
    headers: Dict = {
        "Content-Type": "application/json",
        "Accepts": "application/json",
    },
) -> Dict:
    """Fetches data from given url with exception handling"""

    try:
        response = requests.get(
            url=url,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error making API call : {e}")
        return {}


def appendToJsonFile(path: str, data: Dict, useful_fields: List) -> None:
    """Helper function to write to existing json file. Program checks if file exists, and appends data to the end of json array."""
    useful_data = [{field: item.get(field) for field in useful_fields} for item in data]

    if os.path.exists(path):
        with open(path, "r+", encoding="utf8") as file:
            file.seek(0, os.SEEK_END)
            pos = file.tell() - 1
            while pos > 0:
                file.seek(pos)
                last_char = file.read(1)
                if last_char == "]":
                    file.seek(pos)
                    break
                pos -= 1

            for i,item in enumerate(useful_data):
                file.write(",\n")
                json.dump(item, file)
            
            file.write("]")  # close the array properly.
    else:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(useful_data, file)


if __name__ == "__main__":

    useful_fields = ["id", "name", "category", "weight", "weight_unit"]
    page_number = 25000
    apiToken = "gHmg6jq8Id1x4q1Eqk68ZMJEb5vxrLRY1bPcd9If"  #! It does not look like that there is any expiration date for the bearer token for Kassalappen API.
    while True:  #! This will end if response is invalid.
        baseUrl = f"https://kassal.app/api/v1/products?page={page_number}"
        headers = {
            "Authorization": f"Bearer {apiToken}",
            "Content-Type": "application/json",
            "Accepts": "application/json",
            "page": f"{page_number}",
            "size": "100",  # Doesn't seem to work.
            "unique": "true",  # to filter out any duplicates from different stores.
            "sort": "name_asc",
        }

        print(f"Fetching data, from page: {page_number}")
        raw_res = getKassalappData(headers=headers, url=baseUrl)
        if raw_res == None:
            print("Failed to fetch the data! Exiting the program.")
            exit(-1)
        if isinstance(raw_res, dict) and "data" in raw_res:
            raw_res = raw_res["data"]
        else:
            print("Unexpected response format")
            exit(-1)

        appendToJsonFile(
            "src/kassalappen/filtered-results.json",
            data=raw_res,
            useful_fields=useful_fields,
        )
        time.sleep(1)

        print(f"Successfully fetched the data, from page: {page_number}")
        page_number += 1
