def process_video(item):
    try:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        duration = item["snippet"].get("duration", "N/A")
        views = item["statistics"].get("viewCount", "N/A")
        thumbnail = item["snippet"]["thumbnails"]["high"]["url"]

        artist_name = extract_artist(title)
        channel_name = item["snippet"]["channelTitle"]

        return {
            "title": title,
            "url": url,
            "artist_name": artist_name,
            "channel_name": channel_name,
            "views": views,
            "duration": format_dur(duration),
            "thumbnail": thumbnail,
        }

    except Exception as e:
        print(f"Error processing video item: {e}")
        return None


def format_dur(duration: str):
    try:
        seconds = int(duration)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    except ValueError:
        return "Invalid Duration"


def extract_artist(title: str):
    artist_name = title.split("-")[0].strip() if "-" in title else None
    return artist_name or "Unknown Artist"
