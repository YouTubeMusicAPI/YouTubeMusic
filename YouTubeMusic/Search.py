from urllib.parse import quote_plus
import httpx
import re
import json
from .Utils import format_views

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query={}"


async def Search(query: str, limit: int = 1, client=None):
    search_url = YOUTUBE_SEARCH_URL.format(quote_plus(query))

    # Support external client reuse
    if client is None:
        client = httpx.AsyncClient(http2=True, timeout=5.0)

    try:
        response = await client.get(search_url, headers=HEADERS)
    except Exception as e:
        print(f"[!] Request failed: {e}")
        return {"main_results": [], "suggested": []}

    match = re.search(r"var ytInitialData = ({.*?});</script>", response.text)
    if not match:
        return {"main_results": [], "suggested": []}

    try:
        data = json.loads(match.group(1))
        results = []

        sections = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"] \
            ["sectionListRenderer"]["contents"]

        for section in sections:
            items = section.get("itemSectionRenderer", {}).get("contents", [])
            for item in items:
                if "videoRenderer" in item:
                    v = item["videoRenderer"]
                    results.append({
                        "type": "video",
                        "title": v["title"]["runs"][0]["text"],
                        "url": f"https://www.youtube.com/watch?v={v['videoId']}",
                        "duration": v.get("lengthText", {}).get("simpleText", "LIVE"),
                        "channel_name": v.get("ownerText", {}).get("runs", [{}])[0].get("text", "Unknown"),
                        "views": format_views(v.get("viewCountText", {}).get("simpleText", "0 views")),
                        "thumbnail": v["thumbnail"]["thumbnails"][-1]["url"],
                    })

                if len(results) >= limit:
                    break
            if len(results) >= limit:
                break

        return {
            "main_results": results[:limit],
            "suggested": results[limit:limit + 5],
        }

    except Exception as e:
        print(f"[!] Parse error: {e}")
        return {"main_results": [], "suggested": []}
