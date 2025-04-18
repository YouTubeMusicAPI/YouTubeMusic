import httpx
from bs4 import BeautifulSoup
import urllib.parse

BASE_URL = "https://html.duckduckgo.com/html/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

async def Search(query: str, limit: int = 5):
    query += " site:youtube.com"
    url = BASE_URL + "?q=" + urllib.parse.quote_plus(query)
    print(f"Searching DuckDuckGo: {url}")

    try:
        async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
            r = await client.get(url)
            print("Status Code:", r.status_code)
            if r.status_code != 200:
                print("Error: Status code", r.status_code)
                return []

            soup = BeautifulSoup(r.text, "html.parser")
            results = []

            for link in soup.select(".result__a"):
                href = link.get("href")
                if "youtube.com/watch" in href:
                    results.append({
                        "title": link.get_text(strip=True),
                        "url": href
                    })
                if len(results) >= limit:
                    break

            if not results:
                print("No results found.")
            return results

    except Exception as e:
        print("Request error:", e)
        return []
