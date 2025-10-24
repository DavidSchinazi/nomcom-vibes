#!/usr/bin/env python3
import json
import argparse
from bs4 import BeautifulSoup
import re
import os
import sys
from get_nominees import get_active_nominees, get_nominee_info
from get_positions import get_position_short_name
from get_feedback import save_html_feedback_for_nominee

def parse_feedback(nominee_id, force_metadata=False, force_parse=False):
    save_html_feedback_for_nominee(nominee_id, force_metadata=force_metadata)
    input_file = f"data/feedback_html/{nominee_id}.html"
    output_file = f"data/feedback_json/{nominee_id}.json"
    if os.path.exists(output_file) and not force_parse:
        with open(output_file, "r") as json_file:
            result = json.load(json_file)
        return result

    # Read the HTML file
    with open(input_file, "r") as f:
        html_content = f.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "lxml")

    # Find the active tab pane which contains the feedback comments
    comment_tab_pane = soup.find("div", {"id": "comment", "role": "tabpanel", "class": "tab-pane active"})

    feedback_data = {}

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
                        data["position"] = get_position_short_name(dd_text)
                    elif "Feedback" in dt_text:
                        pre_tag = dd.find("pre")
                        if pre_tag:
                            data["feedback"] = pre_tag.text.strip()
                    elif "Subject" in dt_text:
                        data["subject"] = dd_text
            
            if data:
                position = data.pop("position", None)
                if position not in feedback_data:
                    feedback_data[position] = []
                feedback_data[position].append(data)

    result = {}
    result["feedback"] = feedback_data

    # Get nominee info and add it to the result dictionary
    nominee_info = get_nominee_info(nominee_id, force_metadata=force_metadata)
    result["nominee_info"] = nominee_info

    output_dir = "data/feedback_json"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Write the extracted data to a JSON file
    with open(output_file, "w") as json_file:
        json.dump(result, json_file, indent=4)
    print(f"Successfully extracted feedback from {input_file} and saved to {output_file}")

    return result

def parse_all_feedback(force_metadata=False, force_parse=False):
    for nominee in get_active_nominees(force_metadata=force_metadata):
        parse_feedback(nominee["id"], force_metadata=force_metadata, force_parse=force_parse)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse feedback from HTML files.')
    parser.add_argument('nominee_id', nargs='?', help='Optional: The nominee ID to parse feedback for.')
    parser.add_argument("-m", "--force-metadata", action="store_true", help="Force download of metadata even if file exists")
    parser.add_argument("-p", "--force-parse", action="store_true", help="Force parsing even if JSON file exists")
    args = parser.parse_args()

    if args.nominee_id:
        parse_feedback(args.nominee_id, force_metadata=args.force_metadata, force_parse=args.force_parse)
    else:
        parse_all_feedback(force_metadata=args.force_metadata, force_parse=args.force_parse)
