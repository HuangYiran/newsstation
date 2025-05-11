from typing import Dict
from app.scrapers.base import BaseScraper
from app.scrapers.hacker_news import HackerNewsScraper
from app.scrapers.github_trending import GitHubTrendingScraper
from app.scrapers.reddit import RedditScraper
from app.config.settings import settings

# Dictionary of available scrapers
scrapers: Dict[str, BaseScraper] = {}

def init_scrapers():
    """
    Initialize all scrapers based on the configuration
    """
    # Initialize Hacker News scraper if enabled
    if settings.NEWS_SOURCES["hacker_news"]["enabled"]:
        scrapers["hacker_news"] = HackerNewsScraper()
    
    # Initialize GitHub Trending scraper if enabled
    if settings.NEWS_SOURCES["github_trending"]["enabled"]:
        scrapers["github_trending"] = GitHubTrendingScraper()
    
    # Initialize Reddit scrapers if enabled
    if settings.NEWS_SOURCES["reddit"]["enabled"]:
        # 添加主Reddit爬虫（包含所有subreddits）
        scrapers["reddit"] = RedditScraper()
        
        # 为每个subreddit添加独立的爬虫
        for subreddit in settings.NEWS_SOURCES["reddit"]["subreddits"]:
            scraper_id = f"reddit_{subreddit}"
            scrapers[scraper_id] = RedditScraper(subreddit=subreddit)
    
    # 确保字典中至少有一个刮取器
    if not scrapers:
        # 如果所有刮取器都被禁用，强制启用HackerNews
        scrapers["hacker_news"] = HackerNewsScraper()

# Initialize scrapers
init_scrapers()

__all__ = ["scrapers", "init_scrapers"] 