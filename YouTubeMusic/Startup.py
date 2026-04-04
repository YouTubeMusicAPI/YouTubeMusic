import httpx
import asyncio
from YouTubeMusic import __version__, __author__

PYPI_URL = "https://pypi.org/pypi/{}/json"


async def check_latest_version(pkg_name: str = "YouTubeMusic"):
    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            r = await client.get(PYPI_URL.format(pkg_name))
            if r.status_code == 200:
                return r.json().get("info", {}).get("version")
    except Exception:
        return None
    return None


async def get_startup_info():
    latest = await check_latest_version("YouTubeMusic")

    return {
        "current_version": __version__,
        "latest_version": latest,
        "author": __author__,
        "update_available": bool(latest and latest != __version__),
    }


async def print_startup():
    info = await get_startup_info()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 YouTubeMusic Engine Loaded")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    print(f"👑 Author   : {info['author']}")
    print(f"📦 Version  : {info['current_version']}")

    if info["latest_version"]:
        print(f"🌐 Latest   : {info['latest_version']}")

    if info["update_available"]:
        print("⚠️ Update Available!")
    else:
        print("✅ Up-to-date")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")


def run_startup():
    try:
        asyncio.get_event_loop().create_task(print_startup())
    except RuntimeError:
        asyncio.run(print_startup())
