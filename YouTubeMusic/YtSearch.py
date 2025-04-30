import httpx
import os
from .Models import format_dur, process_video

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY") or "AIzaSyCkV9TrdPtkYa6P20fnlyB4C2HDQLr3g_I"

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
DETAILS_URL = "https://www.googleapis.com/youtube/v3/videos"

async def Search(query: str, limit: int = 1):
    async with httpx.AsyncClient(timeout=10) as client:
        search_params = {
            "part": "snippet",
            "q": query,
            "maxResults": limit,
            "type": "video",
            "key": YOUTUBE_API_KEY,
        }

        search_res = await client.get(SEARCH_URL, params=search_params)
        if search_res.status_code != 200:
            print("Search error:", search_res.status_code)
            return []

        items = search_res.json().get("items", [])
        video_ids = [item["id"]["videoId"] for item in items]

        if not video_ids:
            return []

        details_params = {
            "part": "contentDetails,statistics",
            "id": ",".join(video_ids),
            "key": YOUTUBE_API_KEY,
        }

        detail_res = await client.get(DETAILS_URL, params=details_params)
        detail_items = {v["id"]: v for v in detail_res.json().get("items", [])}

        results = []
        for item in items:
            video_id = item["id"]["videoId"]
            video_details = detail_items.get(video_id)
            if not video_details:
                continue

            video_info = process_video(item, video_details)
            if video_info:
                results.append(video_info)

        return results
