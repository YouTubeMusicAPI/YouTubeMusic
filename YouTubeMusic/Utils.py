import re
import urllib.parse as urlparse


def extract_playlist_id(url: str) -> str:
    query = urlparse.urlparse(url).query
    params = urlparse.parse_qs(query)
    return params.get("list", [""])[0]


def parse_dur(duration) -> str:
    if not duration:
        return "N/A"

    # ✅ Case 1: Already in seconds (int/str)
    if isinstance(duration, (int, float)) or str(duration).isdigit():
        seconds = int(duration)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)

        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"

    duration = str(duration)

    # ✅ Case 2: Normal format "3:45" or "1:02:30"
    if ":" in duration:
        try:
            parts = list(map(int, duration.split(":")))
            seconds = 0
            for p in parts:
                seconds = seconds * 60 + p

            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)

            if h:
                return f"{h}:{m:02d}:{s:02d}"
            return f"{m}:{s:02d}"
        except:
            pass

    # ✅ Case 3: ISO format "PT3M45S"
    match = re.match(
        r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",
        duration,
    )

    if match:
        hours, minutes, seconds = match.groups(default="0")

        h = int(hours)
        m = int(minutes)
        s = int(seconds)

        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"

    return "N/A"

def format_ind(n):
    try:
        n = float(n)
    except (ValueError, TypeError):
        return "0"

    if n >= 10**7:
        return f"{n / 10**7:.1f} Crore"

    if n >= 10**5:
        return f"{n / 10**5:.1f} Lakh"

    if n >= 10**3:
        return f"{n / 10**3:.1f}K"

    return str(int(n))


def format_views(views_str: str):
    if not views_str:
        return "N/A"

    cleaned = "".join(filter(str.isdigit, views_str))

    if not cleaned:
        return "N/A"

    try:
        value = float(cleaned)
    except ValueError:
        return "N/A"

    if "M" in views_str:
        value *= 10**6
    elif "K" in views_str:
        value *= 10**3

    return format_ind(value)
