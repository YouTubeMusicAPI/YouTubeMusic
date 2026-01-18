import subprocess
import json


def get_stream_url(
    video_url: str,
    cookies_path: str = None,
    mode: str = "audio"   # "audio" | "video"
) -> str | None:
    try:
        # 🔥 SAFE FORMAT (auto select)
        fmt = "ba/b" if mode == "audio" else "bv*+ba/b"

        cmd = [
            "yt-dlp",
            "-J",                      # FULL JSON
            "-f", fmt,
            "--no-playlist",
            "--quiet",
            "--no-warnings",
        ]

        # 🔥 YouTube n / signature safe
        cmd += ["--extractor-args", "youtube:player-client=android"]

        # Cookies (optional)
        if cookies_path:
            cmd += ["--cookies", cookies_path]

        cmd.append(video_url)

        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if p.returncode != 0:
            print("❌ yt-dlp error:", p.stderr.strip())
            return None

        data = json.loads(p.stdout)

        # ───────── AUDIO ─────────
        if mode == "audio":
            for f in data.get("formats", []):
                if (
                    f.get("acodec") not in (None, "none")
                    and f.get("vcodec") in (None, "none")
                    and f.get("url")
                ):
                    return f["url"]

        # ───────── VIDEO ─────────
        else:
            for f in data.get("formats", []):
                if (
                    f.get("acodec") not in (None, "none")
                    and f.get("vcodec") not in (None, "none")
                    and f.get("url")
                ):
                    return f["url"]

        return None

    except Exception as e:
        print("❌ Extract error:", e)
        return None
        
