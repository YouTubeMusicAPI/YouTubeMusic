# YtApiSearch.py
import httpx
import os

# Replace this with your actual API key
YOUTUBE_API_KEY = os.getenv("AIzaSyCkV9TrdPtkYa6P20fnlyB4C2HDQLr3g_I") or "AIzaSyCkV9TrdPtkYa6P20fnlyB4C2HDQLr3g_I"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

async def search_youtube(query: str, limit: int = 1):
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

        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            url = f"https://www.youtube.com/watch?v={video_id}"
            results.append({"title": title, "url": url})

        return results
