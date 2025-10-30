#!/usr/bin/env python3
import argparse
import requests
import json
import os
from positions import get_position_name, get_position_short_name

NOMINEES_DATA = None
NOMINEE_POSITIONS_DATA = None
ACTIVE_NOMINEES_DATA = None
NOMINEES_BY_POSITION_DATA = None

def load_nominees(force_metadata=False):
    global NOMINEES_DATA
    if NOMINEES_DATA:
        return NOMINEES_DATA

    nominees_file = "data/nominees.json"
    if not force_metadata and os.path.exists(nominees_file):
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

def get_nominee_info(nominee_id, force_metadata=False):
    nominee_file = f"data/nominees/{nominee_id}.json"
    if not force_metadata and os.path.exists(nominee_file):
        with open(nominee_file, "r") as f:
            return json.load(f)

    nominee = None
    for obj in load_nominees(force_metadata=force_metadata):
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

    url = f'https://datatracker.ietf.org/api/v1/doc/documentauthor/?email={email_data["address"]}'
    response = requests.get(url)
    response.raise_for_status()
    drafts_data = response.json()
    nominee_info['num_drafts'] = drafts_data['meta']['total_count']

    nominee_info['nominee_id'] = nominee_id
    nominee_info['email'] = email_data['address']
    nominee_positions_data = get_nominee_positions(force_metadata=force_metadata)
    positions = {}
    for r in nominee['nominee_position']:
        short_name = get_position_short_name(get_position_name(r, force_metadata=force_metadata))
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

def print_nominee_info(force_metadata=False):
    """Prints each nominee and the number of IETF meetings they have attended, sorted in descending order."""
    nominees_data = get_active_nominees(force_metadata=force_metadata)
    nominee_stats = []
    for nominee in nominees_data:
        nominee_info = get_nominee_info(nominee['id'], force_metadata=force_metadata)
        name = nominee_info['name']
        meetings_attended = nominee_info['num_meetings_attended']
        num_drafts = nominee_info['num_drafts']
        nominee_stats.append({'name': name, 'meetings': meetings_attended, 'drafts': num_drafts})

    nominee_stats.sort(key=lambda x: x['meetings'] + x['drafts'], reverse=True)
    max_name_len = max(len(item['name']) for item in nominee_stats)
    for item in nominee_stats:
        print(f"{item['name']:>{max_name_len}}: {item['meetings']:>3} meetings, {item['drafts']:>3} drafts")
    print("We have a total of {} nominees.".format(len(nominees_data)))

def get_nominee_positions(force_metadata=False):
    global NOMINEE_POSITIONS_DATA
    if NOMINEE_POSITIONS_DATA:
        return NOMINEE_POSITIONS_DATA

    nominee_positions_file = "data/nominee_positions.json"
    if not force_metadata and os.path.exists(nominee_positions_file):
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

def get_active_nominees(force_metadata=False):
    global ACTIVE_NOMINEES_DATA
    if ACTIVE_NOMINEES_DATA:
        return ACTIVE_NOMINEES_DATA

    nominees = load_nominees(force_metadata=force_metadata)
    active_nominees = []
    for nominee in nominees:
        nominee_info = get_nominee_info(nominee['id'], force_metadata=force_metadata)
        if not nominee_info['positions']:
            continue
        has_accepted = False
        for state in nominee_info['positions'].values():
            if state == 'accepted':
                has_accepted = True
                break
        if has_accepted:
            active_nominees.append(nominee)

    ACTIVE_NOMINEES_DATA = active_nominees
    return active_nominees


def get_nominees_by_position(force_metadata=False):
    global NOMINEES_BY_POSITION_DATA
    if NOMINEES_BY_POSITION_DATA:
        return NOMINEES_BY_POSITION_DATA
    NOMINEES_BY_POSITION_DATA = {}
    for nominee in get_active_nominees(force_metadata=force_metadata):
        nominee_info = get_nominee_info(nominee['id'], force_metadata=force_metadata)
        for position, state in nominee_info['positions'].items():
            if state == 'accepted':
                if position not in NOMINEES_BY_POSITION_DATA:
                    NOMINEES_BY_POSITION_DATA[position] = []
                NOMINEES_BY_POSITION_DATA[position].append(nominee['id'])
    return NOMINEES_BY_POSITION_DATA


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--force-metadata", action="store_true", help="Force download of metadata even if file exists")
    parser.add_argument("-a", "--force-all", action="store_true", help="Enable -m flag")
    parser.add_argument("--info", action="store_true", help="Print info on each nominee, sorted.")
    parser.add_argument("--by-position", action="store_true", help="Print nominees by position.")
    parser.add_argument("nominee_id", nargs='?', help="Get info about a specific nominee")
    args = parser.parse_args()

    if args.force_all:
        args.force_metadata = True

    if args.info:
        print_nominee_info(force_metadata=args.force_metadata)
    elif args.by_position:
        print(json.dumps(get_nominees_by_position(force_metadata=args.force_metadata), indent=4))
    elif args.nominee_id:
        print(json.dumps(get_nominee_info(args.nominee_id, force_metadata=args.force_metadata), indent=4))
    else:
        for nominee in load_nominees(force_metadata=args.force_metadata):
            get_nominee_info(nominee['id'], force_metadata=args.force_metadata)
