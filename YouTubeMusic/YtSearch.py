import httpx
import re
from urllib.parse import quote

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

async def Search(query: str, limit: int = 5):
    encoded_query = quote(f"{query} site:youtube.com")
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    print(f"Searching DuckDuckGo: {url}")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, headers=HEADERS)
            if r.status_code != 200:
                print(f"Error: Status code {r.status_code}")
                return []

            matches = re.findall(r'<a[^>]+class="result__a"[^>]*href="(https://www\.youtube\.com/watch\?v=[^"]+)"[^>]*>(.*?)</a>', r.text)

            results = []
            for url, title_html in matches:
                # Remove HTML tags from title
                title = re.sub("<.*?>", "", title_html)
                results.append({"title": title.strip(), "url": url.strip()})
                if len(results) >= limit:
                    break

            return results

    except Exception as e:
        print(f"Error: {e}")
        return []
