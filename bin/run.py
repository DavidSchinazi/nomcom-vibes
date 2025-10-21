#!/usr/bin/env python3

from get_feedback import save_all_html_feedback
from parse_html_feedback import parse_all_feedback
from summarize import run_summarization

def run_everything():
    save_all_html_feedback()
    parse_all_feedback()
    run_summarization()

if __name__ == "__main__":
    run_everything()