import asyncio
from YouTubeMusic.Search import Search
from YouTubeMusic.Update import check_for_update

async def main():
    update_msg = await check_for_update()
    if update_msg:
        print(update_msg)

    query = input("Enter song name or YouTube URL: ").strip()
    results = await Search(query, limit=1)

    if not results or not results.get("main_results"):
        print("❌ No results found.")
        return

    item = results["main_results"][0]
    print("\n🎵 Result")
    print("Type      :", item.get("type", "video"))
    print("Title     :", item["title"])
    print("Channel   :", item["channel_name"])
    print("Views     :", item["views"])
    print("Duration  :", item["duration"])
    print("Thumbnail :", item["thumbnail"])
    print("URL       :", item["url"])

if __name__ == "__main__":
    asyncio.run(main())
