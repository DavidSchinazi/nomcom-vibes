#!/usr/bin/env python3
import requests
import json

def get_nominees():
    url = "https://datatracker.ietf.org/api/v1/nomcom/nominee/?nomcom=16&limit=1000"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    nominees_data = response.json()

    with open("data/nominees.json", "w") as f:
        json.dump(nominees_data, f, indent=4)
    print("Nominees data downloaded and saved to data/nominees.json")

if __name__ == "__main__":
    get_nominees()
