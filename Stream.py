import asyncio
import logging
from functools import partial
from YouTubeMusic.Streams import get_audio_url


logging.basicConfig(level=logging.INFO)


async def ytdl(url: str):
    logging.info("[STREAM] Getting stream URL")

    try:
        # run blocking function in background thread
        loop = asyncio.get_running_loop()
        func = partial(get_audio_url, url, "cookies.txt")
        stream_url = await loop.run_in_executor(None, func)

        if not stream_url:
            return (0, "Failed to get audio stream URL")

        return (1, stream_url)

    except Exception as e:
        logging.error(f"[ERROR] {e}")
        return (0, str(e))


# ───────── RUN TEST ─────────

async def main():
    video = input("Enter YouTube URL: ").strip()

    print("\n⏳ Extracting...\n")

    ok, result = await ytdl(video)

    if ok:
        print("✅ Stream URL Found:\n")
        print(result)
    else:
        print("❌ Failed:\n")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
  
