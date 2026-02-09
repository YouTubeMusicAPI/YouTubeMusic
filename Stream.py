import asyncio
import logging
from YouTubeMusic.Stream import get_audio_url

logging.basicConfig(level=logging.INFO)


async def ytdl(url: str):
    logging.info(f"[STREAM] Extracting → {url}")

    try:
        stream_url = await asyncio.to_thread(
            get_audio_url, url, "cookies.txt"
        )

        if not stream_url:
            return (0, "Failed to get audio stream URL")

        return (1, stream_url)

    except Exception as e:
        logging.exception("[STREAM ERROR]")
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
    
