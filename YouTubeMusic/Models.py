class YouTubeResult:
    def __init__(self, title: str, url: str):
        self.title = title
        self.url = url

    def __repr__(self):
        return f"Title: {self.title} - URL: {self.url}"

    def to_dict(self):
        return {
            "title": self.title,
            "url": self.url
        }
      
