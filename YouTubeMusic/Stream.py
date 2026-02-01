import subprocess
import json
import os
import hashlib

__all__ = ["get_stream"]

_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
os.makedirs(_CACHE_DIR, exist_ok=True)

_MEM_CACHE = {}


def _key(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def _cache_path(url: str) -> str:
    return os.path.join(_CACHE_DIR, _key(url) + ".json")


def _read_disk(url: str):
    try:
        with open(_cache_path(url), "r") as f:
            return json.load(f)
    except Exception:
        return None


def _write_disk(url: str, data: dict):
    try:
        with open(_cache_path(url), "w") as f:
            json.dump(data, f)
    except Exception:
        pass


def _extract_stream(url: str):
    cmd = [
        "yt-dlp",
        "--dump-single-json",
        "-f", "bestaudio*/best",
        "--no-playlist",
        "--quiet",
        "--extractor-args",
        "youtube:player-client=android,web,ios",
        url
    ]

    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if p.returncode != 0 or not p.stdout:
        return None

    data = json.loads(p.stdout)

    for f in data.get("formats", []):
        if f.get("acodec") not in (None, "none") and f.get("url"):
            return {
                "url": f["url"],
                "headers": f.get("http_headers", {})
            }

    return None


def get_stream(url: str):
    # RAM cache
    if url in _MEM_CACHE:
        return _MEM_CACHE[url]

    # Disk cache
    cached = _read_disk(url)
    if cached:
        _MEM_CACHE[url] = cached
        return cached

    # Extract
    stream = _extract_stream(url)
    if stream:
        _MEM_CACHE[url] = stream
        _write_disk(url, stream)

    return stream
    
