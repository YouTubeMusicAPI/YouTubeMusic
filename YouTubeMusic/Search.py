import httpx
import re
import json
from .Utils import parse_dur, format_views

YOUTUBE_VIDEO_REGEX = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/(watch\?v=)?([a-zA-Z0-9_-]{11})'

def Search(query: str, limit: int = 1):
    # If the query is a YouTube URL
    if re.match(YOUTUBE_VIDEO_REGEX, query):
        video_id_match = re.search(r"(?:v=|be/)([a-zA-Z0-9_-]{11})", query)
        if video_id_match:
            video_id = video_id_match.group(1)
            watch_url = f"https://www.youtube.com/watch?v={video_id}"

            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            response = httpx.get(watch_url, headers=headers, timeout=10)

            # Debugging response
            print("Response Text:\n", response.text[:1000])  # Print first 1000 characters of the response

            match = re.search(r"var ytInitialPlayerResponse = ({.*?});", response.text)
            if not match:
                return []

            data = json.loads(match.group(1))
            video_details = data.get("videoDetails", {})

            # Print to check if data is correctly fetched
            print("Video Details:", video_details)

            return [{
                "title": video_details.get("title", "Unknown"),
                "artist_name": video_details.get("author", "Unknown"),
                "channel_name": video_details.get("author", "Unknown"),
                "views": format_views(video_details.get("viewCount", "0")),
                "duration": parse_dur(str(video_details.get("lengthSeconds", "0"))),
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                "url": watch_url,
            }]
    
    # If the query is a name to search
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = httpx.get(search_url, headers=headers, timeout=10)
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
                views = v.get("viewCountText", {}).get("simpleText", "0")
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
