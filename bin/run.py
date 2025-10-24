#!/usr/bin/env python3

import argparse
from format import run_formatting

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Format feedback summaries.')
    parser.add_argument('nominee_id', nargs='?', help='Optional: Specify a single nominee ID to format (e.g., 123).')
    parser.add_argument("-m", "--force-metadata", action="store_true", help="Force download of metadata even if file exists")
    parser.add_argument("-p", "--force-parse", action="store_true", help="Force parsing even if JSON file exists")
    parser.add_argument("-s", "--force-summarize", action="store_true", help="Force summarization even if summary file exists")
    args = parser.parse_args()
    run_formatting(args.nominee_id, force_metadata=args.force_metadata, force_parse=args.force_parse, force_summarize=args.force_summarize)
