import logging
import aiohttp
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

from app.models.news import NewsArticle, NewsSource, Author
from app.scrapers.base import BaseScraper
from app.config.settings import settings

logger = logging.getLogger(__name__)

class HackerNewsScraper(BaseScraper):
    """
    Scraper for Hacker News
    """
    def __init__(self):
        """Initialize the Hacker News scraper"""
        super().__init__(
            source_id="hacker_news",
            source_name="Hacker News",
            source_url="https://news.ycombinator.com/",
            category="technology"
        )
        self.api_url = settings.NEWS_SOURCES["hacker_news"]["api_url"]
    
    async def fetch_articles(self, limit: int = 20) -> List[NewsArticle]:
        """
        Fetch top stories from Hacker News
        
        Args:
            limit: Maximum number of articles to return
            
        Returns:
            List of NewsArticle objects
        """
        articles = []
        try:
            logger.debug(f"Fetching top stories from Hacker News, limit: {limit}")
            async with aiohttp.ClientSession() as session:
                # Fetch top story IDs
                url = f"{self.api_url}/topstories.json"
                logger.debug(f"Requesting: {url}")
                try:
                    async with session.get(url, timeout=10) as response:
                        if response.status != 200:
                            logger.error(f"Failed to fetch top stories from Hacker News: {response.status}")
                            return []
                        
                        story_ids = await response.json()
                        story_ids = story_ids[:limit]  # Limit to the specified number
                        logger.debug(f"Retrieved {len(story_ids)} story IDs from Hacker News")
                except Exception as e:
                    logger.error(f"Exception while fetching story IDs: {str(e)}")
                    return []
                
                # Fetch details for each story
                tasks = []
                for story_id in story_ids:
                    url = f"{self.api_url}/item/{story_id}.json"
                    tasks.append(session.get(url, timeout=10))
                
                try:
                    responses = await asyncio.gather(*tasks)
                    stories = []
                    for response in responses:
                        if response.status == 200:
                            story = await response.json()
                            stories.append(story)
                    
                    logger.debug(f"Retrieved {len(stories)} stories from Hacker News")
                except Exception as e:
                    logger.error(f"Exception while fetching story details: {str(e)}")
                    return []
                
                # Convert to NewsArticle objects
                source = NewsSource(
                    id=self.source_id,
                    name=self.source_name,
                    url=self.source_url,
                    category=self.category
                )
                
                for story in stories:
                    try:
                        # Skip stories without URLs
                        if "url" not in story or not story["url"]:
                            continue
                        
                        # Create author if available
                        author = None
                        if "by" in story:
                            author = Author(
                                name=story["by"],
                                url=f"https://news.ycombinator.com/user?id={story['by']}"
                            )
                        
                        # Create article object
                        article = NewsArticle(
                            id=f"hn-{story['id']}",
                            title=story["title"],
                            url=story["url"],
                            summary=None,  # HN doesn't have summaries
                            content=None,  # Fetch content separately if needed
                            published_at=datetime.fromtimestamp(story["time"]),
                            updated_at=None,
                            author=author,
                            source=source,
                            category=self.category,
                            tags=["hacker-news"],
                            image_url=None,  # HN doesn't have images
                            comments_count=story.get("descendants", 0),
                            likes_count=story.get("score", 0),
                            views_count=None  # HN doesn't track views
                        )
                        
                        articles.append(article)
                    except Exception as e:
                        logger.error(f"Error processing story {story.get('id', 'unknown')}: {str(e)}")
            
            logger.info(f"Successfully fetched {len(articles)} articles from Hacker News")
        
        except Exception as e:
            logger.error(f"Error fetching articles from Hacker News: {str(e)}")
        
        return articles
    
    async def fetch_article_content(self, article_url: str) -> Optional[str]:
        """
        Fetch the full content of an article
        
        Args:
            article_url: URL of the article
            
        Returns:
            Full content of the article as HTML or None if failed
        """
        try:
            from newspaper import Article
            
            article = Article(article_url)
            article.download()
            article.parse()
            
            return article.text
            
        except Exception as e:
            logger.error(f"Error fetching article content from {article_url}: {str(e)}")
            return None 