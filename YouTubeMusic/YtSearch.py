import httpx
import os
import re
from datetime import timedelta

YOUTUBE_API_KEY = os.getenv("AIzaSyCkV9TrdPtkYa6P20fnlyB4C2HDQLr3g_I") or "AIzaSyCkV9TrdPtkYa6P20fnlyB4C2HDQLr3g_I"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_DETAILS_URL = "https://www.googleapis.com/youtube/v3/videos"

def iso8601_duration_to_readable(duration: str) -> str:
    regex = re.match(r"PT(\d+H)?(\d+M)?(\d+S)?", duration)
    hours = int(regex.group(1)[:-1]) if regex.group(1) else 0
    minutes = int(regex.group(2)[:-1]) if regex.group(2) else 0
    seconds = int(regex.group(3)[:-1]) if regex.group(3) else 0

    td = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    
    readable = []
    if hours > 0:
        readable.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        readable.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    if seconds > 0:
        readable.append(f"{seconds} second{'s' if seconds > 1 else ''}")
    
    return " ".join(readable) if readable else "0 seconds"

def extract_artist_from_title(title: str, channel_name: str) -> str:
    match = re.search(r"([^-]+)\s*-\s*(.+)", title)
    if match:
        return match.group(2).strip()
    return channel_name

async def Search(query: str, limit: int = 1):
    search_params = {
        "part": "snippet",
        "q": query,
        "maxResults": limit,
        "type": "video",
        "key": YOUTUBE_API_KEY,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(YOUTUBE_SEARCH_URL, params=search_params)
        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            return []

        search_data = response.json()
        results = []

        video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])]
        if not video_ids:
            return []

        video_details_params = {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(video_ids),
            "key": YOUTUBE_API_KEY,
        }

        video_details_response = await client.get(YOUTUBE_VIDEO_DETAILS_URL, params=video_details_params)
        if video_details_response.status_code != 200:
            print("Error:", video_details_response.status_code, video_details_response.text)
            return []

        video_details_data = video_details_response.json()

        for item in video_details_data.get("items", []):
            title = item["snippet"]["title"]
            video_id = item["id"]
            channel_name = item["snippet"]["channelTitle"]
            channel_id = item["snippet"]["channelId"]
            thumbnail_url = item["snippet"]["thumbnails"]["high"]["url"]
            views = item["statistics"].get("viewCount", "N/A")
            duration = item["contentDetails"].get("duration", "N/A")
            duration_readable = iso8601_duration_to_readable(duration)
            url = f"https://www.youtube.com/watch?v={video_id}"

            artist_name = extract_artist_from_title(title, channel_name)

            results.append({
                "title": title,
                "url": url,
                "artist_name": artist_name,
                "channel_name": channel_name,
                "channel_id": channel_id,
                "thumbnail": thumbnail_url,
                "views": views,
                "duration": duration_readable,
            })

        return results
