import subprocess
import json
import os
import hashlib
import time
import re
from urllib.parse import urlparse, parse_qs

__all__ = ["get_stream"]

_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
os.makedirs(_CACHE_DIR, exist_ok=True)

_MEM_CACHE = {}

# ==============================
# HELPERS
# ==============================

def _key(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def _cache_path(url: str) -> str:
    return os.path.join(_CACHE_DIR, _key(url) + ".json")


def _extract_expire(stream_url: str) -> int | None:
    """
    YouTube stream URL se expire timestamp nikalta hai
    """
    try:
        q = parse_qs(urlparse(stream_url).query)
        return int(q.get("expire", [0])[0])
    except Exception:
        return None


def _read_cache(url: str) -> str | None:
    path = _cache_path(url)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r") as f:
            data = json.load(f)

        expire = data.get("expire", 0)
        if time.time() < expire - 10:  # 10 sec buffer
            return data.get("url")

    except Exception:
        pass

    return None


def _write_cache(url: str, stream_url: str):
    expire = _extract_expire(stream_url)
    if not expire:
        return

    try:
        with open(_cache_path(url), "w") as f:
            json.dump({
                "url": stream_url,
                "expire": expire
            }, f)
    except Exception:
        pass


def _extract_stream(url: str) -> str | None:
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
            return f["url"]

    return None


# ==============================
# PUBLIC API
# ==============================

def get_stream(url: str) -> str | None:
    # 1️⃣ RAM cache
    cached = _MEM_CACHE.get(url)
    if cached:
        expire = _extract_expire(cached)
        if expire and time.time() < expire - 10:
            return cached

    # 2️⃣ Disk cache
    cached = _read_cache(url)
    if cached:
        _MEM_CACHE[url] = cached
        return cached

    # 3️⃣ New extract
    stream = _extract_stream(url)
    if stream:
        _MEM_CACHE[url] = stream
        _write_cache(url, stream)

    return stream
    
