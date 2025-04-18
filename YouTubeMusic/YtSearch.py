# YtSearch.py
import httpx
import re
import json
from YouTubeMusic.Models import format_video_result, get_video_data_from_json  # Importing helper functions

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

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, headers=HEADERS)
            if r.status_code != 200:
                print(f"Error: Received status code {r.status_code}")
                return []

            print("Status Code:", r.status_code)

            # More reliable pattern to find ytInitialData
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
                video_data = get_video_data_from_json(data)  # Use helper function to extract video data

                results = []
                for video in video_data:
                    formatted_result = format_video_result(video)  # Format the video result
                    results.append(formatted_result)
                    if len(results) >= limit:
                        break

                return results
            except Exception as e:
                print("Parsing error:", e)
                return []

    except httpx.RequestError as e:
        print(f"Request error: {e}")
        return []
