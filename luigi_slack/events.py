SUCCESS = "SUCCESS"
FAILURE = "FAILURE"
MISSING = "MISSING"
START = "START"
PROCESSING_TIME = "PROCESSING_TIME"


def event_label(event):
    """Format event constants for Slack

    e.g. from `MISSING` to `*Missing*`
    """
    return "{}".format(event.lower().title())
