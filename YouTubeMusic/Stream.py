import subprocess
import json
import time

__all__ = ["get_stream"]

_CACHE = {}
_TTL = 300  # seconds


def _extract_stream(url: str) -> str | None:
    cmd = [
        "yt-dlp",
        "-J",
        "-f", "ba/b",
        "--quiet",
        "--no-warnings",
        "--extractor-args", "youtube:player-client=android",
        url,
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        return None

    data = json.loads(result.stdout)

    for f in data.get("formats", []):
        if (
            f.get("acodec") not in (None, "none")
            and f.get("vcodec") in (None, "none")
            and f.get("url")
        ):
            return f["url"]

    for f in data.get("formats", []):
        if (
            f.get("acodec") not in (None, "none")
            and f.get("vcodec") not in (None, "none")
            and f.get("url")
        ):
            return f["url"]

    return None


def get_stream(url: str) -> str | None:
    now = time.time()

    cached = _CACHE.get(url)
    if cached:
        stream, ts = cached
        if now - ts < _TTL:
            return stream

    stream = _extract_stream(url)
    if stream:
        _CACHE[url] = (stream, now)

    return stream
    
