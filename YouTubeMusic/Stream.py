import subprocess
import json
import os
import hashlib

__all__ = ["get_stream"]

# ==============================
# CONFIG
# ==============================

_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
os.makedirs(_CACHE_DIR, exist_ok=True)

# RAM cache (url -> stream)
_MEM_CACHE = {}

# ==============================
# INTERNAL HELPERS
# ==============================

def _key(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def _cache_path(url: str) -> str:
    return os.path.join(_CACHE_DIR, _key(url) + ".json")


def _read_disk(url: str) -> str | None:
    path = _cache_path(url)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data.get("stream")
    except Exception:
        return None


def _write_disk(url: str, stream: str):
    try:
        with open(_cache_path(url), "w") as f:
            json.dump({"stream": stream}, f)
    except Exception:
        pass


def _extract_stream(url: str) -> str | None:
    cmd = [
        "yt-dlp",
        "-J",
        "-f", "ba/b",
        "--quiet",
        "--no-warnings",
        "--extractor-args", "youtube:player-client=android",
        url
    ]

    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if p.returncode != 0:
        return None

    data = json.loads(p.stdout)

    for f in data.get("formats", []):
        if (
            f.get("acodec") not in (None, "none")
            and f.get("vcodec") in (None, "none")
            and f.get("url")
        ):
            return f["url"]

    return None


def _stream_alive(url: str) -> bool:
    """
    Lightweight check: stream URL abhi bhi valid hai ya nahi
    """
    try:
        p = subprocess.run(
            ["curl", "-I", "--max-time", "5", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return p.returncode == 0
    except Exception:
        return False


# ==============================
# PUBLIC API
# ==============================

def get_stream(url: str) -> str | None:
    # 1️⃣ RAM cache
    stream = _MEM_CACHE.get(url)
    if stream and _stream_alive(stream):
        return stream

    # 2️⃣ Disk cache
    stream = _read_disk(url)
    if stream and _stream_alive(stream):
        _MEM_CACHE[url] = stream
        return stream

    # 3️⃣ Extract ONLY if expired
    stream = _extract_stream(url)
    if stream:
        _MEM_CACHE[url] = stream
        _write_disk(url, stream)

    return stream
