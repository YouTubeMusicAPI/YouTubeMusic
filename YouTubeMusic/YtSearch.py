import aiohttp
from bs4 import BeautifulSoup
from .Models import YouTubeResult

async def fetch_duckduckgo_html(query: str) -> str:
    search_url = f"https://duckduckgo.com/html/?q=site:youtube.com+{query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url, headers=headers) as response:
            return await response.text()

def parse_results(html: str):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for tag in soup.find_all("a", class_="result__a"):
        title = tag.get_text()
        href = tag.get("href")
        if "youtube.com/watch" in href:
            results.append(YouTubeResult(title=title, url=href))
    return results

async def Search(query: str):
    html = await fetch_duckduckgo_html(query)
    return parse_results(html)
