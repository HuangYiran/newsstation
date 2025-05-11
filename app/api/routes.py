from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.connection import get_db
from app.services.news_service import NewsService
from app.models.news import NewsArticle, NewsFeed, CategorySummary

api_router = APIRouter()

@api_router.get("/news", response_model=NewsFeed)
async def get_news_feed(
    category: str = "realtime",
    page: int = Query(1, gt=0),
    limit: int = Query(20, gt=0, le=100),
    refresh: bool = False
):
    """
    Get news feed for a specific category
    
    Args:
        category: Category to fetch
        page: Page number
        limit: Number of articles per page
        refresh: Whether to force a refresh of the cache
        
    Returns:
        NewsFeed object containing articles
    """
    return await NewsService.get_news_feed(
        category=category,
        page=page,
        limit=limit,
        force_refresh=refresh
    )

@api_router.get("/news/{article_id}", response_model=NewsArticle)
async def get_article(article_id: str, refresh: bool = False):
    """
    Get a specific article by ID
    
    Args:
        article_id: ID of the article
        refresh: Whether to force a refresh of the cache
        
    Returns:
        NewsArticle object
    """
    article = await NewsService.get_article(article_id, force_refresh=refresh)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article {article_id} not found")
    return article

@api_router.get("/news/{article_id}/content", response_model=str)
async def get_article_content(article_id: str):
    """
    Get the full content of an article
    
    Args:
        article_id: ID of the article
        
    Returns:
        Full content of the article as HTML
    """
    content = await NewsService.get_article_content(article_id)
    if not content:
        raise HTTPException(status_code=404, detail=f"Content for article {article_id} not found")
    return content

@api_router.get("/categories", response_model=List[CategorySummary])
async def get_categories():
    """
    Get a summary of all categories
    
    Returns:
        List of CategorySummary objects
    """
    return await NewsService.get_category_summary()

@api_router.get("/trending", response_model=List[NewsArticle])
async def get_trending_articles(
    limit: int = Query(10, gt=0, le=50),
    db: Session = Depends(get_db)
):
    """
    Get trending articles
    
    Args:
        limit: Maximum number of articles to return
        db: Database session
        
    Returns:
        List of NewsArticle objects
    """
    return NewsService.get_trending_articles(db, limit=limit)

@api_router.get("/search", response_model=List[NewsArticle])
async def search_articles(
    query: str,
    category: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = Query(20, gt=0, le=100),
    db: Session = Depends(get_db)
):
    """
    Search for articles
    
    Args:
        query: Search query
        category: Category to search in
        source: Source to search in
        limit: Maximum number of articles to return
        db: Database session
        
    Returns:
        List of NewsArticle objects
    """
    # This would be implemented with database search
    # For now, we'll just return an empty list
    return []

@api_router.get("/news/source/{source_id}", response_model=List[NewsArticle])
async def get_source_news(
    source_id: str,
    category: str = "realtime",
    limit: int = Query(20, gt=0, le=100),
    refresh: bool = False
):
    """
    Get news articles from a specific source
    
    Args:
        source_id: ID of the source to fetch
        category: Category to fetch
        limit: Maximum number of articles to return
        refresh: Whether to force a refresh of the cache
        
    Returns:
        List of NewsArticle objects
    """
    return await NewsService.get_source_news(
        source_id=source_id,
        category=category,
        limit=limit,
        force_refresh=refresh
    )