from YouTubeMusic.YtSearch import Search
import asyncio

async def run():
    results = await Search("Alone Alan Walker")
    for res in results:
        print(res.title, res.url)

asyncio.run(run())
