import subprocess
import os

__all__ = ["get_video_audio_urls", "start_ffmpeg_merge"]


def get_video_audio_urls(url: str, cookies: str = "cookies.txt"):
    command = [
        "yt-dlp",
        "--no-playlist",
        "--quiet",
        "-f", "bv*[ext=mp4]+ba[ext=m4a]/best[ext=mp4]",
        "-g",
        url
    ]

    # Add cookies if available
    if cookies and os.path.exists(cookies):
        command.insert(1, "--cookies")
        command.insert(2, cookies)

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
    except subprocess.TimeoutExpired:
        return None, None

    if result.returncode != 0 or not result.stdout:
        return None, None

    lines = result.stdout.strip().split("\n")

    if len(lines) == 1:
        return lines[0], None

    if len(lines) >= 2:
        return lines[0], lines[1]

    return None, None


def start_ffmpeg_merge(video_url: str, audio_url: str | None):
    if not video_url:
        return None

    if audio_url:
        ffmpeg_command = [
            "ffmpeg",
            "-loglevel", "error",
            "-i", video_url,
            "-i", audio_url,
            "-c:v", "copy",
            "-c:a", "copy",
            "-f", "mp4",
            "-movflags", "frag_keyframe+empty_moov+faststart",
            "pipe:1"
        ]
    else:
        ffmpeg_command = [
            "ffmpeg",
            "-loglevel", "error",
            "-i", video_url,
            "-c", "copy",
            "-f", "mp4",
            "-movflags", "frag_keyframe+empty_moov+faststart",
            "pipe:1"
        ]

    process = subprocess.Popen(
        ffmpeg_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )

    return process
