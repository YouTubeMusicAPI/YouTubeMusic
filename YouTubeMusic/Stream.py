import subprocess
import json
import os

# user define this path
COOKIES_PATH = ""

def get_audio_url(video_url):
    try:
        cmd = [
            "yt-dlp",
            "-j",
            "-f", "bestaudio[ext=m4a]/bestaudio",
            "--no-playlist",
            "--no-check-certificate"
        ]

        # Only add cookies if path is set and file exists
        if COOKIES_PATH and os.path.exists(COOKIES_PATH):
            cmd += ["--cookies", COOKIES_PATH]

        cmd.append(video_url)

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print("❌ yt-dlp error:", result.stderr.strip())
            return None

        data = json.loads(result.stdout)
        return data["url"]

    except Exception as e:
        print(f"❌ Error extracting stream URL: {e}")
        return None
