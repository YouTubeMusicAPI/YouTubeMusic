from urllib.parse import quote_plus, quote
import httpx
import re
import orjson
import asyncio
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query={}"
YOUTUBE_TRENDING_URL = "https://www.youtube.com/feed/trending"

YT_REGEX = re.compile(r"ytInitialData\s*=\s*(\{.*\});", re.DOTALL)

_client = httpx.AsyncClient(http2=True, timeout=15, headers=HEADERS)


def normalize(q: str) -> str:
    return re.sub(r"\s+", " ", q.lower().strip())


def format_views(text: str) -> str:
    return text.replace(" views", "").replace(" view", "")


def extract_channel_name(v: dict) -> str:
    for key in ("ownerText", "longBylineText", "shortBylineText"):
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


async def fetch_yt_data(url: str):
    try:
        r = await _client.get(url)

        if r.status_code != 200:
            return None

        html = r.text

        match = YT_REGEX.search(html)
        if not match:
            return None

        data = match.group(1)

        try:
            return orjson.loads(data)
        except:
            return None

    except Exception:
        return None


# ---------------- SEARCH ----------------

async def Search(query: str, limit: int = 1):
    if not query:
        return {"main_results": [], "suggested": []}

    url = YOUTUBE_SEARCH_URL.format(quote_plus(query))
    raw = await fetch_yt_data(url)

    if not raw:
        return {"main_results": [], "suggested": []}

    contents = safe_get(
        raw,
        "contents",
        "twoColumnSearchResultsRenderer",
        "primaryContents",
        "sectionListRenderer",
        "contents",
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

            title_data = safe_get(v, "title", "runs")
            title = title_data[0]["text"] if title_data else "Unknown"

            results.append({
                "title": title,
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "duration": v.get("lengthText", {}).get("simpleText", "LIVE"),
                "channel": extract_channel_name(v),
                "views": format_views(
                    v.get("viewCountText", {}).get("simpleText", "0 views")
                ),
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            })

            if len(results) >= limit + 5:
                break

    return {
        "main_results": results[:limit],
        "suggested": results[limit: limit + 5],
    }


# ---------------- TRENDING ----------------

async def Trending(limit: int = 10):
    data = await Search("music trending india", limit=limit)

    if not data or not data.get("main_results"):
        return []

    results = data.get("main_results", []) + data.get("suggested", [])
    return results[:limit]


# ---------------- SUGGEST ----------------

async def Suggest(query: str, limit: int = 10):
    data = await Search(query, limit=limit)
    return data.get("suggested", [])


async def close_client():
    await _client.aclose()


__all__ = ["Search", "Trending", "Suggest", "close_client"]

async def main():
    print("🔎 Testing Search...\n")
    
    search_data = await Search("Arijit Singh songs", limit=1)
    print("Main Result:")
    print(search_data["main_results"])
    
    print("\nSuggested:")
    print(search_data["suggested"])


    print("\n🔥 Testing Trending...\n")
    
    trending = await Trending(limit=5)
    for i, video in enumerate(trending, 1):
        print(f"{i}. {video['title']} ({video['views']})")


    print("\n💡 Testing Suggest...\n")
    
    suggest = await Suggest("lofi", limit=5)
    for i, video in enumerate(suggest, 1):
        print(f"{i}. {video['title']}")


    await close_client()


if __name__ == "__main__":
    asyncio.run(main())
