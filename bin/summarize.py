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

def get_summary(feedback_text):
    """Summarizes the feedback text using the Gemini API."""
    try:
        api_key = get_api_key()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro-latest')
        response = model.generate_content(f"Summarize the following feedback. Provide the summary as an HTML snippet suitable for embedding directly into a <body> tag, without any surrounding <html>, <head>, or <body> tags, and without any markdown formatting or extra text outside the HTML.:\n\n{feedback_text}")
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

    with open(output_file, "w") as f:
        f.write("<html>\n<head>\n<title>Feedback Summary</title>\n</head>\n<body>\n")
        f.write("<h1>Summary</h1>\n")
        f.write(summary)
        f.write("<h1>All Feedback</h1>\n")
        for feedback in feedback_without_subject:
            f.write("<hr>\n")
            for key, value in feedback.items():
                f.write(f"<b>{key.capitalize()}:</b> {value}<br>\n")
        if feedback_with_subject:
            f.write("<h2>Self Feedback</h2>\n")
        for feedback in feedback_with_subject:
            f.write("<hr>\n")
            for key, value in feedback.items():
                f.write(f"<b>{key.capitalize()}:</b> {value}<br>\n")
        f.write("</body>\n</html>")

def process_feedback_and_create_summary(input_file, output_file):
    with open(input_file, "r") as f:
        feedback_data = json.load(f)

    feedback_text = "\n".join([item.get("feedback", "") for item in feedback_data if "subject" not in item])
    summary = get_summary(feedback_text)

    create_html_summary(summary, feedback_data, output_file)
    print(f"Successfully summarized {input_file} and saved to {output_file}")

def run_summarization(file_to_summarize=None):
    input_dir = "data/feedback_json"
    output_dir = "data/summaries"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if file_to_summarize:
        filename = file_to_summarize
        input_file = os.path.join(input_dir, filename)
        output_file = os.path.join(output_dir, filename.replace(".json", ".html"))

        if not os.path.exists(input_file):
            print(f"Error: File {input_file} not found.")
        else:
            process_feedback_and_create_summary(input_file, output_file)
    else:
        for filename in os.listdir(input_dir):
            if filename.endswith(".json"):
                input_file = os.path.join(input_dir, filename)
                output_file = os.path.join(output_dir, filename.replace(".json", ".html"))
                process_feedback_and_create_summary(input_file, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Summarize feedback using Gemini.')
    parser.add_argument('input_file', help='Optional: Specify a single JSON file to summarize (e.g., 123.json).')
    args = parser.parse_args()
    run_summarization(args.input_file)
