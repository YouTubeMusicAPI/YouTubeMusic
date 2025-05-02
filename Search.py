import asyncio
import httpx
import re
import json

def fast_search_youtube(query: str, max_results: int = 5):
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
                    "duration": duration,
                    "views": views,
                    "thumbnail": thumbnail,
                    "url": url,
                })

                if len(results) >= max_results:
                    break

    except Exception as e:
        print("Error:", e)

    return results

def main():
    query = input("Enter song name: ")
    results = fast_search_youtube(query, max_results=10)

    for idx, item in enumerate(results, 1):
        print(f"\nResult {idx}")
        print("Title:", item["title"])
        print("Artist:", item["artist_name"])
        print("Channel:", item["channel_name"])
        print("Duration:", item["duration"])
        print("Views:", item["views"])
        print("Thumbnail:", item["thumbnail"])
        print("URL:", item["url"])

if __name__ == "__main__":
    asyncio.run(main())
