import httpx
import re
import json
import asyncio
from urllib.parse import urlparse, parse_qs
from typing import List, Dict


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def extract_playlist_id(value: str) -> str:
    value = value.strip()
    if value.startswith(("PL", "OL", "UU", "RD")):
        return value
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    pid = query.get("list", [None])[0]
    if not pid:
        raise ValueError("Invalid playlist link or ID")
    return pid


async def fetch_playlist_page(playlist_id: str) -> str:
    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    async with httpx.AsyncClient(timeout=20, headers=HEADERS) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.text


def extract_yt_initial_data(html: str) -> dict:
    match = re.search(
        r"ytInitialData\s*=\s*({.*?});\s*</script>",
        html,
        re.DOTALL
    )
    if not match:
        raise ValueError("ytInitialData not found")
    return json.loads(match.group(1))


def get_text(obj) -> str:
    if not obj:
        return ""
    if "simpleText" in obj:
        return obj["simpleText"]
    if "runs" in obj:
        return "".join(r.get("text", "") for r in obj["runs"])
    return ""


def parse_playlist_songs(data: dict) -> List[Dict]:
    songs = []

    tabs = data.get("contents", {}) \
        .get("twoColumnBrowseResultsRenderer", {}) \
        .get("tabs", [])

    for tab in tabs:
        content = tab.get("tabRenderer", {}).get("content")
        if not content:
            continue

        section_list = content.get("sectionListRenderer", {}).get("contents", [])

        for section in section_list:
            items = section.get("itemSectionRenderer", {}).get("contents", [])

            for item in items:
                if "playlistVideoListRenderer" in item:
                    videos = item["playlistVideoListRenderer"].get("contents", [])
                    for v in videos:
                        r = v.get("playlistVideoRenderer")
                        if not r:
                            continue
                        vid = r.get("videoId")
                        if not vid:
                            continue
                        songs.append({
                            "videoId": vid,
                            "title": get_text(r.get("title")),
                            "channel": get_text(r.get("shortBylineText")),
                            "duration": r.get("lengthSeconds", "N/A"),
                            "url": f"https://music.youtube.com/watch?v={vid}"
                        })

                if "playlistPanelRenderer" in item:
                    videos = item["playlistPanelRenderer"].get("contents", [])
                    for v in videos:
                        r = v.get("playlistPanelVideoRenderer")
                        if not r:
                            continue
                        vid = r.get("videoId")
                        if not vid:
                            continue
                        songs.append({
                            "videoId": vid,
                            "title": get_text(r.get("title")),
                            "channel": get_text(r.get("shortBylineText")),
                            "duration": r.get("lengthSeconds", "N/A"),
                            "url": f"https://music.youtube.com/watch?v={vid}"
                        })

    return songs


async def get_playlist_songs(playlist_input: str) -> List[Dict]:
    playlist_id = extract_playlist_id(playlist_input)
    html = await fetch_playlist_page(playlist_id)
    data = extract_yt_initial_data(html)
    return parse_playlist_songs(data)


if __name__ == "__main__":
    async def run():
        playlist = input("Playlist link or ID: ")
        songs = await get_playlist_songs(playlist)
        print(len(songs))
        print(json.dumps(songs[:5], indent=2))

    asyncio.run(run())
