import asyncio
import os
import hashlib
import json
import time
import sys
from urllib.parse import urlparse, parse_qs

__all__ = ["get_stream", "get_video_stream"]

_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
os.makedirs(_CACHE_DIR, exist_ok=True)

_MEM_CACHE = {}


def _key(url, prefix=""):
    return hashlib.md5((prefix + url).encode()).hexdigest()


def _cache_path(url, prefix=""):
    return os.path.join(_CACHE_DIR, _key(url, prefix) + ".json")


def _extract_expire(stream_url):
    try:
        q = parse_qs(urlparse(stream_url).query)
        return int(q.get("expire", [0])[0])
    except:
        return None


def _read_cache(url, prefix=""):
    path = _cache_path(url, prefix)

    if not os.path.exists(path):
        return None

    try:
        with open(path) as f:
            data = json.load(f)

        expire = data.get("expire")

        if expire and time.time() < expire - 15:
            return data["url"]

        os.remove(path)
    except:
        pass

    return None


def _write_cache(url, stream_url, prefix=""):
    expire = _extract_expire(stream_url)
    if not expire:
        return

    try:
        with open(_cache_path(url, prefix), "w") as f:
            json.dump({"url": stream_url, "expire": expire}, f)
    except:
        pass


async def _run_yt_dlp(url, fmt, cookies_file):

    if not cookies_file or not os.path.exists(cookies_file):
        raise FileNotFoundError("Valid cookies file required")

    cmd = [
        "yt-dlp",
        "--cookies", cookies_file,
        "-f", fmt,
        "-g",
        "--no-playlist",
        url,
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if stderr:
        err = stderr.decode().strip()
        if err:
            print("yt-dlp:", err)

    if process.returncode == 0 and stdout:
        out = stdout.decode().strip().splitlines()
        return out[0] if out else None

    return None


async def get_stream(url, cookies_file):

    if ("audio", url) in _MEM_CACHE:
        cached = _MEM_CACHE[("audio", url)]
        expire = _extract_expire(cached)
        if expire and time.time() < expire - 15:
            return cached

    cached = _read_cache(url, "audio_")
    if cached:
        _MEM_CACHE[("audio", url)] = cached
        return cached

    stream = await _run_yt_dlp(url, "251", cookies_file)

    if stream:
        _MEM_CACHE[("audio", url)] = stream
        _write_cache(url, stream, "audio_")

    return stream


async def get_video_stream(url, cookies_file):

    if ("video", url) in _MEM_CACHE:
        cached = _MEM_CACHE[("video", url)]
        expire = _extract_expire(cached)
        if expire and time.time() < expire - 15:
            return cached

    cached = _read_cache(url, "video_")
    if cached:
        _MEM_CACHE[("video", url)] = cached
        return cached

    stream = await _run_yt_dlp(url, "18", cookies_file)

    if stream:
        _MEM_CACHE[("video", url)] = stream
        _write_cache(url, stream, "video_")

    return stream
