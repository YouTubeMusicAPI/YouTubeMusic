import asyncio
from YouTubeMusic.Search import Search

def main():
    query = input("Enter song name: ")
    results = Search(query, limit=3)

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
