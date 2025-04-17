import asyncio
from YouTubeMusic import Search

async def test():
    query = input("🔍 Enter song or video search: ")
    results = await Search(query)
    for res in results:
        print(f"🎵 {res.title} → {res.url}")

asyncio.run(test())
