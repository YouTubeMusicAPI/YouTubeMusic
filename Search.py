from playwright.sync_api import sync_playwright
import asyncio

def search_youtube(query: str, max_results: int = 5):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"https://www.youtube.com/results?search_query={query}")

        page.wait_for_selector('ytd-video-renderer', timeout=10000)
        videos = page.query_selector_all('ytd-video-renderer')

        results = []
        for video in videos[:max_results]:
            title = video.query_selector('#video-title')
            duration = video.query_selector('span.ytd-thumbnail-overlay-time-status-renderer')
            channel = video.query_selector('ytd-channel-name a')
            if title and duration and channel:
                results.append({
                    'title': title.get_attribute('title'),
                    'url': 'https://www.youtube.com' + title.get_attribute('href'),
                    'duration': duration.inner_text().strip(),
                    'channel': channel.inner_text().strip()
                })
        
        browser.close()
        return results

async def main():
  query = input("Enter song name: ")
  results = search_youtube(query)
  print("\nSearch Results:\n")
  for idx, song in enumerate(results, 1):
      print(f"{idx}. {song['title']} - {song['duration']}")
      print(f"   Channel: {song['channel']}")
      print(f"   URL: {song['url']}\n")

asyncio.run((main))
