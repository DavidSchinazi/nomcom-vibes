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
        print(topic.get('subject'))

if __name__ == "__main__":
    get_topics()
