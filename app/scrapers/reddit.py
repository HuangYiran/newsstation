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

class RedditScraper(BaseScraper):
    """
    Scraper for Reddit
    """
    def __init__(self, subreddit=None):
        """
        Initialize the Reddit scraper
        
        Args:
            subreddit: Optional specific subreddit to scrape
        """
        # 如果指定了特定subreddit，则只爬取该subreddit
        if subreddit:
            super().__init__(
                source_id=f"reddit_{subreddit}",
                source_name=f"Reddit r/{subreddit}",
                source_url=f"https://www.reddit.com/r/{subreddit}/",
                category=self._get_category_for_subreddit(subreddit)
            )
            self.subreddits = [subreddit]
        else:
            # 否则爬取所有配置的subreddits
            super().__init__(
                source_id="reddit",
                source_name="Reddit",
                source_url="https://www.reddit.com/",
                category="realtime"
            )
            self.subreddits = settings.NEWS_SOURCES["reddit"]["subreddits"]
    
    def _get_category_for_subreddit(self, subreddit):
        """获取subreddit对应的分类"""
        category_map = {
            "worldnews": "world",
            "technology": "technology",
            "science": "science",
            "politics": "world",
            "business": "business"
        }
        return category_map.get(subreddit, "realtime")
    
    async def fetch_articles(self, limit: int = 20) -> List[NewsArticle]:
        """
        Fetch top posts from Reddit subreddits
        
        Args:
            limit: Maximum number of articles to return
            
        Returns:
            List of NewsArticle objects
        """
        articles = []
        posts_per_subreddit = max(limit // len(self.subreddits), 3)  # At least 3 posts per subreddit
        
        try:
            logger.debug(f"Fetching top posts from Reddit, limit: {limit}")
            async with aiohttp.ClientSession() as session:
                # Create tasks for each subreddit
                tasks = []
                for subreddit in self.subreddits:
                    url = f"https://www.reddit.com/r/{subreddit}/top.json?limit={posts_per_subreddit}&t=day"
                    tasks.append(self.fetch_subreddit(session, url, subreddit))
                
                # Gather all results
                subreddit_results = await asyncio.gather(*tasks)
                
                # Flatten the list of articles
                all_articles = []
                for subreddit_articles in subreddit_results:
                    all_articles.extend(subreddit_articles)
                
                # Sort by score and limit
                all_articles.sort(key=lambda x: x.likes_count or 0, reverse=True)
                articles = all_articles[:limit]
                
                logger.info(f"Successfully fetched {len(articles)} articles from Reddit")
        
        except Exception as e:
            logger.error(f"Error fetching articles from Reddit: {str(e)}")
        
        return articles
    
    async def fetch_subreddit(self, session: aiohttp.ClientSession, url: str, subreddit: str) -> List[NewsArticle]:
        """
        Fetch posts from a specific subreddit
        
        Args:
            session: aiohttp client session
            url: Subreddit JSON URL
            subreddit: Name of the subreddit
            
        Returns:
            List of NewsArticle objects
        """
        articles = []
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch posts from r/{subreddit}: {response.status}")
                    return []
                
                data = await response.json()
                posts = data.get("data", {}).get("children", [])
                
                # Map subreddits to categories
                category_map = {
                    "worldnews": "world",
                    "technology": "technology",
                    "science": "science",
                    "politics": "world",
                    "business": "business"
                }
                
                # Create a source object
                source = NewsSource(
                    id=f"reddit-{subreddit}",
                    name=f"Reddit r/{subreddit}",
                    url=f"https://www.reddit.com/r/{subreddit}/",
                    category=category_map.get(subreddit, "realtime")
                )
                
                for post in posts:
                    post_data = post.get("data", {})
                    
                    # Skip self posts unless they have significant content
                    if post_data.get("is_self", False) and len(post_data.get("selftext", "")) < 100:
                        continue
                    
                    # Skip posts without links unless they're text posts with content
                    if not post_data.get("url") and not post_data.get("selftext"):
                        continue
                    
                    # Create author if available
                    author = None
                    if post_data.get("author"):
                        author = Author(
                            name=post_data["author"],
                            url=f"https://www.reddit.com/user/{post_data['author']}"
                        )
                    
                    # Get the URL (external link or permalink)
                    url = post_data.get("url")
                    if post_data.get("is_self", False):
                        url = f"https://www.reddit.com{post_data.get('permalink')}"
                    
                    # Get the image URL if available
                    image_url = None
                    if post_data.get("thumbnail") and post_data["thumbnail"].startswith("http"):
                        image_url = post_data["thumbnail"]
                    elif post_data.get("preview", {}).get("images"):
                        image_url = post_data["preview"]["images"][0]["source"]["url"]
                    
                    # Create article object
                    article = NewsArticle(
                        id=f"reddit-{post_data['id']}",
                        title=post_data["title"],
                        url=url,
                        summary=post_data.get("selftext", "")[:200] if post_data.get("selftext") else None,
                        content=post_data.get("selftext"),
                        published_at=datetime.fromtimestamp(post_data["created_utc"]),
                        updated_at=None,
                        author=author,
                        source=source,
                        category=source.category,
                        tags=[f"reddit", f"r/{subreddit}"],
                        image_url=image_url,
                        comments_count=post_data.get("num_comments", 0),
                        likes_count=post_data.get("score", 0),
                        views_count=None
                    )
                    
                    articles.append(article)
                
                logger.debug(f"Retrieved {len(articles)} posts from r/{subreddit}")
        
        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit}: {str(e)}")
        
        return articles
    
    async def fetch_article_content(self, article_url: str) -> Optional[str]:
        """
        Fetch the full content of an article
        
        Args:
            article_url: URL of the article
            
        Returns:
            Full content of the article as HTML or None if failed
        """
        # For Reddit self posts, the content is already included
        if "reddit.com" in article_url:
            try:
                async with aiohttp.ClientSession() as session:
                    # Append .json to the Reddit URL
                    json_url = f"{article_url}.json"
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }
                    async with session.get(json_url, headers=headers, timeout=10) as response:
                        if response.status != 200:
                            return None
                        
                        data = await response.json()
                        post_data = data[0]["data"]["children"][0]["data"]
                        
                        if post_data.get("selftext"):
                            return post_data["selftext"]
                        return None
            except Exception as e:
                logger.error(f"Error fetching Reddit post content from {article_url}: {str(e)}")
                return None
        
        # For external links, use newspaper3k to extract content
        try:
            from newspaper import Article
            
            article = Article(article_url)
            article.download()
            article.parse()
            
            return article.text
            
        except Exception as e:
            logger.error(f"Error fetching article content from {article_url}: {str(e)}")
            return None 