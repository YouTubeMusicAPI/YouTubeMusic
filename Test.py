import sys
import asyncio
from YouTubeMusic.YtSearch import Search

def main():
    if len(sys.argv) < 2:
        print("Please provide a search query.")
        return

    query = sys.argv[1]
    results = asyncio.run(Search(query))

    if results:
        print("Found Videos:")
        for video in results:
            print(f"Title: {video.title}\nURL: {video.url}")
    else:
        print("No results found.")

if __name__ == "__main__":
    main()
