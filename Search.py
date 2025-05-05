from YouTubeMusic.Search import Search

def main():
    query = input("Enter song name or YouTube URL: ").strip()
    results = Search(query, limit=3)

    if not results:
        print("No results found.")
        return

    for idx, item in enumerate(results, 1):
        print(f"\nResult {idx}")
        print("Type      :", item.get("type", "video"))

        print("Title     :", item["title"])
        print("Channel   :", item["channel_name"])
        print("Thumbnail :", item["thumbnail"])
        print("URL       :", item["url"])

        if item.get("type") == "playlist":
            print("Videos    :", item.get("video_count", "Unknown"))
        else:
            print("Artist    :", item.get("artist_name", "Unknown"))
            print("Duration  :", item.get("duration", "Unknown"))
            print("Views     :", item.get("views", "0"))

if __name__ == "__main__":
    main()
