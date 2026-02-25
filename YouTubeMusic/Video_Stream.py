import subprocess
import os


def get_video_audio_urls(url: str, cookies: str | None = None):
    cmd = [
        "yt-dlp",
        "--js-runtimes", "node",
        "--remote-components", "ejs:github",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]",
        "--no-playlist",
        "-g",
        url
    ]

    # 👇 Add cookies only if valid path provided
    if cookies:
        if os.path.exists(cookies):
            cmd.insert(1, "--cookies")
            cmd.insert(2, cookies)
        else:
            print(f"⚠ Cookies file not found at: {cookies}")
            return None, None

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        print("yt-dlp error:")
        print(result.stderr)
        return None, None

    urls = result.stdout.strip().split("\n")

    if len(urls) < 2:
        return None, None

    return urls[0], urls[1]


def stream_merged(video_url: str, audio_url: str):
    ffmpeg_cmd = [
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

    return subprocess.run(ffmpeg_cmd)
