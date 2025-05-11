from fastapi import HTTPException, status

class NewsNotFoundException(HTTPException):
    """Exception raised when a news article is not found"""
    def __init__(self, article_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article {article_id} not found"
        )

class NewsSourceNotFoundException(HTTPException):
    """Exception raised when a news source is not found"""
    def __init__(self, source_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"News source {source_id} not found"
        )

class InvalidCategoryException(HTTPException):
    """Exception raised when an invalid category is specified"""
    def __init__(self, category: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category: {category}"
        )

class ScraperException(HTTPException):
    """Exception raised when there is an error scraping news"""
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scraping news: {message}"
        ) 