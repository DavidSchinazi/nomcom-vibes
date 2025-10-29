#!/usr/bin/env python3

import re
import os
import json
import google.generativeai as genai
from pathlib import Path
from feedback_parser import parse_feedback
from nominees import get_nominee_info, get_nominees_by_position, get_active_nominees


GEMINI_API_KEY = None

def get_gemini_api_key():
    global GEMINI_API_KEY
    if not GEMINI_API_KEY:
        api_key_file = Path("data/gemini_api_key.txt")
        if api_key_file.exists():
            GEMINI_API_KEY = api_key_file.read_text().strip()
        else:
            GEMINI_API_KEY = input("Please enter your Gemini API key: ")
            api_key_file.parent.mkdir(exist_ok=True)
            api_key_file.write_text(GEMINI_API_KEY)
    return GEMINI_API_KEY

def get_ai_summary(prompt, use_pro_model=False):
    """Summarizes the feedback text using the Gemini API."""
    try:
        api_key = get_gemini_api_key()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro-latest' if use_pro_model else 'gemini-flash-latest')
        response = model.generate_content(prompt)
        summary_text = response.text
        # Extract HTML from markdown code block if present
        match = re.search(r"<[a-zA-Z][^>]*>.*</[a-zA-Z][^>]*>", summary_text, re.DOTALL)
        if match:
            return match.group(0).strip(), True
        # If no HTML tags found, try to remove the preamble
        preamble = "Of course. Here is a summary of the feedback in HTML format."
        if summary_text.startswith(preamble):
            return summary_text[len(preamble):].strip(), True
        return summary_text, True
    except Exception as e:
        return f"<h1>Error summarizing feedback</h1><p>{e}</p>", False

def get_ai_summary_for_nominee_and_position(nominee_id, position, force_metadata=False, force_feedback=False, force_parse=False, force_summarize=False):
    """Gets the summary for a given nominee and position."""
    nominee_info = get_nominee_info(nominee_id, force_metadata=force_metadata)
    nominee_name = nominee_info['name']
    feedback_dict = parse_feedback(nominee_id, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse)

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

    if os.path.exists(summary_file) and not force_summarize:
        with open(summary_file, "r") as f:
            summary = f.read()
    elif not feedback_text.strip():
        summary = "<p>No feedback for this position.</p>"
    else:
        prompt = f"Summarize the following feedback for {nominee_name} for the {position} position. If there are differing opinions, try to attribute comments to the name of the person who made them. Provide the summary as an HTML snippet suitable for embedding directly into a <body> tag, without any surrounding <html>, <head>, or <body> tags, and without any markdown formatting or extra text outside the HTML:\n\n{feedback_text}"
        summary, success = get_ai_summary(prompt)
        if success:
            with open(summary_file, "w") as f:
                f.write(summary)
    return summary

def get_ai_summary_for_position(position, force_metadata=False, force_feedback=False, force_parse=False, force_summarize=False):
    """Gets the summary for a given position."""
    nominees_by_position = get_nominees_by_position(force_metadata=force_metadata)
    nominee_ids = nominees_by_position.get(position, [])

    if not nominee_ids:
        return f"<h1>No nominees found for position {position}</h1>"

    all_feedback_text = ""
    for nominee_id in nominee_ids:
        nominee_info = get_nominee_info(nominee_id, force_metadata=force_metadata)
        all_feedback_text += f"\n\n--- Feedback for {nominee_info['name']} ---\n\n"
        feedback_dict = parse_feedback(nominee_id, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse)
        feedback_by_position = feedback_dict.get("feedback", {})
        feedback_list = feedback_by_position.get(position, [])

        for item in feedback_list:
            if "subject" in item:
                # Skip self feedback.
                continue
            if "feedback" not in item or "name" not in item:
                print(f"Missing information when parsing feedback for nominee {nominee_id} for position '{position}': {item}")
                continue
            author = item["name"]
            contents = item["feedback"]
            all_feedback_text += f"\n\nFeedback from {author}:\n\n{contents}"

    summary_filename = f"{position}.txt"
    summary_dir = "data/ai_summaries"
    if not os.path.exists(summary_dir):
        os.makedirs(summary_dir)
    summary_file = os.path.join(summary_dir, summary_filename)

    if os.path.exists(summary_file) and not force_summarize:
        with open(summary_file, "r") as f:
            summary = f.read()
    elif not all_feedback_text.strip():
        summary = "<p>No feedback for this position.</p>"
    else:
        prompt = f"Based on the following feedback for multiple candidates for the {position} position, who does the community think is the best choice? If there are differing opinions, try to attribute comments to the name of the person who made them. Provide the summary as an HTML snippet suitable for embedding directly into a <body> tag, without any surrounding <html>, <head>, or <body> tags, and without any markdown formatting or extra text outside the HTML:\n\n{all_feedback_text}"
        summary, success = get_ai_summary(prompt, use_pro_model=True)
        if success:
            with open(summary_file, "w") as f:
                f.write(summary)
    return summary

def run_summarize(nominee_id=None, position=None, force_metadata=False, force_feedback=False, force_parse=False, force_summarize=False):
    if position:
        summary = get_ai_summary_for_position(position, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, force_summarize=force_summarize)
        print(summary)
    elif nominee_id:
        nominee_info = get_nominee_info(nominee_id, force_metadata=force_metadata)
        for position, state in nominee_info["positions"].items():
            if state == 'accepted':
                summary = get_ai_summary_for_nominee_and_position(nominee_id, position, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, force_summarize=force_summarize)
                print(f"--- Summary for {nominee_info['name']} for {position} ---")
                print(summary)
    else:
        for nominee in get_active_nominees(force_metadata=force_metadata):
             nominee_info = get_nominee_info(nominee['id'], force_metadata=force_metadata)
             for position, state in nominee_info["positions"].items():
                 if state == 'accepted':
                    summary = get_ai_summary_for_nominee_and_position(nominee['id'], position, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, force_summarize=force_summarize)
                    print(f"--- Summary for {nominee_info['name']} for {position} ---")
                    print(summary)
        for position in get_nominees_by_position(force_metadata=force_metadata):
            summary = get_ai_summary_for_position(position, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, force_summarize=force_summarize)
            print(f"--- Summary for position {position} ---")
            print(summary)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Summarize feedback for a nominee and position.')
    parser.add_argument('identifier', nargs='?', help='Optional: Specify a single nominee ID (e.g., 123) or a position (e.g., iab) to format.')
    parser.add_argument("-m", "--force-metadata", action="store_true", help="Force download of metadata even if file exists")
    parser.add_argument("-f", "--force-feedback", action="store_true", help="Force download of feedback even if file exists")
    parser.add_argument("-p", "--force-parse", action="store_true", help="Force parsing even if JSON file exists")
    parser.add_argument("-s", "--force-summarize", action="store_true", help="Force summarization even if summary file exists")
    args = parser.parse_args()

    nominee_id = None
    position = None
    if args.identifier:
        try:
            nominee_id = int(args.identifier)
        except ValueError:
            position = args.identifier

    run_summarize(nominee_id=nominee_id, position=position, force_metadata=args.force_metadata, force_feedback=args.force_feedback, force_parse=args.force_parse, force_summarize=args.force_summarize)
