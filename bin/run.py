#!/usr/bin/env python3

from parse_html_feedback import parse_all_feedback
from summarize import run_summarization

def run_everything():
    parse_all_feedback()
    run_summarization()

if __name__ == "__main__":
    run_everything()