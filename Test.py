import asyncio
from Yt.Search import Search

async def main():
    query = input("Enter search query: ")
    results = await Search(query)
    if not results:
        print("No results found.")
        return

    print("\nResults:")
    for res in results:
        print(f"🎵 {res['title']}\n🔗 {res['url']}\n")

if __name__ == "__main__":
    asyncio.run(main())
