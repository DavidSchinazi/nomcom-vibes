#!/usr/bin/env python3

import re
import os
import json
from pathlib import Path
from feedback_parser import parse_feedback_for_nominee
from nominees import get_nominee_info, get_nominees_by_position, get_active_nominees
from positions import get_position_full_name


GEMINI_SETTINGS = None
GEMINI_SETTINGS_FILE = "config/gemini_settings.json"

def save_gemini_settings(settings):
    global GEMINI_SETTINGS
    GEMINI_SETTINGS = settings
    os.makedirs(os.path.dirname(GEMINI_SETTINGS_FILE), exist_ok=True)
    with open(GEMINI_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(GEMINI_SETTINGS, f, indent=4)

def get_gemini_settings():
    global GEMINI_SETTINGS
    if not GEMINI_SETTINGS:
        if os.path.exists(GEMINI_SETTINGS_FILE):
            with open(GEMINI_SETTINGS_FILE, "r", encoding="utf-8") as f:
                GEMINI_SETTINGS = json.load(f)
        else:
            save_gemini_settings({
                "enabled": False,
                "api_key": "",
            })
    return GEMINI_SETTINGS

def get_gemini_api_key(summaries_forced=None):
    if are_summaries_enabled(summaries_forced=summaries_forced):
        settings = get_gemini_settings()
        api_key = settings.get("api_key", "").strip()
        if not api_key:
            api_key = input("Please enter your Gemini API key: ").strip()
            settings["api_key"] = api_key
            save_gemini_settings(settings)
        return api_key
    return None

def save_gemini_api_key(api_key):
    settings = get_gemini_settings()
    settings["api_key"] = api_key
    save_gemini_settings(settings)

def set_enable_summaries(enabled):
    settings = get_gemini_settings()
    settings["enabled"] = enabled
    save_gemini_settings(settings)

def are_summaries_enabled(summaries_forced=None):
    if summaries_forced is not None:
        return summaries_forced
    settings = get_gemini_settings()
    return settings.get("enabled", False)

def get_ai_summary(prompt, use_pro_model=False, summaries_forced=None):
    """Summarizes the feedback text using the Gemini API."""
    try:
        api_key = get_gemini_api_key(summaries_forced=summaries_forced)
        import google.generativeai as genai
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

def get_ai_summary_for_nominee_and_position(nominee_id, position, force_metadata=False, force_feedback=False, force_parse=False, redo_summaries=False, summaries_forced=None):
    """Gets the summary for a given nominee and position."""
    if not get_gemini_api_key(summaries_forced=summaries_forced):
        return None
    nominee_info = get_nominee_info(nominee_id, force_metadata=force_metadata)
    nominee_name = nominee_info['name']
    feedback_dict = parse_feedback_for_nominee(nominee_id, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse)

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

    if os.path.exists(summary_file) and not redo_summaries:
        with open(summary_file, "r", encoding="utf-8") as f:
            summary = f.read()
    elif not feedback_text.strip():
        summary = "<p>No feedback for this position.</p>"
    else:
        prompt = f"Summarize the following feedback for {nominee_name} for the {position} position. If there are differing opinions, try to attribute comments to the name of the person who made them. Provide the summary as an HTML snippet suitable for embedding directly into a <body> tag, without any surrounding <html>, <head>, or <body> tags, and without any markdown formatting or extra text outside the HTML. Use <h3> for main sections and <h4> for subsections.:\n\n{feedback_text}"
        summary, success = get_ai_summary(prompt)
        if success:
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary)
    return summary

def get_ai_summary_for_position(position, force_metadata=False, force_feedback=False, force_parse=False, redo_summaries=False, summaries_forced=None):
    """Gets the summary for a given position."""
    if not get_gemini_api_key(summaries_forced=summaries_forced):
        return None
    nominees_by_position = get_nominees_by_position(force_metadata=force_metadata)
    nominee_ids = nominees_by_position.get(position, [])

    if not nominee_ids:
        return f"<h1>No nominees found for position {position}</h1>"

    all_feedback_text = ""
    for nominee_id in nominee_ids:
        nominee_info = get_nominee_info(nominee_id, force_metadata=force_metadata)
        all_feedback_text += f"\n\n--- Feedback for {nominee_info['name']} ---\n\n"
        feedback_dict = parse_feedback_for_nominee(nominee_id, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse)
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

    if os.path.exists(summary_file) and not redo_summaries:
        with open(summary_file, "r", encoding="utf-8") as f:
            summary = f.read()
    elif not all_feedback_text.strip():
        summary = "<p>No feedback for this position.</p>"
    else:
        if position == 'IAB':
            prompt = "We need to pick six people for the role of Internet Architecture Board (IAB) Member. Based on the feedback for these nominees, who are the six that the community thinks are the best choice?"
        else:
            position_full = get_position_full_name(position)
            prompt = f"We need to pick one person for the role of {position_full}. Based on the following feedback for these nominees, who does the community think is the best choice?"
        prompt += f" If there are differing opinions, try to attribute comments to the name of the person who made them. Provide the summary as an HTML snippet suitable for embedding directly into a <body> tag, without any surrounding <html>, <head>, or <body> tags, and without any markdown formatting or extra text outside the HTML. Use <h3> for main sections and <h4> for subsections.:\n\n{all_feedback_text}"
        summary, success = get_ai_summary(prompt, use_pro_model=True)
        if success:
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary)
    return summary

