import asyncio
from playwright.async_api import async_playwright

async def search_youtube(query: str, max_results: int = 5):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.youtube.com/results?search_query={query}")
        await page.wait_for_selector('ytd-video-renderer', timeout=10000)
        videos = await page.query_selector_all('ytd-video-renderer')

        results = []
        for video in videos[:max_results]:
            title = await video.query_selector('#video-title')
            duration = await video.query_selector('span.ytd-thumbnail-overlay-time-status-renderer')
            channel = await video.query_selector('ytd-channel-name a')
            if title and duration and channel:
                results.append({
                    'title': await title.get_attribute('title'),
                    'url': 'https://www.youtube.com' + (await title.get_attribute('href')),
                    'duration': (await duration.inner_text()).strip(),
                    'channel': (await channel.inner_text()).strip()
                })
        
        await browser.close()
        return results

async def main():
    query = input("Enter song name: ")
    results = await search_youtube(query)

    print("\nSearch Results:\n")
    for idx, song in enumerate(results, 1):
        print(f"{idx}. {song['title']} - {song['duration']}")
        print(f"   Channel: {song['channel']}")
        print(f"   URL: {song['url']}\n")

if __name__ == "__main__":
    asyncio.run(main())
