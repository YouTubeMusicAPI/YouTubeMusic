import httpx
import re
import json

def fast_search_youtube(query: str, max_results: int = 5):
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = httpx.get(search_url, headers=headers, timeout=5)

    # Extract initial JSON data from the HTML
    match = re.search(r'var ytInitialData = ({.*?});</script>', response.text)
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
                url = "https://www.youtube.com/watch?v=" + v["videoId"]
                duration = v.get("lengthText", {}).get("simpleText", "LIVE")
                channel = v["ownerText"]["runs"][0]["text"]
                results.append({
                    "title": title,
                    "url": url,
                    "duration": duration,
                    "channel": channel
                })
                if len(results) >= max_results:
                    break

    except Exception as e:
        print("Error parsing data:", e)

    return results

if __name__ == "__main__":
    query = input("Enter song name: ")
    results = fast_search_youtube(query)

    for idx, video in enumerate(results, 1):
        print(f"{idx}. {video['title']} - {video['duration']}")
        print(f"   Channel: {video['channel']}")
        print(f"   URL: {video['url']}\n")


if __name__ == "__main__":
    asyncio.run(main())
