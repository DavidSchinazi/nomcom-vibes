#!/usr/bin/env python3

import argparse
import re
import os
import json
import google.generativeai as genai
from pathlib import Path

# --- Configuration ---

# --- Functions ---
def get_api_key():
    """Gets the Gemini API key from a file or prompts the user."""
    api_key_file = Path("data/gemini_api_key.txt")
    if api_key_file.exists():
        return api_key_file.read_text().strip()
    else:
        api_key = input("Please enter your Gemini API key: ")
        api_key_file.parent.mkdir(exist_ok=True)
        api_key_file.write_text(api_key)
        return api_key

def get_summary(feedback_text, use_pro_model=False):
    """Summarizes the feedback text using the Gemini API."""
    try:
        api_key = get_api_key()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro-latest' if use_pro_model else 'gemini-flash-latest')
        response = model.generate_content(f"Summarize the following feedback. If there are differeing opinions, try to attribute comments to the name of the person who made them. Provide the summary as an HTML snippet suitable for embedding directly into a <body> tag, without any surrounding <html>, <head>, or <body> tags, and without any markdown formatting or extra text outside the HTML.:\n\n{feedback_text}")
        summary_text = response.text
        # Extract HTML from markdown code block if present
        match = re.search(r"<[a-zA-Z][^>]*>.*</[a-zA-Z][^>]*>", summary_text, re.DOTALL)
        if match:
            return match.group(0).strip()
        # If no HTML tags found, try to remove the preamble
        preamble = "Of course. Here is a summary of the feedback in HTML format."
        if summary_text.startswith(preamble):
            return summary_text[len(preamble):].strip()
        return summary_text
    except Exception as e:
        return f"<h1>Error summarizing feedback</h1><p>{e}</p>"

def create_html_summary(summary, feedback_data, output_file):
    """Creates an HTML file with the summary and feedback."""
    feedback_with_subject = [item for item in feedback_data if "subject" in item]
    feedback_without_subject = [item for item in feedback_data if "subject" not in item]

    # TODO: right now this is incorrectly taking the name and position of
    # the first entry in the file. We need to instead get it from
    # nominees.json when parsing the HTML.
    nominee_name = feedback_data[0].get("name", "Unknown Nominee") if feedback_data else "Unknown Nominee"
    position = feedback_data[0].get("position", "Unknown Position") if feedback_data else "Unknown Position"

    with open(output_file, "w") as f:
        f.write("<html>\n<head>\n<title>Feedback Summary</title>\n</head>\n<body>\n")
        f.write("<h1>Summary for {} ({}):</h1>\n".format(nominee_name, position))
        f.write(summary)
        f.write("<h1>All Feedback for {} ({}):</h1>\n".format(nominee_name, position))
        for feedback in feedback_without_subject:
            f.write("<hr>\n")
            for key, value in feedback.items():
                if key == "position":
                    continue
                f.write(f"<b>{key.capitalize()}:</b> {value}<br>\n")
        if feedback_with_subject:
            f.write("<h2>Self Feedback</h2>\n")
        for feedback in feedback_with_subject:
            f.write("<hr>\n")
            for key, value in feedback.items():
                if key == "position":
                    continue
                f.write(f"<b>{key.capitalize()}:</b> {value}<br>\n")
        f.write("</body>\n</html>")

def sanitize_filename(name):
    """Sanitizes a string to be used as a valid filename."""
    return re.sub(r'[^a-zA-Z0-9_\.-]', '_', name)

def process_feedback_and_create_summary(input_file, output_dir):
    with open(input_file, "r") as f:
        feedback_dict = json.load(f)

    feedback_data = feedback_dict["feedback"]
    feedback_by_position = {}
    for item in feedback_data:
        position = item.get("position")
        if position:
            if position not in feedback_by_position:
                feedback_by_position[position] = []
            feedback_by_position[position].append(item)

    for position, feedback_list in feedback_by_position.items():
        feedback_text = ""
        for item in feedback_list:
            if "subject" in item:
                # Skip self feedback.
                continue
            if "feedback" not in item or "name" not in item:
                print(f"Missing information when parsing {input_file} for position '{position}': {item}")
                continue
            author = item["name"]
            contents = item["feedback"]
            feedback_text += f"\n\nFeedback from {author}:\n\n{contents}"
        summary = get_summary(feedback_text)

        base_filename = os.path.splitext(os.path.basename(input_file))[0]
        sanitized_position = sanitize_filename(position)
        output_filename = f"{base_filename}_{sanitized_position}.html"
        output_file = os.path.join(output_dir, output_filename)

        create_html_summary(summary, feedback_list, output_file)
        print(f"Successfully summarized {input_file} for position '{position}' and saved to {output_file}")

def run_summarization(file_to_summarize=None):
    input_dir = "data/feedback_json"
    output_dir = "data/summaries"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if file_to_summarize:
        input_file = os.path.join(input_dir, file_to_summarize)
        if not os.path.exists(input_file):
            print(f"Error: File {input_file} not found.")
        else:
            process_feedback_and_create_summary(input_file, output_dir)
    else:
        for filename in os.listdir(input_dir):
            if filename.endswith(".json"):
                input_file = os.path.join(input_dir, filename)
                process_feedback_and_create_summary(input_file, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Summarize feedback using Gemini.')
    parser.add_argument('input_file', nargs='?', help='Optional: Specify a single JSON file to summarize (e.g., 123.json).')
    args = parser.parse_args()
    run_summarization(args.input_file)
