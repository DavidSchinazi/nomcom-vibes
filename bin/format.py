#!/usr/bin/env python3

import argparse
import os
import json
from get_nominees import get_nominees
from summarize import get_summary_for_nominee_and_position

def create_html_summary(summary, feedback_data, input_file, output_file, nominee_name, position):
    """Creates an HTML file with the summary and feedback."""
    feedback_with_subject = [item for item in feedback_data if "subject" in item]
    feedback_without_subject = [item for item in feedback_data if "subject" not in item]

    if not feedback_without_subject:
        return

    with open(output_file, "w") as f:
        f.write("<html>\n<head>\n<title>Feedback Summary</title>\n</head>\n<body>\n")
        f.write("<h1>Summary for {} ({}):</h1>\n".format(nominee_name, position))
        f.write(summary)
        f.write("<h1>All Feedback for {} ({}):</h1>\n".format(nominee_name, position))
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
    print(f"Successfully summarized {input_file} for position '{position}' and saved to {output_file}")

def create_summary_for_nominee(nominee_id, force_download=False, force_parse=False, force_summarize=False):
    output_dir = "data/summaries"
    input_file = os.path.join("data/feedback_json", f"{nominee_id}.json")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(input_file, "r") as f:
        feedback_dict = json.load(f)

    nominee_info = feedback_dict.get("nominee_info", {})
    nominee_name = nominee_info.get("name", "Unknown Nominee")
    feedback_by_position = feedback_dict.get("feedback", {})

    for position, feedback_list in feedback_by_position.items():
        summary = get_summary_for_nominee_and_position(nominee_id, position, force_download=force_download, force_parse=force_parse, force_summarize=force_summarize)

        output_filename = f"{nominee_id}_{position}.html"
        output_file = os.path.join(output_dir, output_filename)

        create_html_summary(summary, feedback_list, input_file, output_file, nominee_name, position)

def run_formatting(nominee_id=None, force_download=False, force_parse=False, force_summarize=False):
    if nominee_id:
        create_summary_for_nominee(nominee_id, force_download=force_download, force_parse=force_parse, force_summarize=force_summarize)
    else:
        nominees_data = get_nominees(force_download=force_download)
        for nominee in nominees_data["objects"]:
            create_summary_for_nominee(nominee["id"], force_download=force_download, force_parse=force_parse, force_summarize=force_summarize)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Format feedback summaries.')
    parser.add_argument('nominee_id', nargs='?', help='Optional: Specify a single nominee ID to format (e.g., 123).')
    parser.add_argument("-f", "--force-download", action="store_true", help="Force download even if file exists")
    parser.add_argument("-p", "--force-parse", action="store_true", help="Force parsing even if JSON file exists")
    parser.add_argument("-s", "--force-summarize", action="store_true", help="Force summarization even if summary file exists")
    args = parser.parse_args()
    run_formatting(args.nominee_id, force_download=args.force_download, force_parse=args.force_parse, force_summarize=args.force_summarize)
