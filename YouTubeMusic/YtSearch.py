import aiohttp
import urllib.parse
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

        # Handle DuckDuckGo redirect links
        if url and "/l/?" in url and "uddg=" in url:
            parsed_url = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            actual_url = query_params.get("uddg", [None])[0]

            if actual_url and "youtube.com/watch" in actual_url:
                results.append(YouTubeResult(title=title, url=actual_url))

        # Fallback to direct YouTube links (if available)
        elif url and "youtube.com/watch" in url:
            full_url = url if url.startswith("http") else f"https://www.youtube.com{url}"
            results.append(YouTubeResult(title=title, url=full_url))

        if len(results) >= limit:
            break

    return results


async def Search(query: str, limit: int = 1):
    html = await search_duckduckgo(query)
    return parse_results(html, limit=limit)
