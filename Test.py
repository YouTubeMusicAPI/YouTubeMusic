import asyncio
 from YouTubeMusic.YtSearch import Search
 
 async def main():
     results = await Search("Alone Alan Walker")
     for r in results:
         print(f"{r.title} -> {r.url}")
 
 asyncio.run(main())
