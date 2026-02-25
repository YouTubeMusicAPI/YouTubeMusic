import asyncio
from YouTubeMusic.Stream import get_stream


async def main():
    url = input("Enter YouTube video URL: ")

    use_cookies = input("Use cookies? (y/n): ").lower() == "y"

    cookies_path = None
    if use_cookies:
        cookies_path = input("Enter cookies.txt path: ")

    stream_url = await get_stream(url, cookies_path)

    if stream_url:
        print("\nStream URL:")
        print(stream_url)
    else:
        print("Failed to extract stream URL.")


if __name__ == "__main__":
    asyncio.run(main())
