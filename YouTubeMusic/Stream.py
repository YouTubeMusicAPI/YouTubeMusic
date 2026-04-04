import asyncio
import os

__all__ = ["get_stream", "get_video_stream"]


async def _run_yt_dlp(url: str, format_selector: str, cookies: str | None):
    strategies = [
        ["--extractor-args", "youtube:player_client=tvhtml5"],
        ["--extractor-args", "youtube:player_js_variant=main"],
    ]

    for extra in strategies:
        cmd = [
            "yt-dlp",
            "--quiet",
            "--no-warnings",
            "--no-progress",
            "--no-call-home",
            "--no-check-certificates",
            "--no-cache-dir",
            "--no-playlist",
            "-f", format_selector,
            "-g",
            url,
        ]

        insert_index = cmd.index("-f")
        for i, arg in enumerate(extra):
            cmd.insert(insert_index + i, arg)

        if cookies and os.path.exists(cookies):
            cmd.insert(1, "--cookies")
            cmd.insert(2, cookies)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=12,
            )

            if process.returncode == 0 and stdout:
                return stdout.decode().strip().split("\n")[0]

        except Exception:
            continue

    return None


async def get_stream(url: str, cookies: str | None = None):
    return await _run_yt_dlp(
        url,
        "bestaudio[ext=m4a]/bestaudio/best",
        cookies,
    )


async def get_video_stream(url: str, cookies: str | None = None):
    return await _run_yt_dlp(
        url,
        "best[ext=mp4]/best",
        cookies,
    )
