#!/usr/bin/env python3
import requests
import json
import os

NOMINEES_DATA = None

def get_nominees(force_download=False):
    global NOMINEES_DATA
    if NOMINEES_DATA and not force_download:
        return NOMINEES_DATA

    nominees_file = "data/nominees.json"
    if not force_download and os.path.exists(nominees_file):
        print(f"'{nominees_file}' already exists. Skipping download.")
        with open(nominees_file, "r") as f:
            NOMINEES_DATA = json.load(f)
            return NOMINEES_DATA

    url = "https://datatracker.ietf.org/api/v1/nomcom/nominee/?nomcom=16&limit=1000"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    nominees_data = response.json()

    with open(nominees_file, "w") as f:
        json.dump(nominees_data, f, indent=4)
    print(f"Nominees data downloaded and saved to {nominees_file}")
    NOMINEES_DATA = nominees_data
    return NOMINEES_DATA

if __name__ == "__main__":
    get_nominees()
