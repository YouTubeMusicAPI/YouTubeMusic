import subprocess
import json


def get_audio_url(video_url: str, cookies_path: str | None = None) -> str | None:
    try:
        cmd = [
            "yt-dlp",
            "-j",
            "-f", "bestaudio[ext=m4a]/bestaudio",
            "--no-playlist",
            "--quiet",
            "--no-warnings",
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

        # ⭐ primary
        if data.get("url"):
            return data["url"]

        # ⭐ fallback
        for f in data.get("formats", []):
            if f.get("url"):
                return f["url"]

        return None

    except Exception as e:
        print(f"❌ Error extracting stream URL: {e}")
        return None
      
