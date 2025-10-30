#!/usr/bin/env python3

import argparse
import os
import json
import shutil
from feedback_parser import parse_feedback
from nominees import get_active_nominees, get_nominees_by_position, get_nominee_info
from summarize import are_summaries_enabled, get_ai_summary_for_nominee_and_position, get_ai_summary_for_position
from positions import get_position_short_name, get_position_full_name, get_positions

POSITION_COLOR = "#777777"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <style>
        body {{
            padding: 2rem;
        }}
        .toggle-button {{
            cursor: pointer;
            display: inline-block;
            margin-right: 10px;
            font-size: 1.2rem;
            line-height: 1;
        }}
        .collapsible-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.4s ease-out;
        }}
    </style>
    <script>
        function toggleSection(sectionId) {{
            const content = document.getElementById(sectionId);
            const button = document.getElementById(sectionId + '-toggle');
            if (content.style.maxHeight) {{
                content.style.maxHeight = null;
                button.innerHTML = '&#9654;'; // Right-pointing triangle
            }} else {{
                content.style.maxHeight = content.scrollHeight + "px";
                button.innerHTML = '&#9660;'; // Down-pointing triangle
            }}
        }}

        window.addEventListener('resize', () => {{
            const activeContents = document.querySelectorAll('.collapsible-content.active');
            activeContents.forEach(content => {{
                content.style.maxHeight = content.scrollHeight + "px";
            }});
        }});

        window.addEventListener('load', () => {{
            const activeContents = document.querySelectorAll('.collapsible-content.active');
            activeContents.forEach(content => {{
                content.style.maxHeight = content.scrollHeight + "px";
            }});
        }});
    </script>
</head>
<body>
    <div class="container">
        {body}
    </div>