def run_summarize(nominee_id=None, position=None, force_metadata=False, force_feedback=False, force_parse=False, redo_summaries=False, summaries_forced=None):
    if position:
        summary = get_ai_summary_for_position(position, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, redo_summaries=redo_summaries, summaries_forced=summaries_forced)
        print(summary)
    elif nominee_id:
        nominee_info = get_nominee_info(nominee_id, force_metadata=force_metadata)
        for position, state in nominee_info["positions"].items():
            if state == 'accepted':
                summary = get_ai_summary_for_nominee_and_position(nominee_id, position, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, redo_summaries=redo_summaries, summaries_forced=summaries_forced)
                print(f"--- Summary for {nominee_info['name']} for {position} ---")
                print(summary)
    else:
        for nominee in get_active_nominees(force_metadata=force_metadata):
             nominee_info = get_nominee_info(nominee['id'], force_metadata=force_metadata)
             for position, state in nominee_info["positions"].items():
                 if state == 'accepted':
                    summary = get_ai_summary_for_nominee_and_position(nominee['id'], position, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, redo_summaries=redo_summaries, summaries_forced=summaries_forced)
                    print(f"--- Summary for {nominee_info['name']} for {position} ---")
                    print(summary)
        for position in get_nominees_by_position(force_metadata=force_metadata):
            summary = get_ai_summary_for_position(position, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, redo_summaries=redo_summaries, summaries_forced=summaries_forced)
            print(f"--- Summary for position {position} ---")
            print(summary)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Summarize feedback for a nominee and position.')
    parser.add_argument('identifier', nargs='?', help='Optional: Specify a single nominee ID (e.g., 123) or a position (e.g., iab) to format.')
    parser.add_argument("-m", "--force-metadata", action="store_true", help="Force download of metadata even if file exists")
    parser.add_argument("-f", "--force-feedback", action="store_true", help="Force download of feedback even if file exists")
    parser.add_argument("-p", "--force-parse", action="store_true", help="Force parsing even if JSON file exists")
    parser.add_argument("-s", "--redo-summaries", action="store_true", help="Perform summarization even if summary file exists")
    parser.add_argument("-a", "--force-all", action="store_true", help="Get latest feedback and redo subsequent operations")
    parser.add_argument("-x", "--add-summaries", action='store_const', const=True, default=None, dest="summaries_forced", help="[BETA] Add summarization even if disabled")
    parser.add_argument("-z", "--no-summaries", action='store_const', const=False, default=None, dest="summaries_forced", help="Disable summarization even if enabled")
    parser.add_argument("--enable-summaries", action='store_const', const=True, default=None, dest="summaries_enabled", help="[BETA] Add summarization even if disabled")
    parser.add_argument("--disable-summaries", action='store_const', const=False, default=None, dest="summaries_enabled", help="Disable summarization even if enabled")
    args = parser.parse_args()

    if args.force_all:
        args.force_feedback = True
        args.force_parse = True
        args.redo_summaries = True

    if args.summaries_enabled is not None:
        print(f"Setting enable_summaries to {args.summaries_enabled}")
        set_enable_summaries(args.summaries_enabled)
        if args.summaries_enabled:
            get_gemini_api_key()
    else:
        nominee_id = None
        position = None
        if args.identifier:
            try:
                nominee_id = int(args.identifier)
            except ValueError:
                position = args.identifier

        run_summarize(nominee_id=nominee_id, position=position, force_metadata=args.force_metadata, force_feedback=args.force_feedback, force_parse=args.force_parse, redo_summaries=args.redo_summaries, summaries_forced=args.summaries_forced)
