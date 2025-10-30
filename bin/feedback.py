#!/usr/bin/env python3
import argparse
import requests
import json
import os
from pathlib import Path
from nominees import get_active_nominees

SESSION_ID = None

def get_session_id():
    global SESSION_ID
    if not SESSION_ID:
        session_id_file = Path("config/session_id.txt")
        os.makedirs(os.path.dirname(session_id_file), exist_ok=True)
        if session_id_file.exists():
            SESSION_ID = session_id_file.read_text().strip()
        else:
            SESSION_ID = input("Please enter your IETF Datatracker session ID: ")
            session_id_file.parent.mkdir(exist_ok=True)
            session_id_file.write_text(SESSION_ID)
    return SESSION_ID

def save_html_feedback_for_nominee(nominee_id, force_feedback=False):
    """Downloads and saves the HTML feedback for a single nominee."""
    session_id = get_session_id()
    output_file = f"data/feedback_html/{nominee_id}.html"
    if not force_feedback and os.path.exists(output_file):
        return

    url = f"https://datatracker.ietf.org/nomcom/2025/private/view-feedback/nominee/{nominee_id}"
    print(f"Downloading HTML feedback for nominee {nominee_id} from {url}")
    response = requests.get(url, cookies={"sessionid": session_id})
    response.raise_for_status()

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        f.write(response.text)
    print(f"Saved HTML feedback for nominee {nominee_id} to {output_file}")


def save_all_html_feedback(force_metadata=False, force_feedback=False):
    """Saves HTML feedback for all nominees."""
    for nominee in get_active_nominees(force_metadata=force_metadata):
        save_html_feedback_for_nominee(nominee["id"], force_feedback=force_feedback)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--force-metadata", action="store_true", help="Force download of metadata even if file exists")
    parser.add_argument("-f", "--force-feedback", action="store_true", help="Force download of feedback even if file exists")
    parser.add_argument("-a", "--force-all", action="store_true", help="Enable -m and -f flags")
    args = parser.parse_args()

    if args.force_all:
        args.force_metadata = True
        args.force_feedback = True

    save_all_html_feedback(force_metadata=args.force_metadata, force_feedback=args.force_feedback)
