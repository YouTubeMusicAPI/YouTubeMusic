import asyncio
import os

__all__ = ["get_stream", "get_video_stream"]


async def _run_yt_dlp(url: str, format_selector: str, cookies: str):
    if not cookies or not os.path.exists(cookies):
        raise ValueError("Cookies File is required and must exist")

    cmd = [
        "yt-dlp",
        "--quiet",
        "--no-warnings",
        "--no-progress",
        "--no-call-home",
        "--no-check-certificates",
        "--no-cache-dir",
        "--cookies", cookies,
        "--extractor-args", "youtube:player_js_variant=main",
        "--no-playlist",
        "-f", format_selector,
        "-g",
        url,
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, _ = await asyncio.wait_for(
            process.communicate(),
            timeout=15,
        )

        if process.returncode == 0 and stdout:
            return stdout.decode().strip().split("\n")[0]

    except Exception:
        return None

    return None


async def get_stream(url: str, cookies: str):
    return await _run_yt_dlp(
        url,
        "bestaudio[ext=m4a]/bestaudio/best",
        cookies,
    )


async def get_video_stream(url: str, cookies: str):
    return await _run_yt_dlp(
        url,
        "best[ext=mp4]/best",
        cookies,
    )
