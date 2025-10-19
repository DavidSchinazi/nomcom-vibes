#!/usr/bin/env python3
import requests
import json
import os
from pathlib import Path

def get_session_id():
    session_id_file = Path("data/session_id.txt")
    if session_id_file.exists():
        return session_id_file.read_text().strip()
    else:
        session_id = input("Please enter your session ID: ")
        session_id_file.parent.mkdir(exist_ok=True)
        session_id_file.write_text(session_id)
        return session_id

def get_feedback():
    session_id = get_session_id()
    with open("data/nominees.json", "r") as f:
        nominees_data = json.load(f)

    if not os.path.exists("data/feedback_html"):
        os.makedirs("data/feedback_html")

    for nominee in nominees_data["objects"]:
        nominee_id = nominee["id"]
        url = f"https://datatracker.ietf.org/nomcom/2025/private/view-feedback/nominee/{nominee_id}"
        print(f"Downloading feedback for nominee {nominee_id} from {url}")
        response = requests.get(url, cookies={"sessionid": session_id})
        response.raise_for_status()
        with open(f"data/feedback_html/{nominee_id}.html", "w") as f:
            f.write(response.text)
        print(f"Saved feedback for nominee {nominee_id} to feedback_html/{nominee_id}.html")

if __name__ == "__main__":
    get_feedback()
