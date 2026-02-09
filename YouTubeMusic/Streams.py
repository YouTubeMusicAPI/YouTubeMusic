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
            "--js-runtimes", "node",   # ⭐ IMPORTANT
        ]

        if cookies_path:
            base_cmd += ["--cookies", cookies_path]

        # 🎯 try best audio first
        cmd = base_cmd + ["-f", "(bestaudio)[protocol^=http]/best", video_url]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30   # ⭐ IMPORTANT
        )

        # 🎯 fallback → best combined
        if result.returncode != 0:
            cmd = base_cmd + ["-f", "best", video_url]
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

        # ✅ primary url
        if data.get("url"):
            return data["url"]

        # ✅ smarter fallback
        formats = data.get("formats", [])
        for f in formats:
            if f.get("acodec") != "none" and f.get("protocol", "").startswith("http"):
                return f.get("url")

        return None

    except subprocess.TimeoutExpired:
        print("❌ yt-dlp timeout")
        return None

    except Exception as e:
        print(f"❌ Error extracting stream URL: {e}")
        return None
