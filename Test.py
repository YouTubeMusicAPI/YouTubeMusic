import asyncio
from YouTubeMusic.YtSearch import Search

async def main():
    query = input("🔍 Enter song or video search: ")
    results = await Search(query)
    for r in results:
        print(f"{r.title} -> {r.url}")

asyncio.run(main())
