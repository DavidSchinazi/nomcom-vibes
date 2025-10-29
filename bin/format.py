#!/usr/bin/env python3

import argparse
import os
import json
from feedback_parser import parse_feedback
from nominees import get_active_nominees, get_nominees_by_position, get_nominee_info
from summarize import are_summaries_enabled, get_ai_summary_for_nominee_and_position, get_ai_summary_for_position
from positions import get_position_short_name, get_position_full_name

POSITION_COLOR = "#777777"

def wrap_in_html(title, body):
    """Wraps the given body in a basic HTML structure."""
    with open("data/template.html", "r") as f:
        template = f.read()
    return template.format(title=title, body=body)

def create_page_for_nominee_and_position(summary, feedback_list, input_file, output_file, feedback_dict, position_short_name):
    """Creates an HTML file with the summary and feedback."""
    feedback_with_subject = [item for item in feedback_list if "subject" in item]
    feedback_without_subject = [item for item in feedback_list if "subject" not in item]

    nominee_info = feedback_dict["nominee_info"]
    nominee_name = nominee_info["name"]
    position_full_name = get_position_full_name(position_short_name)

    body = f'<h1>{nominee_name} – <a href="{position_short_name}.html" style="color: {POSITION_COLOR}; text-decoration: none;">{position_full_name}</a></h1>\n'
    if summary:
        body += f'<div style="background-color: #ffdddd;">\n'
        body += f'<h2 onclick="toggleSection(\'ai-summary-content\')" style="cursor: pointer;"><span id="ai-summary-toggle" class="toggle-button">&#9660;</span>AI Summary:</h2>\n'
        body += f'<div id="ai-summary-content">{summary}</div>\n'
        body += f'</div>\n'
    if feedback_without_subject:
        body += '<div style="background-color: #ddffdd;">\n'
        body += f'<h2 onclick="toggleSection(\'community-feedback-content\')" style="cursor: pointer;"><span id="community-feedback-toggle" class="toggle-button">&#9660;</span>Community Feedback:</h2>\n'
        body += '<div id="community-feedback-content">\n'
        for feedback in feedback_without_subject:
            name = feedback["name"]
            email = feedback["email"]
            date = feedback["date"]
            contents = feedback["feedback"]
            body += f'<div class="feedback">\n'
            body += f'<p><a href="https://datatracker.ietf.org/person/{email}" class="feedback-author">{name}</a> <span class="feedback-date">({date})</span></p>\n'
            body += f'<p>{contents}</p>\n'
            body += f'</div>\n'
        body += '</div>\n'
        body += '</div>\n'
    questionnaire = feedback_dict["questionnaires"].get(position_short_name)
    if questionnaire:
        body += '<div style="background-color: #eeeeee;">\n'
        body += f'<h2 onclick="toggleSection(\'questionnaire-content\')" style="cursor: pointer;"><span id="questionnaire-toggle" class="toggle-button">&#9660;</span>Questionnaire:</h2>\n'
        body += f'<div id="questionnaire-content"><pre class="questionnaire">{questionnaire}</pre></div>\n'
        body += '</div>\n'
    if feedback_with_subject:
        body += f'<h2 onclick="toggleSection(\'self-feedback-content\')" style="cursor: pointer;"><span id=\"self-feedback-toggle\" class=\"toggle-button\">&#9660;</span>Self Feedback:</h2>\n'
        body += '<div id="self-feedback-content">\n'
        for feedback in feedback_with_subject:
            name = feedback["name"]
            email = feedback["email"]
            date = feedback["date"]
            contents = feedback["feedback"]
            body += f'<div class="feedback">\n'
            body += f'<p><a href="https://datatracker.ietf.org/person/{email}" class="feedback-author">{name}</a> <span class="feedback-date">({date})</span></p>\n'
            body += f'<p>{contents}</p>\n'
            body += f'</div>\n'
        body += '</div>\n'

    with open(output_file, "w") as f:
        f.write(wrap_in_html(f"Feedback Summary for {nominee_name}", body))
    print(f"Successfully summarized {input_file} for {position_short_name} and saved to {output_file}")

