import time
from YouTubeMusic.Search import Search  # Make sure this matches your module/package structure

QUERIES = [
    "Love Story Taylor Swift",
    "Faded Alan Walker",
    "Shape of You",
    "Believer Imagine Dragons",
    "Dance Monkey",
    "Hymn for the Weekend",
    "Bohemian Rhapsody",
    "Bad Guy Billie Eilish",
]

def main():
    print("🎧 Testing YouTubeMusic Search...\n")

    for query in QUERIES:
        start = time.perf_counter()
        result = Search(query, limit=1)
        end = time.perf_counter()

        main_result = result["main_results"][0] if result["main_results"] else None

        if main_result:
            print(f"✅ {query}")
            print(f"   Title: {main_result['title']}")
            print(f"   URL  : {main_result['url']}")
            print(f"   Time : {end - start:.2f}s\n")
        else:
            print(f"❌ {query} — No result found\n")

if __name__ == "__main__":
    main()
  
