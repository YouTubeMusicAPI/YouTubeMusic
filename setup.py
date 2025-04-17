from setuptools import setup, find_packages

setup(
    name="YouTubeMusic",
    version="1.2.1",
    description="Fast YouTube Music Search with DuckDuckGo",
    author="ABHISHEK THAKUR",
    author_email="abhishekbanshiwal2005@gmail.com",
    packages=find_packages(),
    install_requires=[
        "aiohttp",
        "beautifulsoup4",
    ],
    entry_points={
        "console_scripts": [
            "fastyt=cli:main",
            "youtube=cli:main",
            "ytmusic=cli:main",
            "abhimusic=cli:main"
        ]
    },
)
