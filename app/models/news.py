from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field

class NewsSource(BaseModel):
    """Model representing a news source"""
    id: str
    name: str
    url: HttpUrl
    description: Optional[str] = None
    category: Optional[str] = None
    language: Optional[str] = "en"
    country: Optional[str] = None

class Author(BaseModel):
    """Model representing an author of a news article"""
    name: str
    url: Optional[HttpUrl] = None
    
class NewsArticle(BaseModel):
    """Model representing a news article"""
    id: str
    title: str
    url: HttpUrl
    summary: Optional[str] = None
    content: Optional[str] = None
    published_at: datetime
    updated_at: Optional[datetime] = None
    author: Optional[Author] = None
    source: NewsSource
    category: str
    tags: List[str] = []
    image_url: Optional[HttpUrl] = None
    comments_count: Optional[int] = 0
    likes_count: Optional[int] = 0
    views_count: Optional[int] = 0
    
class NewsFeed(BaseModel):
    """Model representing a collection of news articles"""
    articles: List[NewsArticle]
    category: str
    page: int = 1
    limit: int = 20
    total: int
    last_updated: datetime = Field(default_factory=datetime.now)

class CategorySummary(BaseModel):
    """Model representing a summary of a news category"""
    name: str
    count: int
    last_updated: datetime = Field(default_factory=datetime.now) 