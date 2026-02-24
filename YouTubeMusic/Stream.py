import subprocess
import json
import os
import hashlib
import time
from urllib.parse import urlparse, parse_qs

__all__ = ["get_stream"]

_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
os.makedirs(_CACHE_DIR, exist_ok=True)

_MEM_CACHE = {}
_CACHE_LIMIT = 500  # prevent unlimited RAM growth


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
        expire = int(q.get("expire", [0])[0])
        return expire if expire > int(time.time()) else None
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

        # 15 sec safety buffer
        if time.time() < expire - 15:
            return data.get("url")
        else:
            os.remove(path)

    except Exception:
        try:
            os.remove(path)
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
# 🎯 STREAM EXTRACTOR
# ==============================

def _extract_stream(url: str, cookies: str | None = None) -> str | None:
    cmd = [
        "yt-dlp",
        "--dump-single-json",
        "-f", "bestaudio[protocol^=http]/best",
        "--no-playlist",
        "--quiet",
        "--no-warnings",
        "--no-check-certificates",
        "--extractor-args",
        "youtube:player-client=android,web",
    ]

    if cookies and os.path.exists(cookies):
        cmd += ["--cookies", cookies]

    cmd.append(url)

    try:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
    except subprocess.TimeoutExpired:
        return None

    if p.returncode != 0 or not p.stdout:
        return None

    try:
        data = json.loads(p.stdout)
    except Exception:
        return None

    # direct url if available
    if data.get("url"):
        return data["url"]

    # fallback formats
    for f in data.get("formats", []):
        if (
            f.get("acodec") not in (None, "none")
            and f.get("protocol", "").startswith("http")
            and f.get("url")
        ):
            return f["url"]

    return None


# ==============================
# PUBLIC API
# ==============================

def get_stream(url: str, cookies: str | None = None) -> str | None:
    now = time.time()

    # MEMORY CACHE
    cached = _MEM_CACHE.get(url)
    if cached:
        expire = _extract_expire(cached)
        if expire and now < expire - 15:
            return cached
        else:
            _MEM_CACHE.pop(url, None)

    # FILE CACHE
    cached = _read_cache(url)
    if cached:
        _MEM_CACHE[url] = cached
        return cached

    # NEW EXTRACTION
    stream = _extract_stream(url, cookies)
    if stream:
        if len(_MEM_CACHE) >= _CACHE_LIMIT:
            _MEM_CACHE.clear()

        _MEM_CACHE[url] = stream
        _write_cache(url, stream)

    return stream
