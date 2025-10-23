#!/usr/bin/env python3
import requests
import json

def get_topics():
    """
    Fetches topics from the IETF datatracker API and prints their subjects.
    """
    url = "https://datatracker.ietf.org/api/v1/nomcom/topic/?limit=1000"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    topics_data = response.json()

    for topic in topics_data.get('objects', []):
        subject = topic.get('subject')
        description_path = topic.get('description')
        description_url = f"https://datatracker.ietf.org{description_path}"
        description_response = requests.get(description_url)
        description_response.raise_for_status()
        description_data = description_response.json()
        content = description_data.get('content')
        print(f"\n{subject}:\n\t{content}")

if __name__ == "__main__":
    get_topics()