def create_page_for_nominee(nominee_id, force_metadata=False, force_feedback=False, force_parse=False, redo_summaries=False, summaries_forced=None):
    print(f"Creating summary for nominee {nominee_id}")
    output_dir = "data/summaries"
    input_file = os.path.join("data/feedback_json", f"{nominee_id}.json")

    # Make sure the parsed JSON is there.
    parse_feedback(nominee_id, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(input_file, "r") as f:
        feedback_dict = json.load(f)

    for position_short_name, state in feedback_dict["nominee_info"]["positions"].items():
        if state != "accepted":
            continue
        feedback_list = feedback_dict["feedback"].get(position_short_name, [])
        summary = get_ai_summary_for_nominee_and_position(nominee_id, position_short_name, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, redo_summaries=redo_summaries, summaries_forced=summaries_forced)
        output_filename = f"{nominee_id}_{position_short_name}.html"
        output_file = os.path.join(output_dir, output_filename)

        create_page_for_nominee_and_position(summary, feedback_list, input_file, output_file, feedback_dict, position_short_name)

def create_page_for_position(position_short_name, force_metadata=False, force_feedback=False, force_parse=False, redo_summaries=False, summaries_forced=None):
    position_full_name = get_position_full_name(position_short_name)
    print(f"Creating summary for position {position_full_name}")
    output_dir = "data/summaries"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    nominees_by_position = get_nominees_by_position(force_metadata=force_metadata)
    nominee_ids = nominees_by_position.get(position_short_name)
    body = f'<h1><a href="index.html" style="color: {POSITION_COLOR}; text-decoration: none;">Nominees</a> for {position_full_name}:</h1>\n'
    if not nominee_ids:
        print(f"No nominees found for position {position_full_name}")
        return

    output_filename = f"{position_short_name}.html"
    output_file = os.path.join(output_dir, output_filename)

    body += '<div style="background-color: #ddeeff; padding: 1rem;">\n'
    body += "<ul style=\"font-size: 1.2em;\">\n"
    for nominee_id in nominee_ids:
        nominee_info = get_nominee_info(nominee_id, force_metadata=force_metadata)
        nominee_name = nominee_info["name"]
        summary_file = f"{nominee_id}_{position_short_name}.html"
        body += f'<li><a href="{summary_file}">{nominee_name}</a></li>\n'
    body += "</ul>\n"
    body += '</div>\n'
    summary = get_ai_summary_for_position(position_short_name, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, redo_summaries=redo_summaries, summaries_forced=summaries_forced)
    if summary:
        body += f'<div style="background-color: #ffdddd;">\n'
        body += f'<h2 onclick="toggleSection(\'ai-summary-content\')" style="cursor: pointer;"><span id="ai-summary-toggle" class="toggle-button">&#9660;</span>AI Summary for this position:</h2>\n'
        body += f'<div id="ai-summary-content">{summary}</div>\n'
        body += f'</div>\n'

    with open(output_file, "w") as f:
        f.write(wrap_in_html(f"Nominee Summary for {position_full_name}", body))
    print(f"Successfully created summary for position {position_full_name} and saved to {output_file}")


def create_index_page(force_metadata=False):
    output_dir = "data/summaries"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    positions = get_nominees_by_position(force_metadata=force_metadata).keys()
    output_file = os.path.join(output_dir, "index.html")

    body = "<h1>Positions:</h1>\n"
    body += "<ul>\n"
    for position_short_name in positions:
        position_full_name = get_position_full_name(position_short_name)
        body += f'<li><a href="{position_short_name}.html">{position_full_name}</a></li>\n'
    body += "</ul>\n"

    with open(output_file, "w") as f:
        f.write(wrap_in_html("NomCom Summary", body))
    print(f"Successfully created overall summary and saved to {output_file}")


def run_formatting(nominee_id=None, position_short_name=None, force_metadata=False, force_feedback=False, force_parse=False, redo_summaries=False, summaries_forced=None):
    if position_short_name:
        create_page_for_position(position_short_name, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, redo_summaries=redo_summaries, summaries_forced=summaries_forced)
    elif nominee_id:
        create_page_for_nominee(nominee_id, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, redo_summaries=redo_summaries, summaries_forced=summaries_forced)
    else:
        for nominee in get_active_nominees(force_metadata=force_metadata):
            create_page_for_nominee(nominee["id"], force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, redo_summaries=redo_summaries, summaries_forced=summaries_forced)
        for position_short_name in get_nominees_by_position(force_metadata=force_metadata):
            create_page_for_position(position_short_name, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, redo_summaries=redo_summaries, summaries_forced=summaries_forced)
        create_index_page(force_metadata=force_metadata)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Format feedback summaries.')
    parser.add_argument('identifier', nargs='?', help='Optional: Specify a single nominee ID (e.g., 123) or a position (e.g., iab) to format.')
    parser.add_argument("-m", "--force-metadata", action="store_true", help="Force download of metadata even if file exists")
    parser.add_argument("-f", "--force-feedback", action="store_true", help="Force download of feedback even if file exists")
    parser.add_argument("-p", "--force-parse", action="store_true", help="Force parsing even if JSON file exists")
    parser.add_argument("-s", "--redo-summaries", action="store_true", help="Perform summarization even if summary file exists")
    parser.add_argument("-x", "--add-summaries", action='store_const', const=True, default=None, dest="summaries_forced", help="Add summarization even if disabled")
    parser.add_argument("-z", "--no-summaries", action='store_const', const=False, default=None, dest="summaries_forced", help="Disable summarization even if enabled")
    args = parser.parse_args()

    nominee_id = None
    position_short_name = None
    if args.identifier:
        try:
            nominee_id = int(args.identifier)
        except ValueError:
            position_short_name = args.identifier

    run_formatting(nominee_id=nominee_id, position_short_name=position_short_name, force_metadata=args.force_metadata, force_feedback=args.force_feedback, force_parse=args.force_parse, redo_summaries=args.redo_summaries, summaries_forced=args.summaries_forced)
