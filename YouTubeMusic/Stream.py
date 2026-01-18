import subprocess
import json


def get_stream_url(
    video_url: str,
    cookies_path: str = None,
    mode: str = "audio"   # "audio" | "video"
) -> str | None:
    try:
        # SAFE AUTO FORMAT
        fmt = "ba/b" if mode == "audio" else "bv*+ba/b"

        cmd = [
            "yt-dlp",
            "-J",  # full json
            "-f", fmt,
            "--no-playlist",
            "--quiet",
            "--no-warnings",
            "--extractor-args", "youtube:player-client=android",
        ]

        # cookies (optional)
        if cookies_path:
            cmd += ["--cookies", cookies_path]

        cmd.append(video_url)

        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=25
        )

        if p.returncode != 0:
            print("❌ yt-dlp error:", p.stderr.strip())
            return None

        data = json.loads(p.stdout)
        formats = data.get("formats", [])

        # ───────── AUDIO MODE ─────────
        if mode == "audio":

            # 1️⃣ Try PURE audio-only stream
            for f in formats:
                if (
                    f.get("acodec") not in (None, "none")
                    and f.get("vcodec") in (None, "none")
                    and f.get("url")
                ):
                    return f["url"]

            # 2️⃣ FALLBACK → video+audio stream
            for f in formats:
                if (
                    f.get("acodec") not in (None, "none")
                    and f.get("vcodec") not in (None, "none")
                    and f.get("url")
                ):
                    return f["url"]

        # ───────── VIDEO MODE ─────────
        else:
            for f in formats:
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
