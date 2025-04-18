import asyncio
from YouTubeMusic.YtSearch import Search

async def main():
    query = input("Enter search query: ").strip()
    limit = 5  # You can change this to any number to limit the results

    print(f"Searching YouTube for: {query}")
    results = await Search(query, limit=1)

    if results:
        print(f"\nFound {len(results)} result(s):\n")
        for idx, video in enumerate(results, start=1):
            print(f"🎵 {video['title']}")
            print(f"🔗 {video['url']}")
            print(f"👤 Artist: {video['artist_name']}")
            print(f"👥 Channel: {video['channel_name']}")
            print(f"👁 Views: {video['views']}")
            print(f"⏱ Duration: {video['duration']}")
            print(f"🖼 Thumbnail: {video['thumbnail']}\n")
    else:
        print("No results found.")

if __name__ == "__main__":
    asyncio.run(main())
