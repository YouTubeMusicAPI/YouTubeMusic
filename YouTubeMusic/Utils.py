import re

def parse_dur(duration):
    match = re.match(
        r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration
    )
    if not match:
        return "N/A"

    hours, minutes, seconds = match.groups(default="0")
    h, m, s = int(hours), int(minutes), int(seconds)

    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"
