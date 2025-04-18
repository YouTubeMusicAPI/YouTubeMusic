import httpx
import os
from .Models import format_dur, process_video

YOUTUBE_API_KEY = os.getenv("AIzaSyCkV9TrdPtkYa6P20fnlyB4C2HDQLr3g_I") or "AIzaSyCkV9TrdPtkYa6P20fnlyB4C2HDQLr3g_I"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

async def Search(query: str, limit: int = 1):
    params = {
        "part": "snippet",
        "q": query,
        "maxResults": limit,
        "type": "video",
        "key": YOUTUBE_API_KEY,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(YOUTUBE_SEARCH_URL, params=params)
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            return []

        data = response.json()
        results = []

        # Process the items and add them to the results list
        for item in data.get("items", []):
            video_info = process_video(item)
            if video_info:
                results.append(video_info)

        return results
