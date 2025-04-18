import asyncio
from YouTubeMusic.YtSearch import Search

async def main():
    query = input("Enter search query: ")
    print(f"Searching YouTube for: {query}")
    results = await Search(query, limit=3)

    if not results:
        print("No results found.")
        return

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
