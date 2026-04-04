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
        "best[ext=mp4]/best",
        cookies,
    )
    return stream
