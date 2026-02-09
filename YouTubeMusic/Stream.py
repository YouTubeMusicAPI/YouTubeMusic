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

# ✅ cookies path
_COOKIES_FILE = os.path.join(os.path.dirname(__file__), "cookies.txt")


# ==============================
# HELPERS
# ==============================

def _key(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def _cache_path(url: str) -> str:
    return os.path.join(_CACHE_DIR, _key(url) + ".json")


def _extract_expire(stream_url: str) -> int | None:
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
        if time.time() < expire - 10:
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


# ==============================
# 🎯 STREAM EXTRACTOR WITH COOKIES
# ==============================

def _extract_stream(url: str) -> str | None:
    cmd = [
        "yt-dlp",
        "--dump-single-json",
        "-f", "bestaudio*/best",
        "--no-playlist",
        "--quiet",
        "--extractor-args",
        "youtube:player-client=android,web,ios",
    ]

    # ✅ cookies.txt use karo agar exist karta hai
    if os.path.exists(_COOKIES_FILE):
        cmd += ["--cookies", _COOKIES_FILE]

    # ❗ agar cookies file nahi hai, browser try karega
    else:
        cmd += ["--cookies-from-browser", "chrome"]

    cmd.append(url)

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
    cached = _MEM_CACHE.get(url)
    if cached:
        expire = _extract_expire(cached)
        if expire and time.time() < expire - 10:
            return cached

    cached = _read_cache(url)
    if cached:
        _MEM_CACHE[url] = cached
        return cached

    stream = _extract_stream(url)
    if stream:
        _MEM_CACHE[url] = stream
        _write_cache(url, stream)

    return stream
    
