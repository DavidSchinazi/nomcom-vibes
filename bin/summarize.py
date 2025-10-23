#!/usr/bin/env python3

import re
import os
import json
import google.generativeai as genai
from pathlib import Path
from parse_html_feedback import parse_feedback

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
        response = model.generate_content(f"Summarize the following feedback. If there are differing opinions, try to attribute comments to the name of the person who made them. Provide the summary as an HTML snippet suitable for embedding directly into a <body> tag, without any surrounding <html>, <head>, or <body> tags, and without any markdown formatting or extra text outside the HTML.:\n\n{feedback_text}")
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

def get_summary_for_nominee_and_position(nominee_id, position, force_download=False):
    """Gets the summary for a given nominee and position."""
    feedback_dict = parse_feedback(nominee_id, force_download=force_download)

    feedback_by_position = feedback_dict.get("feedback", {})
    feedback_list = feedback_by_position.get(position, [])

    feedback_text = ""
    for item in feedback_list:
        if "subject" in item:
            # Skip self feedback.
            continue
        if "feedback" not in item or "name" not in item:
            print(f"Missing information when parsing feedback for nominee {nominee_id} for position '{position}': {item}")
            continue
        author = item["name"]
        contents = item["feedback"]
        feedback_text += f"\n\nFeedback from {author}:\n\n{contents}"

    summary_filename = f"{nominee_id}_{position}.txt"
    summary_dir = "data/ai_summaries"
    if not os.path.exists(summary_dir):
        os.makedirs(summary_dir)
    summary_file = os.path.join(summary_dir, summary_filename)

    if os.path.exists(summary_file):
        with open(summary_file, "r") as f:
            summary = f.read()
    elif not feedback_text.strip():
        summary = "<p>No feedback to summarize for this position.</p>"
    else:
        summary = get_summary(feedback_text)
        with open(summary_file, "w") as f:
            f.write(summary)
    return summary
