import subprocess
import json


def get_audio_url(video_url: str, cookies_path: str | None = None) -> str | None:
    try:
        base_cmd = [
            "yt-dlp",
            "-j",
            "--no-playlist",
            "--quiet",
            "--no-warnings",
            "--geo-bypass",
            "--no-check-certificate",
        ]

        if cookies_path:
            base_cmd += ["--cookies", cookies_path]

        # ⭐ Try strict audio first
        cmd = base_cmd + ["-f", "(bestaudio)[protocol^=http]/best", video_url]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # ⭐ If failed → try best (audio+video)
        if result.returncode != 0:
            cmd = base_cmd + ["-f", "best", video_url]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                print("❌ yt-dlp error:", result.stderr.strip())
                return None

        data = json.loads(result.stdout)

        # primary
        if data.get("url"):
            return data["url"]

        # fallback
        for f in data.get("formats", []):
            if f.get("url"):
                return f["url"]

        return None

    except Exception as e:
        print(f"❌ Error extracting stream URL: {e}")
        return None
        
