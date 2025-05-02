import httpx
import re
import json
from .Utils import parse_dur, format_views

def Search(query: str, limit: int = 1):
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = httpx.get(url, headers=headers, timeout=5)

    match = re.search(r"var ytInitialData = ({.*?});</script>", response.text)
    if not match:
        return []

    data = json.loads(match.group(1))
    results = []

    try:
        videos = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]\
            ["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]

        for video in videos:
            if "videoRenderer" in video:
                v = video["videoRenderer"]
                title = v["title"]["runs"][0]["text"]
                video_id = v["videoId"]
                url = f"https://www.youtube.com/watch?v={video_id}"
                duration = v.get("lengthText", {}).get("simpleText", "LIVE")
                views = v.get("viewCountText", {}).get("simpleText", "N/A")
                channel_name = v["ownerText"]["runs"][0]["text"]
                thumbnail = v["thumbnail"]["thumbnails"][-1]["url"]

                results.append({
                    "title": title,
                    "artist_name": channel_name,
                    "channel_name": channel_name,
                    "views": format_views(views),
                    "duration": duration,
                    "thumbnail": thumbnail,
                    "url": url,
                })

                if len(results) >= limit:
                    break

    except Exception as e:
        print("Error:", e)

    return results
