import asyncio
import os

__all__ = ["get_stream", "get_video_stream"]


async def _run_yt_dlp(url: str, format_selector: str, cookies: str | None):
    base_cmd = [
        "yt-dlp",
        "-v",
        "--js-runtimes", "node",
        "--remote-components", "ejs:github",
        "--no-playlist",
        "-f", format_selector,
        "-g",
        url,
    ]

    if cookies and os.path.exists(cookies):
        base_cmd.insert(1, "--cookies")
        base_cmd.insert(2, cookies)

    # 🔁 Fallback strategies
    strategies = [
        [],  # normal
        ["--extractor-args", "youtube:player_js_variant=main"],
        ["--extractor-args", "youtube:player_client=android"],
    ]

    for extra in strategies:
        cmd = base_cmd.copy()

        if extra:
            insert_index = cmd.index("-f")
            for i, arg in enumerate(extra):
                cmd.insert(insert_index + i, arg)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=40,
            )

        except Exception:
            continue

        if process.returncode == 0 and stdout:
            return stdout.decode().strip().split("\n")[0]

    return None


async def get_stream(url: str, cookies: str | None = None) -> str | None:
    stream = await _run_yt_dlp(
        url,
        "bestaudio[ext=m4a]/bestaudio/best",
        cookies,
    )
    return stream


async def get_video_stream(url: str, cookies: str | None = None) -> str | None:
    stream = await _run_yt_dlp(
        url,
        "best[ext=mp4][protocol=https]",
        cookies,
    )
    return stream

import asyncio
import os

COOKIES_PATH = "cookies.txt"  # yaha apna path dal


async def main():
    test_url = "https://www.youtube.com/watch?v=O5gwxm3NxFU"

    cookies = COOKIES_PATH if os.path.exists(COOKIES_PATH) else None

    print("🔎 Testing Audio Stream...\n")

    audio = await get_stream(test_url, cookies)

    if audio:
        print("✅ AUDIO STREAM (WITH COOKIES):")
        print(audio)
    else:
        print("❌ AUDIO FAILED WITH COOKIES")

        print("\n🔁 Retrying WITHOUT cookies...\n")
        audio = await get_stream(test_url, None)

        if audio:
            print("✅ AUDIO STREAM (WITHOUT COOKIES):")
            print(audio)
        else:
            print("❌ AUDIO FAILED COMPLETELY")

    print("\n🎬 Testing Video Stream...\n")

    video = await get_video_stream(test_url, cookies)

    if video:
        print("✅ VIDEO STREAM (WITH COOKIES):")
        print(video)
    else:
        print("❌ VIDEO FAILED WITH COOKIES")

        print("\n🔁 Retrying WITHOUT cookies...\n")
        video = await get_video_stream(test_url, None)

        if video:
            print("✅ VIDEO STREAM (WITHOUT COOKIES):")
            print(video)
        else:
            print("❌ VIDEO FAILED COMPLETELY")


if __name__ == "__main__":
    asyncio.run(main())
