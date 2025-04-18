import httpx
import re
import json
from .Models import Video

BASE_URL = "https://www.youtube.com/results?search_query="
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

async def Search(query: str, limit: int = 1):
    url = BASE_URL + query.replace(" ", "+")
    print(f"Searching: {url}")

    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(url, headers=HEADERS)
        print("Status Code:", r.status_code)

        match = re.search(r"var ytInitialData = ({.*?});", r.text) or \
                re.search(r'window\["ytInitialData"\]\s*=\s*({.*?});', r.text)

        if not match:
            print("ytInitialData not found in response")
            return []

        try:
            data = json.loads(match.group(1))
        except Exception as e:
            print("JSON parsing error:", e)
            return []

        try:
            results = []
            videos = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]\
                    ["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]

            for item in videos:
                video_data = item.get("videoRenderer")
                if not video_data:
                    continue

                title = video_data.get("title", {}).get("runs", [{}])[0].get("text", "Unknown Title")
                video_id = video_data.get("videoId")
                if not video_id:
                    continue

                url = f"https://www.youtube.com/watch?v={video_id}"
                video = Video(title=title, url=url)
                results.append(video)
                if len(results) >= limit:
                    break

            return results
        except Exception as e:
            print("Parsing error:", e)
            return []
