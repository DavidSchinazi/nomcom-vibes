#!/usr/bin/env python3
import json
import argparse
from bs4 import BeautifulSoup
import re
import os
import sys
from get_nominees import get_nominees

def parse_feedback(nominee_id):
    input_file = f"data/feedback_html/{nominee_id}.html"
    output_file = f"data/feedback_json/{nominee_id}.json"
    # Read the HTML file
    with open(input_file, "r") as f:
        html_content = f.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "lxml")

    # Find the active tab pane which contains the feedback comments
    comment_tab_pane = soup.find("div", {"id": "comment", "role": "tabpanel", "class": "tab-pane active"})

    feedback_data = []

    if comment_tab_pane:
        # Find all feedback entries within the comment tab pane
        feedback_entries = comment_tab_pane.find_all("dl", class_="row")

        for entry in feedback_entries:
            data = {}
            dts = entry.find_all("dt")
            for dt in dts:
                dt_text = dt.text.strip()
                dd = dt.find_next_sibling("dd")
                if dd:
                    dd_text = dd.text.strip()
                    if "From" in dt_text:
                        if len(dd.contents) > 0:
                            name = dd.contents[0].strip().replace('<', '').strip()
                            data['name'] = name
                        email_tag = dd.find("a")
                        if email_tag and "mailto:" in email_tag.get("href", ""):
                            data["email"] = email_tag.text.strip()
                    elif "Date" in dt_text:
                        data["date"] = dd_text
                    elif "Positions" in dt_text:
                        data["position"] = dd_text
                    elif "Feedback" in dt_text:
                        pre_tag = dd.find("pre")
                        if pre_tag:
                            data["feedback"] = pre_tag.text.strip()
                    elif "Subject" in dt_text:
                        data["subject"] = dd_text
            
            if data:
                feedback_data.append(data)

    result = {}
    result["feedback"] = feedback_data

    # Write the extracted data to a JSON file
    with open(output_file, "w") as json_file:
        json.dump(result, json_file, indent=4)

    print(f"Successfully extracted feedback from {input_file} and saved to {output_file}")

def parse_all_feedback():
    nominees_data = get_nominees()
    output_dir = "data/feedback_json"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for nominee in nominees_data["objects"]:
        nominee_id = nominee["id"]
        parse_feedback(nominee_id)

if __name__ == "__main__":
    parse_all_feedback()
