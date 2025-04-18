def format_video_result(video):
    """Formats the video result for better readability."""
    title = video.get("title", "Unknown Title")
    url = video.get("url", "#")
    return f"Title: {title}\nURL: {url}"

def get_video_data_from_json(data):
    """Extracts video data from raw JSON."""
    try:
        videos = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]\
            ["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]
        video_data = []
        for item in videos:
            video_renderer = item.get("videoRenderer")
            if video_renderer:
                title = video_renderer.get("title", {}).get("runs", [{}])[0].get("text", "Unknown Title")
                video_id = video_renderer.get("videoId")
                if video_id:
                    url = f"https://www.youtube.com/watch?v={video_id}"
                    video_data.append({"title": title, "url": url})
        return video_data
    except KeyError:
        return []
