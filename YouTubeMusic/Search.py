# Search.py

from urllib.parse import quote_plus, quote
import httpx
import re
import orjson
import asyncio
import os

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
UPSTASH_REDIS_REST_URL = os.getenv(
    "UPSTASH_REDIS_REST_URL",
    "https://accepted-woodcock-22573.upstash.io"
)

UPSTASH_REDIS_REST_TOKEN = os.getenv(
    "UPSTASH_REDIS_REST_TOKEN",
    "AlgtAAIgcDJ6f5vhlO6Q9Af3w4dwAI4dvtMnh0IJCpKbAZDWe3Ac9w"
)

REDIS_HEADERS = {
    "Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query={}"
YT_REGEX = re.compile(r"ytInitialData\s*=\s*(\{.+?\});", re.DOTALL)

_client = httpx.AsyncClient(http2=True, timeout=15, headers=HEADERS)

# ─────────────────────────────
# CACHE
# ─────────────────────────────
MEMORY_CACHE = {}
LOCKS = {}
CACHE_LIMIT = 1000


# ─────────────────────────────
# UTILS
# ─────────────────────────────
def normalize(q: str) -> str:
    return re.sub(r"\s+", " ", q.lower().strip())


def format_views(text: str) -> str:
    return text.replace(" views", "").replace(" view", "")


def extract_channel_name(v: dict) -> str:
    for key in ["ownerText", "longBylineText", "shortBylineText"]:
        data = v.get(key, {})
        if data.get("runs"):
            return data["runs"][0].get("text", "Unknown")
    return "Unknown"


def safe_get(obj, *keys):
    for key in keys:
        if not isinstance(obj, dict):
            return {}
        obj = obj.get(key, {})
    return obj


# ─────────────────────────────
# REDIS
# ─────────────────────────────
async def redis_get(key: str):
    try:
        key = quote(key)
        r = await _client.get(
            f"{UPSTASH_REDIS_REST_URL}/get/{key}",
            headers=REDIS_HEADERS
        )
        if r.status_code == 200:
            return r.json().get("result")
    except Exception:
        pass
    return None


async def redis_set(key: str, value):
    try:
        key = quote(key)
        if isinstance(value, bytes):
            value = value.decode()

        await _client.post(
            f"{UPSTASH_REDIS_REST_URL}/set/{key}",
            headers=REDIS_HEADERS,
            json={"value": value}
        )
    except Exception:
        pass


async def close_client():
    await _client.aclose()


# ─────────────────────────────
# MAIN SEARCH
# ─────────────────────────────
async def Search(query: str, limit: int = 1):
    if not query:
        return {"main_results": [], "suggested": []}

    qkey = normalize(query)

    # RAM CACHE
    if qkey in MEMORY_CACHE:
        return MEMORY_CACHE[qkey]

    # REDIS CACHE
    cached = await redis_get(qkey)
    if cached:
        data = orjson.loads(cached.encode())
        MEMORY_CACHE[qkey] = data
        return data

    lock = LOCKS.setdefault(qkey, asyncio.Lock())

    async with lock:
        try:
            url = YOUTUBE_SEARCH_URL.format(quote_plus(query))
            r = await _client.get(url)

            match = YT_REGEX.search(r.text)
            if not match:
                return {"error": "YouTube layout changed", "main_results": [], "suggested": []}

            raw = orjson.loads(match.group(1))

            contents = safe_get(
                raw,
                "contents",
                "twoColumnSearchResultsRenderer",
                "primaryContents",
                "sectionListRenderer",
                "contents"
            )

            results = []

            for section in contents:
                items = safe_get(section, "itemSectionRenderer", "contents")

                for item in items:
                    v = item.get("videoRenderer")
                    if not v:
                        continue

                    video_id = v.get("videoId")
                    if not video_id:
                        continue

                    results.append({
                        "title": safe_get(v, "title", "runs")[0]["text"]
                                 if safe_get(v, "title", "runs") else "Unknown",
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "duration": v.get("lengthText", {}).get("simpleText", "LIVE"),
                        "channel": extract_channel_name(v),
                        "views": format_views(
                            v.get("viewCountText", {}).get("simpleText", "0 views")
                        ),
                        "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                    })

                    if len(results) >= limit + 5:
                        break

            output = {
                "main_results": results[:limit],
                "suggested": results[limit:limit + 5]
            }

            # Cache cleanup
            if len(MEMORY_CACHE) >= CACHE_LIMIT:
                MEMORY_CACHE.clear()

            MEMORY_CACHE[qkey] = output
            await redis_set(qkey, orjson.dumps(output))

            return output

        finally:
            LOCKS.pop(qkey, None)


__all__ = ["Search", "close_client"]
