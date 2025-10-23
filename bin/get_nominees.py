#!/usr/bin/env python3
import argparse
import requests
import json
import os
from get_positions import get_position_name, get_position_short_name

NOMINEES_DATA = None
NOMINEE_POSITIONS_DATA = None
ACTIVE_NOMINEES_DATA = None

def get_nominees(force_download=False):
    global NOMINEES_DATA
    if NOMINEES_DATA:
        return NOMINEES_DATA

    nominees_file = "data/nominees.json"
    if not force_download and os.path.exists(nominees_file):
        with open(nominees_file, "r") as f:
            NOMINEES_DATA = json.load(f)['objects']
            return NOMINEES_DATA

    url = "https://datatracker.ietf.org/api/v1/nomcom/nominee/?nomcom=16&limit=1000"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    nominees_data = response.json()

    with open(nominees_file, "w") as f:
        json.dump(nominees_data, f, indent=4)
    print(f"Nominees data downloaded and saved to {nominees_file}")
    NOMINEES_DATA = nominees_data['objects']
    return NOMINEES_DATA

def get_nominee_info(nominee_id, force_download=False):
    nominee_file = f"data/nominees/{nominee_id}.json"
    if not force_download and os.path.exists(nominee_file):
        with open(nominee_file, "r") as f:
            return json.load(f)

    get_nominees()
    nominee = None
    for obj in NOMINEES_DATA:
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
    nominee_positions_data = get_nominee_positions(force_download=force_download)
    positions = {}
    for r in nominee['nominee_position']:
        short_name = get_position_short_name(get_position_name(r, force_download=force_download))
        state = 'unknown'
        for np in nominee_positions_data:
            if np['nominee'] == nominee['resource_uri'] and np['position'] == r:
                state = np['state'].split('/')[-2]
                break
        positions[short_name] = state
    nominee_info['positions'] = positions

    os.makedirs(os.path.dirname(nominee_file), exist_ok=True)
    with open(nominee_file, "w") as f:
        json.dump(nominee_info, f, indent=4)
    print(f"Nominee info downloaded and saved to {nominee_file}")

    return nominee_info

def print_meetings_attended(force_download=False):
    """Prints each nominee and the number of IETF meetings they have attended, sorted in descending order."""
    nominees_data = get_active_nominees(force_download=force_download)
    nominee_meetings = []
    for nominee in nominees_data:
        nominee_info = get_nominee_info(nominee['id'], force_download=force_download)
        name = nominee_info['name']
        meetings_attended = nominee_info['num_meetings_attended']
        nominee_meetings.append({'name': name, 'meetings': meetings_attended})

    nominee_meetings.sort(key=lambda x: x['meetings'], reverse=True)
    max_name_len = max(len(item['name']) for item in nominee_meetings)
    for item in nominee_meetings:
        print(f"{item['name']:>{max_name_len}}: {item['meetings']:>3} meetings")
    print("We have a total of {} nominees.".format(len(nominees_data)))

def get_nominee_positions(force_download=False):
    global NOMINEE_POSITIONS_DATA
    if NOMINEE_POSITIONS_DATA:
        return NOMINEE_POSITIONS_DATA

    nominee_positions_file = "data/nominee_positions.json"
    if not force_download and os.path.exists(nominee_positions_file):
        with open(nominee_positions_file, "r") as f:
            NOMINEE_POSITIONS_DATA = json.load(f)['objects']
            return NOMINEE_POSITIONS_DATA

    url = "https://datatracker.ietf.org/api/v1/nomcom/nomineeposition/?limit=4000"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    nominee_positions_data = response.json()

    with open(nominee_positions_file, "w") as f:
        json.dump(nominee_positions_data, f, indent=4)
    print(f"Nominee positions data downloaded and saved to {nominee_positions_file}")
    NOMINEE_POSITIONS_DATA = nominee_positions_data['objects']
    return NOMINEE_POSITIONS_DATA

def get_active_nominees(force_download=False):
    global ACTIVE_NOMINEES_DATA
    if ACTIVE_NOMINEES_DATA:
        return ACTIVE_NOMINEES_DATA

    nominees = get_nominees(force_download=force_download)
    active_nominees = []
    for nominee in nominees:
        nominee_info = get_nominee_info(nominee['id'], force_download=force_download)
        if not nominee_info['positions']:
            continue
        all_declined = True
        for state in nominee_info['positions'].values():
            if state != 'declined':
                all_declined = False
                break
        if not all_declined:
            active_nominees.append(nominee)

    ACTIVE_NOMINEES_DATA = active_nominees
    return active_nominees


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force-download", action="store_true", help="Force download even if file exists")
    parser.add_argument("-m", "--meetings-attended", action="store_true", help="Print number of meetings attended by each nominee, sorted.")
    parser.add_argument("nominee_id", nargs='?', help="Get info about a specific nominee")
    args = parser.parse_args()

    if args.meetings_attended:
        print_meetings_attended(force_download=args.force_download)
    elif args.nominee_id:
        print(json.dumps(get_nominee_info(args.nominee_id, force_download=args.force_download), indent=4))
    else:
        for nominee in get_nominees(force_download=args.force_download):
            get_nominee_info(nominee['id'], force_download=args.force_download)
