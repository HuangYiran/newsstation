import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from cachetools import TTLCache

from app.models.news import NewsArticle, NewsFeed, CategorySummary
from app.scrapers import scrapers
from app.config.settings import settings
from app.database.models import Article, Source, Tag
from sqlalchemy.orm import Session
from sqlalchemy import func

logger = logging.getLogger(__name__)

# In-memory cache for news feeds
# Key: category, Value: NewsFeed
news_cache = TTLCache(maxsize=100, ttl=settings.CACHE_EXPIRATION)

# In-memory cache for articles
# Key: article_id, Value: NewsArticle
article_cache = TTLCache(maxsize=1000, ttl=settings.CACHE_EXPIRATION)

class NewsService:
    """
    Service for fetching and managing news articles
    """
    
    @staticmethod
    async def get_news_feed(category: str = "realtime", page: int = 1, limit: int = 20, force_refresh: bool = False) -> NewsFeed:
        """
        Get news feed for a specific category
        
        Args:
            category: Category to fetch
            page: Page number
            limit: Number of articles per page
            force_refresh: Whether to force a refresh of the cache
            
        Returns:
            NewsFeed object containing articles
        """
        cache_key = f"{category}_{page}_{limit}"
        
        # Check cache first if not forcing refresh
        if not force_refresh and cache_key in news_cache:
            logger.info(f"Returning cached news feed for {cache_key}")
            return news_cache[cache_key]
        
        logger.info(f"Fetching fresh news feed for {cache_key}")
        
        # Fetch articles from all sources for the specified category
        all_articles: List[NewsArticle] = []
        fetch_tasks = []
        
        for scraper_id, scraper in scrapers.items():
            # Skip if scraper doesn't match the category
            if category != "realtime" and scraper.category != category:
                continue
                
            # Create fetch task
            logger.debug(f"Creating fetch task for {scraper_id}")
            fetch_tasks.append(scraper.fetch_articles(limit=limit))
        
        if not fetch_tasks:
            logger.warning(f"No suitable scrapers found for category: {category}")
            # 返回空的NewsFeed而不是抛出错误
            return NewsFeed(
                articles=[],
                category=category,
                page=page,
                limit=limit,
                total=0,
                last_updated=datetime.now()
            )
            
        try:
            # Wait for all fetch tasks to complete
            article_lists = await asyncio.gather(*fetch_tasks)
            
            # Combine all articles
            for article_list in article_lists:
                all_articles.extend(article_list)
            
            logger.info(f"Fetched {len(all_articles)} articles for category {category}")
            
            # Sort by published date (newest first)
            all_articles.sort(key=lambda x: x.published_at, reverse=True)
            
            # Paginate
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            paginated_articles = all_articles[start_idx:end_idx]
            
            # Create feed
            feed = NewsFeed(
                articles=paginated_articles,
                category=category,
                page=page,
                limit=limit,
                total=len(all_articles),
                last_updated=datetime.now()
            )
            
            # Cache the feed
            news_cache[cache_key] = feed
            
            # Also cache individual articles
            for article in paginated_articles:
                article_cache[article.id] = article
            
            return feed
        except Exception as e:
            logger.error(f"Error fetching news feed: {str(e)}")
            # 在出错时返回空的NewsFeed而不是传播异常
            return NewsFeed(
                articles=[],
                category=category,
                page=page,
                limit=limit,
                total=0,
                last_updated=datetime.now()
            )
    
    @staticmethod
    async def get_article(article_id: str, force_refresh: bool = False) -> Optional[NewsArticle]:
        """
        Get a specific article by ID
        
        Args:
            article_id: ID of the article
            force_refresh: Whether to force a refresh of the cache
            
        Returns:
            NewsArticle object or None if not found
        """
        # Check cache first if not forcing refresh
        if not force_refresh and article_id in article_cache:
            logger.info(f"Returning cached article for {article_id}")
            return article_cache[article_id]
        
        logger.info(f"Article {article_id} not in cache or force refresh requested")
        
        # We need to extract the source from the article_id
        if "-" not in article_id:
            logger.error(f"Invalid article ID format: {article_id}")
            return None
        
        source_id, _ = article_id.split("-", 1)
        
        # Find the appropriate scraper
        for scraper_id, scraper in scrapers.items():
            if scraper_id == source_id or source_id.startswith(scraper_id):
                # Fetch articles and find the one with the matching ID
                articles = await scraper.fetch_articles(limit=50)
                for article in articles:
                    if article.id == article_id:
                        # Cache the article
                        article_cache[article_id] = article
                        return article
        
        logger.error(f"Article {article_id} not found")
        return None
    
    @staticmethod
    async def get_article_content(article_id: str) -> Optional[str]:
        """
        Get the full content of an article
        
        Args:
            article_id: ID of the article
            
        Returns:
            Full content of the article as HTML or None if not found
        """
        # First get the article to get its URL
        article = await NewsService.get_article(article_id)
        if not article:
            logger.error(f"Article {article_id} not found")
            return None
        
        # Extract source ID
        if "-" not in article_id:
            logger.error(f"Invalid article ID format: {article_id}")
            return None
        
        source_id, _ = article_id.split("-", 1)
        
        # Find the appropriate scraper
        for scraper_id, scraper in scrapers.items():
            if scraper_id == source_id or source_id.startswith(scraper_id):
                # Fetch the content
                content = await scraper.fetch_article_content(article.url)
                return content
        
        logger.error(f"No scraper found for article {article_id}")
        return None
    
    @staticmethod
    async def get_category_summary() -> List[CategorySummary]:
        """
        Get a summary of all categories
        
        Returns:
            List of CategorySummary objects
        """
        summaries = []
        
        for category in settings.NEWS_CATEGORIES:
            # Get count of articles in this category
            feed = await NewsService.get_news_feed(category=category, page=1, limit=1)
            
            summary = CategorySummary(
                name=category,
                count=feed.total,
                last_updated=feed.last_updated
            )
            
            summaries.append(summary)
        
        return summaries
    
    @staticmethod
    async def get_source_news(source_id: str, category: str = "realtime", limit: int = 20, force_refresh: bool = False) -> List[NewsArticle]:
        """
        Get news articles from a specific source
        
        Args:
            source_id: ID of the source to fetch
            category: Category to filter
            limit: Maximum number of articles to return
            force_refresh: Whether to force a refresh of the cache
            
        Returns:
            List of NewsArticle objects from the specified source
        """
        # Find the appropriate scraper
        found_scraper = None
        for scraper_id, scraper in scrapers.items():
            if scraper_id == source_id:
                found_scraper = scraper
                break
        
        if not found_scraper:
            logger.warning(f"No scraper found for source_id: {source_id}")
            return []
        
        # Skip if scraper doesn't match the category and category is not realtime
        if category != "realtime" and found_scraper.category != category:
            logger.warning(f"Scraper {source_id} does not match category {category}")
            return []
            
        try:
            # Fetch articles from the source
            logger.info(f"Fetching articles from source: {source_id}, category: {category}")
            articles = await found_scraper.fetch_articles(limit=limit)
            
            # Cache individual articles
            for article in articles:
                article_cache[article.id] = article
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching articles from source {source_id}: {str(e)}")
            return []
    
    @staticmethod
    def save_to_database(db: Session, articles: List[NewsArticle]):
        """
        Save articles to the database
        
        Args:
            db: Database session
            articles: List of articles to save
        """
        for article in articles:
            try:
                # Check if source exists, create if not
                db_source = db.query(Source).filter(Source.source_id == article.source.id).first()
                if not db_source:
                    db_source = Source(
                        source_id=article.source.id,
                        name=article.source.name,
                        url=str(article.source.url),
                        description=article.source.description,
                        category=article.source.category,
                        language=article.source.language,
                        country=article.source.country
                    )
                    db.add(db_source)
                    db.commit()
                    db.refresh(db_source)
                
                # Check if article exists, update if it does
                db_article = db.query(Article).filter(Article.article_id == article.id).first()
                if db_article:
                    # Update existing article
                    db_article.title = article.title
                    db_article.url = str(article.url)
                    db_article.summary = article.summary
                    db_article.published_at = article.published_at
                    db_article.updated_at = article.updated_at
                    db_article.author_name = article.author.name if article.author else None
                    db_article.author_url = str(article.author.url) if article.author and article.author.url else None
                    db_article.category = article.category
                    db_article.image_url = str(article.image_url) if article.image_url else None
                    db_article.comments_count = article.comments_count or 0
                    db_article.likes_count = article.likes_count or 0
                    db_article.views_count = article.views_count or 0
                else:
                    # Create new article
                    db_article = Article(
                        article_id=article.id,
                        title=article.title,
                        url=str(article.url),
                        summary=article.summary,
                        content=article.content,
                        published_at=article.published_at,
                        updated_at=article.updated_at,
                        author_name=article.author.name if article.author else None,
                        author_url=str(article.author.url) if article.author and article.author.url else None,
                        source_id=db_source.id,
                        category=article.category,
                        image_url=str(article.image_url) if article.image_url else None,
                        comments_count=article.comments_count or 0,
                        likes_count=article.likes_count or 0,
                        views_count=article.views_count or 0
                    )
                    db.add(db_article)
                
                # Handle tags
                for tag_name in article.tags:
                    # Get or create tag
                    db_tag = db.query(Tag).filter(Tag.name == tag_name).first()
                    if not db_tag:
                        db_tag = Tag(name=tag_name)
                        db.add(db_tag)
                        db.commit()
                        db.refresh(db_tag)
                    
                    # Add tag to article if not already present
                    if db_tag not in db_article.tags:
                        db_article.tags.append(db_tag)
                
                db.commit()
                
            except Exception as e:
                db.rollback()
                logger.error(f"Error saving article {article.id} to database: {str(e)}")
    
    @staticmethod
    def get_trending_articles(db: Session, limit: int = 10) -> List[Article]:
        """
        Get trending articles from the database
        
        Args:
            db: Database session
            limit: Maximum number of articles to return
            
        Returns:
            List of Article objects
        """
        # Get articles with the most interactions (sum of comments, likes, views)
        return db.query(Article)\
            .filter(Article.published_at >= func.now() - func.interval('1 day'))\
            .order_by((Article.comments_count + Article.likes_count + Article.views_count).desc())\
            .limit(limit)\
            .all() 