</body>
</html>"""

def copy_logo():
    """Copies the logo to the data directory."""
    source_logo_path = "static/logo.jpg"
    destination_logo_path = "data/summaries/logo.jpg"
    if os.path.exists(source_logo_path):
        os.makedirs(os.path.dirname(destination_logo_path), exist_ok=True)
        shutil.copy(source_logo_path, destination_logo_path)

def wrap_in_html(title, body):
    """Wraps the given body in a basic HTML structure."""
    return HTML_TEMPLATE.format(title=title, body=body)

def create_page_for_nominee_and_position(summary, feedback_list, input_file, output_file, feedback_dict, position_short_name):
    """Creates an HTML file with the summary and feedback."""
    feedback_with_subject = [item for item in feedback_list if "subject" in item]
    feedback_without_subject = [item for item in feedback_list if "subject" not in item]

    nominee_info = feedback_dict["nominee_info"]
    nominee_name = nominee_info["name"]
    nominee_photo = nominee_info.get("photo")
    position_full_name = get_position_full_name(position_short_name)
    body = '<a href="index.html"><img src="logo.jpg" style="position: absolute; top: 1rem; left: 1rem; width: 70px;"/></a>'
    if nominee_photo:
        body += f'<img src="{nominee_photo}" style="float: right; margin: 1rem;" width="150"/>\n'
    body += f'<h1 style="margin-top: 2rem;">{nominee_name} – <a href="{position_short_name}.html" style="color: {POSITION_COLOR}; text-decoration: none;">{position_full_name}</a></h1>\n'
    if summary:
        body += f'<div style="background-color: #ffdddd;">\n'
        body += f'<h1 onclick="toggleSection(\'ai-summary-content\')" style="cursor: pointer;"><span id="ai-summary-content-toggle" class="toggle-button">&#9660;</span>AI Summary</h1>\n'
        body += f'<div id="ai-summary-content" class="collapsible-content active" style="padding-left: 1.5rem; max-height: 1000px;">{summary}</div>\n'
        body += f'</div>\n'
    if feedback_without_subject:
        body += '<div style="background-color: #ddffdd;">\n'
        body += f'<h1 onclick="toggleSection(\'community-feedback-content\')" style="cursor: pointer;"><span id="community-feedback-content-toggle" class="toggle-button">&#9660;</span>Community Feedback</h1>\n'
        body += '<div id="community-feedback-content" class="collapsible-content active" style="padding-left: 1.5rem; max-height: 1000px;">\n'
        for feedback in feedback_without_subject:
            name = feedback["name"]
            email = feedback["email"]
            date = feedback["date"]
            contents = feedback["feedback"]
            body += f'<div class="feedback">\n'
            body += f'<p><a href="https://datatracker.ietf.org/person/{email}" class="feedback-author" title="{date}">{name}</a>: {contents}</p>\n'
            body += f'</div>\n'
        body += '</div>\n'
        body += '</div>\n'
    questionnaire = feedback_dict["questionnaires"].get(position_short_name)
    if questionnaire:
        body += '<div style="background-color: #eeeeee;">\n'
        body += f'<h1 onclick="toggleSection(\'questionnaire-content\')" style="cursor: pointer;"><span id="questionnaire-content-toggle" class="toggle-button">&#9660;</span>Questionnaire</h1>\n'
        body += f'<div id="questionnaire-content" class="collapsible-content active" style="padding-left: 1.5rem; max-height: 1000px;"><pre class="questionnaire" style="white-space: pre-wrap; word-wrap: break-word;">{questionnaire}</pre></div>\n'
        body += '</div>\n'
    if feedback_with_subject:
        body += f'<h1 onclick="toggleSection(\'self-feedback-content\')" style="cursor: pointer;"><span id=\"self-feedback-content-toggle\" class=\"toggle-button\">&#9660;</span>Self Feedback</h1>\n'
        body += '<div id="self-feedback-content" class="collapsible-content active" style="padding-left: 1.5rem; max-height: 1000px;">\n'
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
    body = '<a href="index.html"><img src="logo.jpg" style="position: absolute; top: 1rem; left: 1rem; width: 70px;"/></a>'
    body += f'<h1 style="margin-top: 2rem;">{position_full_name}</h1>\n'
    if not nominee_ids:
        print(f"No nominees found for position {position_full_name}")
        return

    output_filename = f"{position_short_name}.html"
    output_file = os.path.join(output_dir, output_filename)

    body += '<div style="background-color: #ddeeff; padding: 1rem;">\n'
    body += "<ul style=\"font-size: 1.2em; list-style-type: none; padding-left: 0;\">\n"
    for nominee_id in nominee_ids:
        nominee_info = get_nominee_info(nominee_id, force_metadata=force_metadata)
        nominee_name = nominee_info["name"]
        nominee_photo = nominee_info.get("photo")
        summary_file = f"{nominee_id}_{position_short_name}.html"
        if nominee_photo:
            body += f'<li style="display: flex; align-items: center; margin: 0; padding: 0.2rem 0;"><a href="{summary_file}"><img src="{nominee_photo}" width="40" height="40" style="margin-right: 1rem; object-fit: contain;"/></a><a href="{summary_file}">{nominee_name}</a></li>\n'
        else:
            body += f'<li style="display: flex; align-items: center; margin: 0; padding: 0.2rem 0;"><a href="{summary_file}"><img src="https://www.ietf.org/media/images/ietf-logo.original.png" width="40" height="40" style="margin-right: 1rem; object-fit: contain;"/></a><a href="{summary_file}">{nominee_name}</a></li>\n'
    body += "</ul>\n"
    body += '</div>\n'
    summary = get_ai_summary_for_position(position_short_name, force_metadata=force_metadata, force_feedback=force_feedback, force_parse=force_parse, redo_summaries=redo_summaries, summaries_forced=summaries_forced)
    if summary:
        body += f'<div style="background-color: #ffdddd;">\n'
        body += f'<h1 onclick="toggleSection(\'ai-summary-content\')" style="cursor: pointer;"><span id="ai-summary-content-toggle" class="toggle-button">&#9660;</span>AI Summary for {position_full_name}</h1>\n'
        body += f'<div id="ai-summary-content" class="collapsible-content active" style="padding-left: 1.5rem; max-height: 1000px;">{summary}</div>\n'
        body += f'</div>\n'

    with open(output_file, "w") as f:
        f.write(wrap_in_html(f"Nominee Summary for {position_full_name}", body))
    print(f"Successfully created summary for position {position_full_name} and saved to {output_file}")


def create_index_page(force_metadata=False):
    output_dir = "data/summaries"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    positions = get_positions(force_metadata=force_metadata)
    iab_position = [p for p in positions if p['name'] == 'Internet Architecture Board, Member']
    iesg_positions = sorted([p for p in positions if p['is_iesg_position'] and p['name'] != 'Internet Architecture Board, Member'], key=lambda p: p['name'])
    non_iesg_positions = sorted([p for p in positions if not p['is_iesg_position'] and p['name'] != 'Internet Architecture Board, Member'], key=lambda p: p['name'])
    sorted_positions = iab_position + non_iesg_positions + iesg_positions

    output_file = os.path.join(output_dir, "index.html")

    body = '<a href="index.html"><img src="logo.jpg" style="display: block; margin: 0 auto; height: 300px;"/></a>'
    body += "<ul style=\"font-size: 1.5em; list-style-type: none; text-align: center; padding-left: 0; margin-top: 2rem;\">\n"
    for position in sorted_positions:
        position_short_name = get_position_short_name(position['name'])
        position_full_name = get_position_full_name(position_short_name)
        body += f'<li><a href="{position_short_name}.html">{position_full_name}</a></li>\n'
    body += "</ul>\n"

    with open(output_file, "w") as f:
        f.write(wrap_in_html("", body))
    print(f"Successfully created overall summary and saved to {output_file}")


def run_formatting(nominee_id=None, position_short_name=None, force_metadata=False, force_feedback=False, force_parse=False, redo_summaries=False, summaries_forced=None):
    copy_logo()
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
    parser.add_argument("-a", "--force-all", action="store_true", help="Enable -m, -f, -p, and -s flags")
    parser.add_argument("-x", "--add-summaries", action='store_const', const=True, default=None, dest="summaries_forced", help="Add summarization even if disabled")
    parser.add_argument("-z", "--no-summaries", action='store_const', const=False, default=None, dest="summaries_forced", help="Disable summarization even if enabled")
    args = parser.parse_args()

    if args.force_all:
        args.force_metadata = True
        args.force_feedback = True
        args.force_parse = True
        args.redo_summaries = True

    nominee_id = None
    position_short_name = None
    if args.identifier:
        try:
            nominee_id = int(args.identifier)
        except ValueError:
            position_short_name = args.identifier

    run_formatting(nominee_id=nominee_id, position_short_name=position_short_name, force_metadata=args.force_metadata, force_feedback=args.force_feedback, force_parse=args.force_parse, redo_summaries=args.redo_summaries, summaries_forced=args.summaries_forced)
