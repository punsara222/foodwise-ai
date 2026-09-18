import re

def parse_duration_to_minutes(duration_str):
    """
    Converts ISO 8601 duration format (e.g., 'PT1H30M') into total minutes.
    Handles '0' or missing values as 0 minutes.
    """
    if not duration_str or duration_str == "0" or str(duration_str).strip() == "":
        return 0

    duration_str = str(duration_str)
    hours_match = re.search(r'(\d+)H', duration_str)
    minutes_match = re.search(r'(\d+)M', duration_str)

    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0

    return hours * 60 + minutes