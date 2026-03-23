import asyncio
import os

__all__ = ["get_stream", "get_video_stream"]


async def _run_yt_dlp(url: str, format_selector: str, cookies: str | None):
    base_cmd = [
        "yt-dlp",
        "--no-playlist",
        "-f", format_selector,
        "-g",
        "--quiet",
        "--no-warnings",
        url,
    ]

    if cookies and os.path.exists(cookies):
        base_cmd.insert(1, "--cookies")
        base_cmd.insert(2, cookies)

    strategies = [
        [],
        ["--extractor-args", "youtube:player_client=android"],
        ["--extractor-args", "youtube:player_client=web"],
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

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=25,
            )

        except Exception:
            continue

        if process.returncode != 0:
            continue

        if not stdout:
            continue

        output = stdout.decode().strip().split("\n")

        for line in output:
            if line.startswith("http"):
                return line.strip()

    return None


async def get_stream(url: str, cookies: str | None = None) -> str | None:
    return await _run_yt_dlp(
        url,
        "bestaudio[ext=m4a]/bestaudio/best",
        cookies,
    )


async def get_video_stream(url: str, cookies: str | None = None) -> str | None:
    return await _run_yt_dlp(
        url,
        "best[ext=mp4][protocol=https]/best",
        cookies,
    )
