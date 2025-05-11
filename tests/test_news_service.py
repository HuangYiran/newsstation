import pytest
import asyncio
from datetime import datetime
from app.models.news import NewsArticle, NewsSource, Author
from app.services.news_service import NewsService
from app.scrapers.base import BaseScraper
from typing import List

# Mock scraper for testing
class MockScraper(BaseScraper):
    """Mock scraper for testing"""
    
    def __init__(self, source_id: str, source_name: str, category: str = "technology"):
        super().__init__(
            source_id=source_id,
            source_name=source_name,
            source_url=f"https://example.com/{source_id}",
            category=category
        )
    
    async def fetch_articles(self, limit: int = 10) -> List[NewsArticle]:
        """Mock implementation that returns dummy articles"""
        articles = []
        
        source = NewsSource(
            id=self.source_id,
            name=self.source_name,
            url=self.source_url,
            category=self.category
        )
        
        for i in range(limit):
            article = NewsArticle(
                id=f"{self.source_id}-{i}",
                title=f"Test article {i} from {self.source_name}",
                url=f"https://example.com/{self.source_id}/article/{i}",
                summary=f"Summary of test article {i}",
                content=f"Content of test article {i}",
                published_at=datetime.now(),
                author=Author(name=f"Author {i}", url=f"https://example.com/author/{i}"),
                source=source,
                category=self.category,
                tags=[self.source_id, f"tag-{i}"]
            )
            articles.append(article)
        
        return articles
    
    async def fetch_article_content(self, article_url: str):
        """Mock implementation that returns dummy content"""
        return f"Mock content for {article_url}"

# Register mock scrapers
@pytest.fixture
def mock_scrapers(monkeypatch):
    """Register mock scrapers for testing"""
    from app.scrapers import scrapers
    
    # Clear existing scrapers
    scrapers.clear()
    
    # Add mock scrapers
    scrapers["mock1"] = MockScraper("mock1", "Mock Source 1", "technology")
    scrapers["mock2"] = MockScraper("mock2", "Mock Source 2", "world")
    
    return scrapers

# Tests
@pytest.mark.asyncio
async def test_get_news_feed(mock_scrapers):
    """Test getting news feed from service"""
    feed = await NewsService.get_news_feed(category="realtime", page=1, limit=5)
    
    assert feed is not None
    assert feed.category == "realtime"
    assert feed.page == 1
    assert feed.limit == 5
    assert len(feed.articles) <= 10  # We have 2 sources with 5 articles each
    
    # Test technology category (should only get mock1 articles)
    tech_feed = await NewsService.get_news_feed(category="technology", page=1, limit=5)
    assert tech_feed is not None
    assert tech_feed.category == "technology"
    assert all(article.source.id == "mock1" for article in tech_feed.articles)
    
    # Test world category (should only get mock2 articles)
    world_feed = await NewsService.get_news_feed(category="world", page=1, limit=5)
    assert world_feed is not None
    assert world_feed.category == "world"
    assert all(article.source.id == "mock2" for article in world_feed.articles)

@pytest.mark.asyncio
async def test_get_article(mock_scrapers):
    """Test getting an article by ID"""
    # First get feed to populate cache
    feed = await NewsService.get_news_feed(category="realtime", page=1, limit=5)
    
    # Pick an article ID
    article_id = feed.articles[0].id
    
    # Get article by ID
    article = await NewsService.get_article(article_id)
    
    assert article is not None
    assert article.id == article_id

@pytest.mark.asyncio
async def test_get_article_content(mock_scrapers):
    """Test getting article content"""
    # First get feed to populate cache
    feed = await NewsService.get_news_feed(category="realtime", page=1, limit=5)
    
    # Pick an article ID
    article_id = feed.articles[0].id
    
    # Get article content
    content = await NewsService.get_article_content(article_id)
    
    assert content is not None
    assert "Mock content" in content

@pytest.mark.asyncio
async def test_get_category_summary(mock_scrapers):
    """Test getting category summary"""
    # Clear the cache to ensure fresh data
    from app.services.news_service import news_cache
    news_cache.clear()
    
    # Get category summary
    categories = await NewsService.get_category_summary()
    
    assert categories is not None
    assert len(categories) > 0
    
    # Verify we have technology and world categories
    tech_category = next((c for c in categories if c.name == "technology"), None)
    world_category = next((c for c in categories if c.name == "world"), None)
    
    assert tech_category is not None
    assert world_category is not None
    assert tech_category.count > 0
    assert world_category.count > 0 