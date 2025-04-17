import asyncio
from YouTubeMusic import Search

def main():
    query = input("🔍 Enter YouTube search: ")
    results = asyncio.run(Search(query))
    if results:
        for idx, result in enumerate(results, 1):
            print(f"\n🎵 Result {idx}:\n{result}")
    else:
        print("❌ No results found.")
