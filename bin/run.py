#!/usr/bin/env python3

from parse_html_feedback import parse_all_feedback
from format import run_formatting

def run_everything():
    parse_all_feedback()
    run_formatting()

if __name__ == "__main__":
    run_everything()