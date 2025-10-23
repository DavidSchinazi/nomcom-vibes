#!/usr/bin/env python3

from format import run_formatting

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Format feedback summaries.')
    parser.add_argument('nominee_id', nargs='?', help='Optional: Specify a single nominee ID to format (e.g., 123).')
    parser.add_argument("-f", "--force-download", action="store_true", help="Force download even if file exists")
    parser.add_argument("-p", "--force-parse", action="store_true", help="Force parsing even if JSON file exists")
    parser.add_argument("-s", "--force-summarize", action="store_true", help="Force summarization even if summary file exists")
    args = parser.parse_args()
    run_formatting(args.nominee_id, force_download=args.force_download, force_parse=args.force_parse, force_summarize=args.force_summarize)
