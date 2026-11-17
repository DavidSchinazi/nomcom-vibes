#!/usr/bin/env python3
import argparse
import requests
import json
import os
import re

NOMCOM_ID = None
NOMCOM_YEAR = None
POSITIONS_DATA = None
TOPICS_DATA = None

POSITION_SHORT_NAMES = {
    "Applications and Real Time (ART) AD": "ART",
    "Applications and Real-Time Area (ART) AD": "ART",
    "Internet Architecture Board, Member": "IAB",
    "Internet Architecture Board (IAB), Member": "IAB",
    "IETF LLC Board, Director": "LLC",
    "IETF LLC Board, Director (mid-term + 3 year term)": "LLC2",
    "IETF IPMC Board, Director": "IPMC",
    "IETF Trust, Trustee": "Trust",
    "IETF Chair / GEN AD": "GEN",
    "Internet (INT) AD": "INT",
    "Internet Area (INT) AD": "INT",
    "Mid-Term Vacancy Internet (INT) AD": "INT2",
    "Operations and Management (OPS) AD": "OPS",
    "Operations and Management Area (OPS) AD": "OPS",
    "Routing (RTG) AD": "RTG",
    "Routing Area (RTG) AD": "RTG",
    "Security (SEC) AD": "SEC",
    "Security Area (SEC) AD": "SEC",
    "Web and Internet Transport (WIT) AD": "WIT",
    "The Web and Internet Transport (WIT) AD": "WIT"
}


def get_nomcom_year():
    global NOMCOM_YEAR
    if NOMCOM_YEAR is not None:
        return NOMCOM_YEAR

    nomcom_year_file = "config/nomcom_year.txt"
    if os.path.exists(nomcom_year_file):
        with open(nomcom_year_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                NOMCOM_YEAR = content
                return NOMCOM_YEAR

    year = input("Please enter the year that your NomCom was selected (e.g., 2026): ").strip()
    if not year:
        raise ValueError("NomCom year cannot be empty")
    os.makedirs(os.path.dirname(nomcom_year_file), exist_ok=True)
    with open(nomcom_year_file, "w", encoding="utf-8") as f:
        f.write(f"{year}\n")
    NOMCOM_YEAR = year
    return NOMCOM_YEAR

def get_nomcom_id():
    global NOMCOM_ID
    if NOMCOM_ID is not None:
        return NOMCOM_ID

    nomcom_id_file = "config/nomcom_id.txt"
    if os.path.exists(nomcom_id_file):
        with open(nomcom_id_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                NOMCOM_ID = int(content)
                return NOMCOM_ID

    year = get_nomcom_year()

    url = "https://datatracker.ietf.org/api/v1/nomcom/nomcom/?limit=1000"
    response = requests.get(url)
    response.raise_for_status()
    nomcoms_data = response.json()

    nomcom_id = None
    target = f"nomcom{year}"
    for entry in nomcoms_data.get("objects", []):
        public_key = entry.get("public_key") or ""
        if target in public_key:
            nomcom_id = int(entry["id"])
            break

    if nomcom_id is None:
        raise ValueError(f"Could not find NomCom ID for year {year}")

    os.makedirs(os.path.dirname(nomcom_id_file), exist_ok=True)
    with open(nomcom_id_file, "w", encoding="utf-8") as f:
        f.write(f"{nomcom_id}\n")
    NOMCOM_ID = nomcom_id
    return NOMCOM_ID

def get_position_short_name(name):
    if not name:
        return name
    if name in POSITION_SHORT_NAMES:
        return POSITION_SHORT_NAMES[name]
    for full_name, s_name in POSITION_SHORT_NAMES.items():
        if full_name.lower() == name.lower():
            return s_name
    match = re.search(r'\(([A-Z0-9]+)\)', name)
    if match:
        return match.group(1)
    if "IPMC" in name:
        return "IPMC"
    if "LLC" in name:
        return "LLC"
    if "Trust" in name:
        return "Trust"
    if "GEN" in name or "General" in name:
        return "GEN"
    return name

def get_position_full_name(short_name):
    if not short_name:
        return short_name
    try:
        positions = get_positions()
        for p in positions:
            name = p.get('name', '')
            if get_position_short_name(name) == short_name:
                return name
    except Exception:
        pass

    for full_name, s_name in POSITION_SHORT_NAMES.items():
        if s_name == short_name:
            return full_name
    return short_name

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
    short_name = get_position_short_name(position_full_name)
    if short_name:
        for topic in topics:
            if short_name in topic['subject']:
                return topic['id']
    if 'Internet Architecture Board' in position_full_name or (expanded_full_name is not None and 'Internet Architecture Board' in expanded_full_name):
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
