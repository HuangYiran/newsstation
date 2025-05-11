import os
from pydantic_settings import BaseSettings
from typing import List, Dict, Optional

class Settings(BaseSettings):
    # Basic app settings
    APP_NAME: str = "NewsStation"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # API settings
    API_PREFIX: str = "/api"
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./news.db"
    
    # News source settings
    NEWS_SOURCES: Dict[str, Dict] = {
        "hacker_news": {
            "name": "Hacker News",
            "url": "https://news.ycombinator.com/",
            "api_url": "https://hacker-news.firebaseio.com/v0",
            "refresh_interval": 300,  # 5 minutes
            "enabled": True
        },
        "reddit": {
            "name": "Reddit",
            "url": "https://www.reddit.com/",
            "subreddits": ["worldnews", "technology", "science", "politics", "business"],
            "refresh_interval": 300,  # 5 minutes
            "enabled": True
        },
        "github_trending": {
            "name": "GitHub Trending",
            "url": "https://github.com/trending",
            "refresh_interval": 3600,  # 1 hour
            "enabled": True
        }
    }
    
    # News categories
    NEWS_CATEGORIES: List[str] = [
        "realtime",
        "technology",
        "world",
        "business",
        "entertainment",
        "sports",
        "science",
        "health"
    ]
    
    # Cache settings
    CACHE_EXPIRATION: int = 1800  # 30 minutes
    
    # JWT settings
    JWT_SECRET: str = "news_aggregator_secret_key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 3600  # 1 hour
    
    # GitHub OAuth (for login)
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings() 