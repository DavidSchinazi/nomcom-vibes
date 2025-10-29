#!/usr/bin/env python3

import argparse
from format import run_formatting

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
