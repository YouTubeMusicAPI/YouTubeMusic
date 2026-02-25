import asyncio
from YouTubeMusic.Search import Search


async def main():
    query = input("Enter song name: ")

    results = await Search(query, limit=1)

    if not results or not results.get("main_results"):
        print("No results found.")
        return

    item = results["main_results"][0]

    print("\nSearch Result")
    print("Title     :", item.get("title"))
    print("Channel   :", item.get("channel"))
    print("Views     :", item.get("views"))
    print("Duration  :", item.get("duration"))
    print("Thumbnail :", item.get("thumbnail"))
    print("URL       :", item.get("url"))


if __name__ == "__main__":
    asyncio.run(main())
