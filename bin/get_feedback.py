#!/usr/bin/env python3
import requests
import json
import os
from pathlib import Path
from get_nominees import get_nominees

def get_session_id():
    session_id_file = Path("data/session_id.txt")
    if session_id_file.exists():
        return session_id_file.read_text().strip()
    else:
        session_id = input("Please enter your IETF Datatracker session ID: ")
        session_id_file.parent.mkdir(exist_ok=True)
        session_id_file.write_text(session_id)
        return session_id

def save_html_feedback_for_nominee(nominee_id, session_id, force_download=False):
    """Downloads and saves the HTML feedback for a single nominee."""
    output_file = f"data/feedback_html/{nominee_id}.html"
    if not force_download and os.path.exists(output_file):
        print(f"Feedback for nominee {nominee_id} already exists. Skipping download.")
        return

    url = f"https://datatracker.ietf.org/nomcom/2025/private/view-feedback/nominee/{nominee_id}"
    print(f"Downloading feedback for nominee {nominee_id} from {url}")
    response = requests.get(url, cookies={"sessionid": session_id})
    response.raise_for_status()
    with open(output_file, "w") as f:
        f.write(response.text)
    print(f"Saved feedback for nominee {nominee_id} to {output_file}")


def save_all_html_feedback(force_download=False):
    """Saves HTML feedback for all nominees."""
    session_id = get_session_id()
    nominees_data = get_nominees(force_download=force_download)

    if not os.path.exists("data/feedback_html"):
        os.makedirs("data/feedback_html")

    for nominee in nominees_data["objects"]:
        nominee_id = nominee["id"]
        save_html_feedback_for_nominee(nominee_id, session_id, force_download=force_download)


if __name__ == "__main__":
    save_all_html_feedback()
