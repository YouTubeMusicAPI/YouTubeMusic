import asyncio
import json

from YouTubeMusic.Search import Search, close_client
from YouTubeMusic.Playlist import get_playlist_songs
from YouTubeMusic.Stream import get_stream


async def test_search():
    print("\n🔍 TEST: YouTube Search\n" + "-" * 30)
    query = input("Search query: ")

    data = await Search(query, limit=1)

    print("\nMain Result:")
    print(json.dumps(data["main_results"], indent=2))

    print("\nSuggested:")
    print(json.dumps(data["suggested"], indent=2))


async def test_playlist():
    print("\n📃 TEST: Playlist Fetch\n" + "-" * 30)
    playlist = input("Playlist link or ID: ")

    songs = await get_playlist_songs(playlist)

    print(f"\nTotal songs: {len(songs)}")
    print("\nFirst 3 songs:")
    print(json.dumps(songs[:3], indent=2))


def test_stream():
    print("\n🎧 TEST: Stream Extract\n" + "-" * 30)
    url = input("YouTube video URL: ")

    stream = get_stream(url)

    if stream:
        print("\n✅ Stream URL extracted:")
        print(stream)
    else:
        print("\n❌ Failed to extract stream")


async def main():
    while True:
        print(
            "\n==============================\n"
            "1️⃣  Test Search\n"
            "2️⃣  Test Playlist\n"
            "3️⃣  Test Stream\n"
            "0️⃣  Exit\n"
            "=============================="
        )

        choice = input("Choose: ").strip()

        if choice == "1":
            await test_search()

        elif choice == "2":
            await test_playlist()

        elif choice == "3":
            test_stream()

        elif choice == "0":
            print("\n👋 Exiting...")
            await close_client()
            break

        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    asyncio.run(main())
