#!/usr/bin/env python3

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
