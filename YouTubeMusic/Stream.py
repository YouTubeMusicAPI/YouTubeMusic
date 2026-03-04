import asyncio
import os
import hashlib
import json
import time
from urllib.parse import urlparse, parse_qs

__all__ = ["get_stream", "get_video_stream"]

_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
os.makedirs(_CACHE_DIR, exist_ok=True)

_MEM_CACHE = {}


def _key(url: str, prefix: str = "") -> str:
    return hashlib.md5((prefix + url).encode()).hexdigest()


def _cache_path(url: str, prefix: str = "") -> str:
    return os.path.join(_CACHE_DIR, _key(url, prefix) + ".json")


def _extract_expire(stream_url: str):
    try:
        q = parse_qs(urlparse(stream_url).query)
        expire = int(q.get("expire", [0])[0])
        return expire if expire > int(time.time()) else None
    except Exception:
        return None


def _read_cache(url: str, prefix: str = ""):
    path = _cache_path(url, prefix)

    if not os.path.exists(path):
        return None

    try:
        with open(path, "r") as f:
            data = json.load(f)

        expire = data.get("expire", 0)

        if time.time() < expire - 15:
            return data.get("url")

        os.remove(path)

    except Exception:
        try:
            os.remove(path)
        except Exception:
            pass

    return None


def _write_cache(url: str, stream_url: str, prefix: str = ""):
    expire = _extract_expire(stream_url)
    if not expire:
        return

    try:
        with open(_cache_path(url, prefix), "w") as f:
            json.dump(
                {
                    "url": stream_url,
                    "expire": expire,
                },
                f,
            )
    except Exception:
        pass


async def _run_yt_dlp(url: str, format_selector: str, cookies: str | None):
    cmd = [
        "yt-dlp",
        "--js-runtimes", "node",
        "--remote-components", "ejs:github",
        "--extractor-arg", "youtube:player_client=android_vr",
        "--no-warnings",
        "--quiet",
        "-f", format_selector,
        "--no-playlist",
        "-g",
        url,
    ]

    if cookies and os.path.exists(cookies):
        cmd.insert(1, "--cookies")
        cmd.insert(2, cookies)

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, _ = await asyncio.wait_for(
            process.communicate(),
            timeout=15,
        )

    except Exception:
        return None

    if process.returncode == 0 and stdout:
        out = stdout.decode().strip().splitlines()
        return out[0] if out else None

    return None


async def get_stream(url: str, cookies: str | None = None):
    cached = _MEM_CACHE.get(("audio", url))
    if cached:
        expire = _extract_expire(cached)
        if expire and time.time() < expire - 15:
            return cached

    cached = _read_cache(url, prefix="audio_")
    if cached:
        _MEM_CACHE[("audio", url)] = cached
        return cached

    stream = await _run_yt_dlp(
        url,
        "251/bestaudio",
        cookies,
    )

    if stream:
        _MEM_CACHE[("audio", url)] = stream
        _write_cache(url, stream, prefix="audio_")

    return stream


async def get_video_stream(url: str, cookies: str | None = None):
    cached = _MEM_CACHE.get(("video", url))
    if cached:
        expire = _extract_expire(cached)
        if expire and time.time() < expire - 15:
            return cached

    cached = _read_cache(url, prefix="video_")
    if cached:
        _MEM_CACHE[("video", url)] = cached
        return cached

    stream = await _run_yt_dlp(
        url,
        "best[ext=mp4][protocol=https]",
        cookies,
    )

    if stream:
        _MEM_CACHE[("video", url)] = stream
        _write_cache(url, stream, prefix="video_")

    return stream
