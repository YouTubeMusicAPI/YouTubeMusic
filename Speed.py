import asyncio
import time
import httpx
from YouTubeMusic.Search import Search

QUERIES = [
    "Love Story Taylor Swift",
    "Faded Alan Walker",
    "Shape of You",
    "Believer Imagine Dragons",
    "Dance Monkey",
    "Hymn for the Weekend",
    "Bohemian Rhapsody",
    "Bad Guy Billie Eilish",
]

async def main():
    print("🎧 Testing YouTubeMusic Search...\n")
    start = time.perf_counter()

    async with httpx.AsyncClient(http2=True, timeout=5.0) as client:
        tasks = [Search(query, limit=1, client=client) for query in QUERIES]
        results = await asyncio.gather(*tasks)

    end = time.perf_counter()
    print(f"\n⏱️ Total Time: {end - start:.2f}s\n")

    for query, result in zip(QUERIES, results):
        if result["main_results"]:
            song = result["main_results"][0]
            print(f"✅ {query}")
            print(f"   Title: {song['title']}")
            print(f"   URL  : {song['url']}\n")
        else:
            print(f"❌ {query} — No result\n")

if __name__ == "__main__":
    asyncio.run(main())
