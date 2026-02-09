import subprocess
import json


def get_audio_url(video_url: str, cookies_path: str | None = None) -> str | None:
    """
    Extract direct audio stream URL using yt-dlp.
    Returns best playable URL or None.
    """

    try:
        cmd = [
            "yt-dlp",
            "-j",
            "-f", "bestaudio[acodec!=none]/bestaudio",
            "--no-playlist",
            "--quiet",
            "--no-warnings",
            "--geo-bypass",
            "--no-check-certificate",
        ]

        if cookies_path:
            cmd += ["--cookies", cookies_path]

        cmd.append(video_url)

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print("❌ yt-dlp error:", result.stderr.strip())
            return None

        data = json.loads(result.stdout)

        # ✅ Primary direct URL
        url = data.get("url")
        if url:
            return url

        # ✅ Backup → best format with audio
        formats = data.get("formats", [])
        for f in formats:
            if f.get("acodec") != "none" and f.get("url"):
                return f["url"]

        return None

    except subprocess.TimeoutExpired:
        print("❌ yt-dlp timeout")
        return None

    except Exception as e:
        print(f"❌ Error extracting stream URL: {e}")
        return None
