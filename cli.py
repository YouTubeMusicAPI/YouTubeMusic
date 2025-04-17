import asyncio
from YouTubeMusic import Search

def main():
    query = input("Enter a song or keyword to search on YouTube: ")
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(Search(query))
    
    if results:
        for result in results:
            print(f"Title: {result.title} - URL: {result.url}")
    else:
        print("No results found!")
      
