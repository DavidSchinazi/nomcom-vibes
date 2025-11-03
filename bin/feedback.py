#!/usr/bin/env python3
import argparse
import requests
import json
import os
from pathlib import Path
from nominees import get_active_nominees
from positions import get_topic_id_from_position_name

SESSION_ID = None

def get_session_id():
    global SESSION_ID
    if not SESSION_ID:
        session_id_file = Path("config/session_id.txt")
        os.makedirs(os.path.dirname(session_id_file), exist_ok=True)
        if session_id_file.exists():
            SESSION_ID = session_id_file.read_text().strip()
        else:
            print("\nHello, and welcome to NomCom Vibes!\n")
            print("In order to download confidential NomCom feedback, this tool needs your IETF datatracker cookie.")
            print("To gather it, start your favorite browser and open Developer Tools.")
            print("For most browsers, you can do that by pressing Cmd-Option-I or Ctrl-Shift-I.")
            print("Then navigate to the NomCom private page at:\n")
            print("https://datatracker.ietf.org/nomcom/2025/private/\n")
            print("You will need to log in and enter the NomCom private key if you haven't already.")
            print("Once you're able to see the NomCom private area, use Developer Tools to check HTTP headers.")
            print("You'll need to find either the \"Cookie\" header on the request, or the \"Set-Cookie\" header on the response.")
            print("You'll find multiple cookies there, and the one we need is \"sessionid\".")
            print("For example, it'll look like `sessionid=k5swyy3pnvstettpnvbw63kwnfrgk4zb;`.\n")
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
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"Saved HTML feedback for nominee {nominee_id} to {output_file}")


def save_html_feedback_for_position(position_name, force_feedback=False):
    """Downloads and saves the HTML feedback for a single position."""
    session_id = get_session_id()
    topic_id = get_topic_id_from_position_name(position_name)
    if not topic_id:
        print(f"Could not find topic ID for position {position_name}")
        return
    output_file = f"data/feedback_html/position_{topic_id}.html"
    if not force_feedback and os.path.exists(output_file):
        return

    url = f"https://datatracker.ietf.org/nomcom/2025/private/view-feedback/topic/{topic_id}"
    print(f"Downloading HTML feedback for position {position_name} from {url}")
    response = requests.get(url, cookies={"sessionid": session_id})
    response.raise_for_status()

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"Saved HTML feedback for position {position_name} to {output_file}")


def save_all_html_feedback(force_metadata=False, force_feedback=False):
    """Saves HTML feedback for all nominees."""
    for nominee in get_active_nominees(force_metadata=force_metadata):
        save_html_feedback_for_nominee(nominee["id"], force_feedback=force_feedback)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--force-metadata", action="store_true", help="Force download of metadata even if file exists")
    parser.add_argument("-f", "--force-feedback", action="store_true", help="Force download of feedback even if file exists")
    parser.add_argument("identifier", nargs="?", help="Optional: The nominee ID or position name to get feedback for.")
    parser.add_argument("-a", "--force-all", action="store_true", help="Get latest feedback and redo subsequent operations")
    args = parser.parse_args()

    if args.force_all:
        args.force_feedback = True

    if args.identifier:
        try:
            nominee_id = int(args.identifier)
            save_html_feedback_for_nominee(nominee_id, force_feedback=args.force_feedback)
        except ValueError:
            position_name = args.identifier
            save_html_feedback_for_position(position_name, force_feedback=args.force_feedback)
    else:
        save_all_html_feedback(force_metadata=args.force_metadata, force_feedback=args.force_feedback)
