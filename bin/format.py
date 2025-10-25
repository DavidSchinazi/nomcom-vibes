#!/usr/bin/env python3

import argparse
import os
import json
from feedback_parser import parse_feedback
from nominees import get_active_nominees, get_nominees_by_position, get_nominee_info
from summarize import get_summary_for_nominee_and_position

def _write_feedback(f, feedback_list):
    """Writes a list of feedback items to the file."""
    for feedback in feedback_list:
        f.write("<hr>\n")
        name = feedback["name"]
        email = feedback["email"]
        date = feedback["date"]
        contents = feedback["feedback"]
        f.write(f'<span title="{date}"><a href="https://datatracker.ietf.org/person/{email}"><b>{name}</b></a></span>: {contents}\n')

def create_summary_for_nominee_and_position(summary, feedback_list, input_file, output_file, feedback_dict, position):
    """Creates an HTML file with the summary and feedback."""
    feedback_with_subject = [item for item in feedback_list if "subject" in item]
    feedback_without_subject = [item for item in feedback_list if "subject" not in item]

    nominee_info = feedback_dict["nominee_info"]
    nominee_name = nominee_info["name"]

    with open(output_file, "w") as f:
        f.write("<html>\n<head>\n<title>Feedback Summary</title>\n</head>\n<body>\n")
        f.write(f'<h1>AI Summary for {nominee_name} for <a href="{position}.html" style="color:black; text-decoration:none;">{position}</a>:</h1>\n')
        f.write(summary)
        if feedback_without_subject:
            f.write("<h1>Actual Feedback:</h1>\n")
            _write_feedback(f, feedback_without_subject)
        questionnaire = feedback_dict["questionnaires"].get(position)
        if questionnaire:
            f.write("<h1>Questionnaire:</h1>\n")
            f.write(f'<pre style="white-space: pre-wrap;">{questionnaire}</pre>\n')
        if feedback_with_subject:
            f.write("<h2>Self Feedback</h2>\n")
            _write_feedback(f, feedback_with_subject)
        f.write("</body>\n</html>")
    print(f"Successfully summarized {input_file} for {position} and saved to {output_file}")

def create_summary_for_nominee(nominee_id, force_metadata=False, force_feedback=False, force_parse=False, force_summarize=False):
    print(f"Creating summary for nominee {nominee_id}")
    output_dir = "data/summaries"
    input_file = os.path.join("data/feedback_json", f"{nominee_id}.json")

    # Make sure the parsed JSON is there.
    parse_feedback(nominee_id, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(input_file, "r") as f:
        feedback_dict = json.load(f)

    for position, state in feedback_dict["nominee_info"]["positions"].items():
        if state != "accepted":
            continue
        feedback_list = feedback_dict["feedback"].get(position, [])
        summary = get_summary_for_nominee_and_position(nominee_id, position, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, force_summarize=force_summarize)
        output_filename = f"{nominee_id}_{position}.html"
        output_file = os.path.join(output_dir, output_filename)

        create_summary_for_nominee_and_position(summary, feedback_list, input_file, output_file, feedback_dict, position)

def create_summary_for_position(position, force_metadata=False):
    print(f"Creating summary for position {position}")
    output_dir = "data/summaries"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    nominees_by_position = get_nominees_by_position(force_metadata=force_metadata)
    nominee_ids = nominees_by_position.get(position)
    if not nominee_ids:
        print(f"No nominees found for position {position}")
        return

    output_filename = f"{position}.html"
    output_file = os.path.join(output_dir, output_filename)

    with open(output_file, "w") as f:
        f.write("<html>\n<head>\n<title>Nominee Summary</title>\n</head>\n<body>\n")
        f.write(f'<h1><a href="index.html" style="color:black; text-decoration:none;">Nominees</a> for {position}:</h1>\n')
        f.write("<ul>\n")
        for nominee_id in nominee_ids:
            nominee_info = get_nominee_info(nominee_id, force_metadata=force_metadata)
            nominee_name = nominee_info["name"]
            summary_file = f"{nominee_id}_{position}.html"
            f.write(f'<li><a href="{summary_file}">{nominee_name}</a></li>\n')
        f.write("</ul>\n")
        f.write("</body>\n</html>")
    print(f"Successfully created summary for position {position} and saved to {output_file}")


def create_overall_summary(force_metadata=False):
    print("Creating overall summary")
    output_dir = "data/summaries"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    positions = get_nominees_by_position(force_metadata=force_metadata).keys()
    output_file = os.path.join(output_dir, "index.html")

    with open(output_file, "w") as f:
        f.write("<html>\n<head>\n<title>NomCom Summary</title>\n</head>\n<body>\n")
        f.write("<h1>Positions:</h1>\n")
        f.write("<ul>\n")
        for position in positions:
            f.write(f'<li><a href="{position}.html">{position}</a></li>\n')
        f.write("</ul>\n")
        f.write("</body>\n</html>")
    print(f"Successfully created overall summary and saved to {output_file}")


def run_formatting(nominee_id=None, position=None, force_metadata=False, force_feedback=False, force_parse=False, force_summarize=False):
    if position:
        create_summary_for_position(position, force_metadata=force_metadata)
    elif nominee_id:
        create_summary_for_nominee(nominee_id, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, force_summarize=force_summarize)
    else:
        for nominee in get_active_nominees(force_metadata=force_metadata):
            create_summary_for_nominee(nominee["id"], force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, force_summarize=force_summarize)
        for position in get_nominees_by_position(force_metadata=force_metadata):
            create_summary_for_position(position, force_metadata=force_metadata)
        create_overall_summary(force_metadata=force_metadata)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Format feedback summaries.')
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

    run_formatting(nominee_id=nominee_id, position=position, force_metadata=args.force_metadata, force_feedback=args.force_feedback, force_parse=args.force_parse, force_summarize=args.force_summarize)
