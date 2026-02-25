import asyncio
import os
import hashlib
import json
import time
from urllib.parse import urlparse, parse_qs

__all__ = ["get_stream"]

_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
os.makedirs(_CACHE_DIR, exist_ok=True)

_MEM_CACHE = {}
_CACHE_LIMIT = 500


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
            json.dump(
                {
                    "url": stream_url,
                    "expire": expire,
                },
                f,
            )
    except Exception:
        pass


async def _run_yt_dlp(url: str, cookies: str | None = None) -> str | None:
    cmd = [
        "yt-dlp",
        "--js-runtimes",
        "node",
        "--remote-components",
        "ejs:github",
        "-f",
        "bestaudio[ext=m4a]/bestaudio/best",
        "--no-playlist",
        "-g",
        url,
    ]

    if cookies:
        if os.path.exists(cookies):
            cmd.insert(1, "--cookies")
            cmd.insert(2, cookies)
        else:
            return None

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=30)
        except asyncio.TimeoutError:
            process.kill()
            return None

    except Exception:
        return None

    if process.returncode == 0 and stdout:
        return stdout.decode().strip().split("\n")[0]

    return None


async def get_stream(url: str, cookies: str | None = None) -> str | None:
    now = time.time()

    cached = _MEM_CACHE.get(url)
    if cached:
        expire = _extract_expire(cached)
        if expire and now < expire - 15:
            return cached
        else:
            _MEM_CACHE.pop(url, None)

    cached = _read_cache(url)
    if cached:
        _MEM_CACHE[url] = cached
        return cached

    stream = await _run_yt_dlp(url, cookies)

    if stream:
        if len(_MEM_CACHE) >= _CACHE_LIMIT:
            _MEM_CACHE.clear()

        _MEM_CACHE[url] = stream
        _write_cache(url, stream)

    return stream
