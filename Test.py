import pytest
from YouTubeMusic.YtSearch import Search

@pytest.mark.asyncio
async def test_search_youtube():
    query = "Chanda Sitare"
    results = await Search(query)
    assert len(results) > 0
    assert "title" in results[0].to_dict()
    assert "url" in results[0].to_dict()
