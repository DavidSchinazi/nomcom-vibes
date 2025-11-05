#!/usr/bin/env python3
import argparse
import requests
import json
import os

POSITIONS_DATA = None
TOPICS_DATA = None

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

def get_nomcom_id():
    return 16

def get_position_short_name(name):
    return POSITION_SHORT_NAMES[name]

def get_position_full_name(short_name):
    for full_name, s_name in POSITION_SHORT_NAMES.items():
        if s_name == short_name:
            return full_name
    return None

def get_positions(force_metadata=False):
    global POSITIONS_DATA
    if POSITIONS_DATA:
        return POSITIONS_DATA

    positions_file = "data/positions.json"
    if not force_metadata and os.path.exists(positions_file):
        with open(positions_file, "r", encoding="utf-8") as f:
            POSITIONS_DATA = json.load(f)['objects']
            return POSITIONS_DATA

    nomcom_id = get_nomcom_id()
    url = f"https://datatracker.ietf.org/api/v1/nomcom/position/?nomcom={nomcom_id}&limit=1000"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    positions_data = response.json()

    os.makedirs(os.path.dirname(positions_file), exist_ok=True)
    with open(positions_file, "w", encoding="utf-8") as f:
        json.dump(positions_data, f, indent=4)
    print(f"Positions data downloaded and saved to {positions_file}")
    POSITIONS_DATA = positions_data['objects']
    return POSITIONS_DATA

def get_topics(force_metadata=False):
    global TOPICS_DATA
    if TOPICS_DATA:
        return TOPICS_DATA

    topics_file = "data/topics.json"
    if not force_metadata and os.path.exists(topics_file):
        with open(topics_file, "r", encoding="utf-8") as f:
            TOPICS_DATA = json.load(f)['objects']
            return TOPICS_DATA

    nomcom_id = get_nomcom_id()
    url = f"https://datatracker.ietf.org/api/v1/nomcom/topic/?nomcom={nomcom_id}&limit=1000"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    topics_data = response.json()

    os.makedirs(os.path.dirname(topics_file), exist_ok=True)
    with open(topics_file, "w", encoding="utf-8") as f:
        json.dump(topics_data, f, indent=4)
    print(f"Topics data downloaded and saved to {topics_file}")
    TOPICS_DATA = topics_data['objects']
    return TOPICS_DATA

def get_position_name(resource_uri, force_metadata=False):
    positions = get_positions(force_metadata=force_metadata)
    for position in positions:
        if position['resource_uri'] == resource_uri:
            return position['name']
    return None

def get_topic_id_from_position_name(position_full_name, force_metadata=False):
    topics = get_topics(force_metadata=force_metadata)
    for topic in topics:
        if position_full_name in topic['subject']:
            return topic['id']
    expanded_full_name = get_position_full_name(position_full_name)
    if expanded_full_name:
        for topic in topics:
            if expanded_full_name in topic['subject']:
                return topic['id']
    if 'Internet Architecture Board' in position_full_name or 'Internet Architecture Board' in expanded_full_name:
        for topic in topics:
            if 'IAB' in topic['subject']:
                return topic['id']
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--force-metadata", action="store_true", help="Force download of metadata even if file exists")
    args = parser.parse_args()

    get_positions(force_metadata=args.force_metadata)
    get_topics(force_metadata=args.force_metadata)
