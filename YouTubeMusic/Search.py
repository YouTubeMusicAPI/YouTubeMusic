from urllib.parse import quote_plus
import httpx
import re
import orjson
import asyncio

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query={}"

YT_REGEX = re.compile(r"ytInitialData\s*=\s*(\{.+?\});", re.DOTALL)

_client = httpx.AsyncClient(http2=True, timeout=15, headers=HEADERS)


def normalize(q: str) -> str:
    return re.sub(r"\s+", " ", q.lower().strip())


def format_views(text: str) -> str:
    try:
        if not text:
            return "0 Views"

        text = str(text).lower().replace(",", "").strip()

        match = re.search(r"\d+", text)
        if not match:
            return "0 Views"

        num = int(match.group())

        if num >= 10_000_000:
            return f"{num/10_000_000:.1f}Cr Views"
        elif num >= 1_000_000:
            return f"{num/1_000_000:.1f}M Views"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K Views"
        else:
            return f"{num} Views"

    except:
        return "0 Views"


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

        text = r.text

        match = YT_REGEX.search(text)
        if not match:
            return None

        return orjson.loads(match.group(1))

    except Exception:
        return None


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

            title_runs = safe_get(v, "title", "runs")
            title = title_runs[0]["text"] if title_runs else "Unknown"

            views_data = v.get("viewCountText", {})
            views = views_data.get("simpleText")

            if not views:
                runs = views_data.get("runs")
                if runs:
                    views = runs[0].get("text")

            results.append({
                "title": title,
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "duration": v.get("lengthText", {}).get("simpleText", "LIVE"),
                "channel": extract_channel_name(v),
                "views": format_views(views),
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            })

            if len(results) >= limit + 5:
                break

    return {
        "main_results": results[:limit],
        "suggested": results[limit:limit + 5],
    }


async def Trending(limit: int = 10):
    data = await Search("music trending india", limit=limit)
    if not data:
        return []
    return (data.get("main_results", []) + data.get("suggested", []))[:limit]


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
