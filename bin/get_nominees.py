#!/usr/bin/env python3
import argparse
import requests
import json
import os
from get_positions import get_position_name, get_position_short_name

NOMINEES_DATA = None

def get_nominees(force_download=False):
    global NOMINEES_DATA
    if NOMINEES_DATA:
        return NOMINEES_DATA

    nominees_file = "data/nominees.json"
    if not force_download and os.path.exists(nominees_file):
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

def get_nominee_info(nominee_id, force_download=False):
    nominee_file = f"data/nominees/{nominee_id}.json"
    if not force_download and os.path.exists(nominee_file):
        with open(nominee_file, "r") as f:
            return json.load(f)

    get_nominees()
    nominee = None
    for obj in NOMINEES_DATA['objects']:
        if str(obj['id']) == str(nominee_id):
            nominee = obj
            break
    if not nominee:
        raise Exception(f'Nominee with id {nominee_id} not found')

    email_path = nominee['email']
    url = f'https://datatracker.ietf.org{email_path}'
    response = requests.get(url)
    response.raise_for_status()
    email_data = response.json()
    person_path = email_data['person']

    url = f'https://datatracker.ietf.org{person_path}'
    response = requests.get(url)
    response.raise_for_status()
    nominee_info = response.json()

    url = f'https://datatracker.ietf.org/api/v1/meeting/attended/?person={nominee_info["id"]}&limit=1'
    response = requests.get(url)
    response.raise_for_status()
    attended_data = response.json()
    nominee_info['num_meetings_attended'] = attended_data['meta']['total_count']

    nominee_info['nominee_id'] = nominee_id
    nominee_info['email'] = email_data['address']
    nominee_info['positions'] = [get_position_short_name(get_position_name(r, force_download=force_download)) for r in nominee['nominee_position']]

    os.makedirs(os.path.dirname(nominee_file), exist_ok=True)
    with open(nominee_file, "w") as f:
        json.dump(nominee_info, f, indent=4)
    print(f"Nominee info downloaded and saved to {nominee_file}")

    return nominee_info

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force-download", action="store_true", help="Force download even if file exists")
    parser.add_argument("nominee_id", nargs='?', help="Get info about a specific nominee")
    args = parser.parse_args()

    if args.nominee_id:
        print(json.dumps(get_nominee_info(args.nominee_id, force_download=args.force_download), indent=4))
    else:
        nominees = get_nominees(force_download=args.force_download)
        for nominee in nominees['objects']:
            get_nominee_info(nominee['id'], force_download=args.force_download)
