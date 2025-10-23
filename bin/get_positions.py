#!/usr/bin/env python3
import argparse
import requests
import json
import os

POSITIONS_DATA = None

POSITION_SHORT_NAMES = {
    "Applications and Real Time (ART) AD": "ART",
    "Internet Architecture Board, Member": "IAB",
    "IETF LLC Board, Director": "LLC",
    "IETF Trust, Trustee": "Trust",
    "IETF Chair / GEN AD": "GEN",
    "Internet (INT) AD": "INT",
    "Operations and Management (OPS) AD": "OPS",
    "Routing (RTG) AD": "RTG",
    "Security (SEC) AD": "SEC",
    "Web and Internet Transport (WIT) AD": "WIT"
}

def get_position_short_name(name):
    return POSITION_SHORT_NAMES[name]

def get_positions(force_download=False):
    global POSITIONS_DATA
    if POSITIONS_DATA:
        return POSITIONS_DATA

    positions_file = "data/positions.json"
    if not force_download and os.path.exists(positions_file):
        print(f"'{positions_file}' already exists. Skipping download.")
        with open(positions_file, "r") as f:
            POSITIONS_DATA = json.load(f)['objects']
            return POSITIONS_DATA

    url = "https://datatracker.ietf.org/api/v1/nomcom/position/?nomcom=16&limit=1000"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    positions_data = response.json()

    with open(positions_file, "w") as f:
        json.dump(positions_data, f, indent=4)
    print(f"Positions data downloaded and saved to {positions_file}")
    POSITIONS_DATA = positions_data['objects']
    return POSITIONS_DATA

def get_position_name(resource_uri, force_download=False):
    positions = get_positions(force_download=force_download)
    for position in positions:
        if position['resource_uri'] == resource_uri:
            return position['name']
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force-download", action="store_true", help="Force download even if file exists")
    args = parser.parse_args()
    get_positions(force_download=args.force_download)
