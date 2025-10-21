#!/usr/bin/env python3
import requests
import json

def get_positions():
    url = "https://datatracker.ietf.org/api/v1/nomcom/position/?nomcom=16&limit=1000"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    positions_data = response.json()

    with open("data/positions.json", "w") as f:
        json.dump(positions_data, f, indent=4)
    print("Positions data downloaded and saved to data/positions.json")

if __name__ == "__main__":
    get_positions()
