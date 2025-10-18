
import json
import argparse
from bs4 import BeautifulSoup
import re

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description='Parse feedback from an HTML file and output to JSON.')
parser.add_argument('input_file', help='The input HTML file to parse.')
parser.add_argument('output_file', help='The output JSON file to write to.')
args = parser.parse_args()

# Read the HTML file
with open(args.input_file, "r") as f:
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
                if dt_text == "From":
                    # Extract name and email more carefully
                    full_text = dd.text
                    match = re.match(r"(.*?)\s*<([^>]+)>", full_text)
                    if match:
                        data["name"] = match.group(1).strip()
                        data["email"] = match.group(2).strip()
                    else:
                        data["name"] = dd.contents[0].strip().replace('<','').strip()
                        email_tag = dd.find("a")
                        if email_tag and "mailto:" in email_tag.get("href", ""):
                            data["email"] = email_tag.text.strip()

                elif dt_text == "Date":
                    data["date"] = dd_text
                elif dt_text == "Positions":
                    data["position"] = dd_text
                elif dt_text == "Feedback":
                    pre_tag = dd.find("pre")
                    if pre_tag:
                        data["feedback"] = pre_tag.text.strip()
        
        if data:
            feedback_data.append(data)

# Write the extracted data to a JSON file
with open(args.output_file, "w") as json_file:
    json.dump(feedback_data, json_file, indent=4)

print(f"Successfully extracted feedback from {args.input_file} and saved to {args.output_file}")
