#!/usr/bin/env python3
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
        response = model.generate_content(f"Summarize the following feedback:\n\n{feedback_text}")
        return response.text
    except Exception as e:
        return f"Error summarizing feedback: {e}"

def create_html_summary(summary, feedback_data, output_file):
    """Creates an HTML file with the summary and feedback."""
    with open(output_file, "w") as f:
        f.write("<html>\n<head>\n<title>Feedback Summary</title>\n</head>\n<body>\n")
        f.write("<h1>Summary</h1>\n")
        f.write(f"<p>{summary}</p>\n")
        f.write("<h1>All Feedback</h1>\n")
        for feedback in feedback_data:
            f.write("<hr>\n")
            for key, value in feedback.items():
                f.write(f"<b>{key.capitalize()}:</b> {value}<br>\n")
        f.write("</body>\n</html>")

if __name__ == "__main__":
    input_dir = "data/feedback_json"
    output_dir = "data/summaries"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, filename.replace(".json", ".html"))

            with open(input_file, "r") as f:
                feedback_data = json.load(f)

            feedback_text = "\n".join([item.get("feedback", "") for item in feedback_data])
            summary = get_summary(feedback_text)

            create_html_summary(summary, feedback_data, output_file)
            print(f"Successfully summarized {input_file} and saved to {output_file}")
