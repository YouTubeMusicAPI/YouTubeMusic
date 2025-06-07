import asyncio
from YouTubeMusic.Search import Search
from YouTubeMusic.Playlist import get_playlist_songs

def main():
    query = input("Enter song name or YouTube URL: ").strip()
    results = Search(query, limit=3)

    if not results or not results.get("main_results"):
        print("No results found.")
        return

    print("\n--- Main Results ---")
    for idx, item in enumerate(results["main_results"], 1):
        print(f"\nResult {idx}")
        print("Type      :", item.get("type", "video"))
        print("Title     :", item["title"])
        print("Channel   :", item["channel_name"])
        print("Thumbnail :", item["thumbnail"])
        print("URL       :", item["url"])

        if item.get("type") == "playlist":
            print("Videos    :", item.get("video_count", "Unknown"))
            playlist_id = item["url"].split("list=")[-1]
            print("\nFetching playlist songs...")
            try:
                songs = asyncio.run(get_playlist_songs(playlist_id))
                for s_idx, song in enumerate(songs, 1):
                    print(f"  {s_idx}. {song['title']} - {song['channel']} [{song['duration']}]")
                    print(f"     URL: {song['url']}")
            except Exception as e:
                print(f"  Error fetching playlist songs: {e}")
        else:
            print("Artist    :", item.get("artist_name", "Unknown"))
            print("Duration  :", item.get("duration", "Unknown"))
            print("Views     :", item.get("views", "0"))

    suggested = results.get("suggested", [])
    if suggested:
        print("\n--- Suggested Songs ---")
        for idx, item in enumerate(suggested, 1):
            print(f"\nSuggestion {idx}")
            print("Title     :", item["title"])
            print("Channel   :", item["channel_name"])
            print("Thumbnail :", item["thumbnail"])
            print("URL       :", item["url"])
            print("Artist    :", item.get("artist_name", "Unknown"))
            print("Duration  :", item.get("duration", "Unknown"))
            print("Views     :", item.get("views", "0"))

if __name__ == "__main__":
    main()
