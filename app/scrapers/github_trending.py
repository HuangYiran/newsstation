import logging
import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

from app.models.news import NewsArticle, NewsSource, Author
from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

class GitHubTrendingScraper(BaseScraper):
    """
    Scraper for GitHub Trending
    """
    def __init__(self):
        """Initialize the GitHub Trending scraper"""
        super().__init__(
            source_id="github_trending",
            source_name="GitHub Trending",
            source_url="https://github.com/trending",
            category="technology"
        )
    
    async def fetch_articles(self, limit: int = 20) -> List[NewsArticle]:
        """
        Fetch trending repositories from GitHub
        
        Args:
            limit: Maximum number of articles to return
            
        Returns:
            List of NewsArticle objects
        """
        articles = []
        try:
            logger.debug(f"Fetching trending repositories from GitHub, limit: {limit}")
            async with aiohttp.ClientSession() as session:
                # Fetch trending repositories HTML
                try:
                    logger.debug(f"Requesting: {self.source_url}")
                    async with session.get(self.source_url, timeout=10) as response:
                        if response.status != 200:
                            logger.error(f"Failed to fetch trending repositories from GitHub: {response.status}")
                            return []
                        
                        html_content = await response.text()
                except Exception as e:
                    logger.error(f"Exception while fetching GitHub trending page: {str(e)}")
                    return []
                
                try:
                    # Parse HTML
                    soup = BeautifulSoup(html_content, 'html.parser')
                    repos = soup.select('article.Box-row')
                    logger.debug(f"Found {len(repos)} repositories on GitHub trending page")
                    
                    # Create source object
                    source = NewsSource(
                        id=self.source_id,
                        name=self.source_name,
                        url=self.source_url,
                        category=self.category
                    )
                    
                    # Current time (GitHub trending doesn't provide timestamps)
                    now = datetime.now()
                    
                    # Process each repository
                    for i, repo in enumerate(repos):
                        if i >= limit:
                            break
                        
                        try:
                            # Extract repository information
                            repo_rel_path_elem = repo.select_one('h2 a')
                            if not repo_rel_path_elem:
                                logger.warning(f"Could not find repository path for item {i+1}")
                                continue
                                
                            repo_rel_path = repo_rel_path_elem.get('href').strip()
                            repo_url = f"https://github.com{repo_rel_path}"
                            title_parts = repo_rel_path.strip('/').split('/')
                            
                            # Get repo title (username/repo-name)
                            if len(title_parts) >= 2:
                                title = f"{title_parts[0]}/{title_parts[1]}"
                            else:
                                title = repo_rel_path.strip('/')
                            
                            # Get description
                            desc_elem = repo.select_one('p')
                            description = desc_elem.text.strip() if desc_elem else None
                            
                            # Get stars count
                            stars_elem = repo.select_one('a.Link--muted:nth-of-type(1)')
                            stars = int(''.join(filter(str.isdigit, stars_elem.text.strip()))) if stars_elem else 0
                            
                            # Get language
                            lang_elem = repo.select_one('span[itemprop="programmingLanguage"]')
                            language = lang_elem.text.strip() if lang_elem else None
                            
                            # Create tags
                            tags = ["github-trending"]
                            if language:
                                tags.append(language.lower())
                            
                            # Create article
                            article = NewsArticle(
                                id=f"github-{self.generate_article_id(repo_url)}",
                                title=title,
                                url=repo_url,
                                summary=description,
                                content=None,  # Would require additional request to fetch README
                                published_at=now - timedelta(hours=i),  # Approximate time
                                updated_at=None,
                                author=Author(
                                    name=title_parts[0],
                                    url=f"https://github.com/{title_parts[0]}"
                                ),
                                source=source,
                                category=self.category,
                                tags=tags,
                                image_url=None,
                                comments_count=None,
                                likes_count=stars,
                                views_count=None
                            )
                            
                            articles.append(article)
                        
                        except Exception as e:
                            logger.error(f"Error processing GitHub trending repository #{i+1}: {str(e)}")
                except Exception as e:
                    logger.error(f"Error parsing GitHub trending page: {str(e)}")
            
            logger.info(f"Successfully fetched {len(articles)} articles from GitHub Trending")
        
        except Exception as e:
            logger.error(f"Error fetching trending repositories from GitHub: {str(e)}")
        
        return articles
    
    async def fetch_article_content(self, article_url: str) -> Optional[str]:
        """
        Fetch the README content of a GitHub repository
        
        Args:
            article_url: URL of the GitHub repository
            
        Returns:
            README content as HTML or None if failed
        """
        try:
            # Extract owner and repo from URL
            parts = article_url.split('github.com/')
            if len(parts) != 2:
                return None
            
            repo_path = parts[1].strip('/')
            readme_url = f"https://raw.githubusercontent.com/{repo_path}/main/README.md"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(readme_url) as response:
                    if response.status == 200:
                        return await response.text()
                
                # Try master branch if main doesn't exist
                readme_url = f"https://raw.githubusercontent.com/{repo_path}/master/README.md"
                async with session.get(readme_url) as response:
                    if response.status == 200:
                        return await response.text()
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching README content from {article_url}: {str(e)}")
            return None 