import aiohttp
from bs4 import BeautifulSoup
from .Models import YouTubeResult


async def search_duckduckgo(query: str):
    search_url = f"https://duckduckgo.com/html/?q=site:youtube.com+{query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(search_url, headers=headers) as response:
            html = await response.text()
            return html


def parse_results(html: str, limit: int = 1):
    soup = BeautifulSoup(html, 'html.parser')
    results = []

    for a_tag in soup.find_all('a', class_='result__a'):
        title = a_tag.get_text()
        url = a_tag.get('href')

        if "youtube.com/watch" in url:
            full_url = url if url.startswith("http") else f"https://www.youtube.com{url}"
            results.append(YouTubeResult(title=title, url=full_url))

        if len(results) >= limit:
            break

    return results


async def Search(query: str, limit: int = 1):
    html = await search_duckduckgo(query)
    return parse_results(html, limit=limit)
