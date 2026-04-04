import asyncio
from .startup import get_startup_info


class YouTubeMusic:

    def __init__(self):
        self.started = False

    async def start(self):
        if self.started:
            return

        self.started = True
        asyncio.create_task(self._startup_task())

    async def _startup_task(self):
        info = await get_startup_info()

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🚀 YouTubeMusic Engine Started")
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

    async def stop(self):
        if not self.started:
            return

        print("🛑 YouTubeMusic Engine Stopped\n")
        self.started = False
