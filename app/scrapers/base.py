import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.news import NewsArticle

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Base class for all news scrapers
    """
    def __init__(self, source_id: str, source_name: str, source_url: str, category: str = "realtime"):
        """
        Initialize the scraper
        
        Args:
            source_id: Unique identifier for the news source
            source_name: Display name of the news source
            source_url: URL of the news source
            category: Default category for the news source
        """
        self.source_id = source_id
        self.source_name = source_name
        self.source_url = source_url
        self.category = category
        logger.info(f"Initialized {self.__class__.__name__} for {source_name}")
    
    @abstractmethod
    async def fetch_articles(self, limit: int = 10) -> List[NewsArticle]:
        """
        Fetch articles from the news source
        
        Args:
            limit: Maximum number of articles to return
            
        Returns:
            List of NewsArticle objects
        """
        pass
    
    @abstractmethod
    async def fetch_article_content(self, article_url: str) -> Optional[str]:
        """
        Fetch the full content of an article
        
        Args:
            article_url: URL of the article
            
        Returns:
            Full content of the article as HTML or None if failed
        """
        pass
    
    def generate_article_id(self, article_url: str) -> str:
        """
        Generate a unique ID for an article based on its URL
        
        Args:
            article_url: URL of the article
            
        Returns:
            Unique ID for the article
        """
        import hashlib
        return hashlib.md5(article_url.encode()).hexdigest()
    
    def extract_domain(self, url: str) -> str:
        """
        Extract the domain from a URL
        
        Args:
            url: URL to extract domain from
            
        Returns:
            Domain name
        """
        from urllib.parse import urlparse
        return urlparse(url).netloc 