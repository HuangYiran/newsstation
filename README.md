# NewsStation - Real-time News Aggregator

A Python-based news aggregator that collects news from various sources and presents them in a clean, organized interface.

## Features

- **Real-time News Aggregation**: Fetch latest news from multiple sources
- **Categorized Feeds**: Browse news by categories (Technology, World, Business, Health, etc.)
- **Caching Mechanism**: Efficiently cache news to minimize API calls
- **Responsive UI**: Mobile-friendly interface with dark mode support
- **API Endpoints**: Well-defined API for integrating with other applications

## Current Sources

- Hacker News
- GitHub Trending

## Prerequisites

- Python 3.8+
- pip

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   
   - Windows:
     ```
     venv\Scripts\activate
     ```
   
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Run the application:
   ```
   python main.py
   ```

6. Access the application at [http://127.0.0.1:8000](http://127.0.0.1:8000)

## API Endpoints

- `GET /api/news`: Get news feed for a specific category
  - Query Parameters:
    - `category`: Category to fetch (default: "realtime")
    - `page`: Page number (default: 1)
    - `limit`: Number of articles per page (default: 20)
    - `refresh`: Whether to force a refresh of the cache (default: false)

- `GET /api/news/{article_id}`: Get a specific article by ID

- `GET /api/news/{article_id}/content`: Get the full content of an article

- `GET /api/categories`: Get a summary of all categories

- `GET /api/trending`: Get trending articles

- `GET /api/search`: Search for articles
  - Query Parameters:
    - `query`: Search query
    - `category`: Category to search in (optional)
    - `source`: Source to search in (optional)
    - `limit`: Maximum number of articles to return (default: 20)

## Project Structure

```
├── app/
│   ├── api/              # API endpoints
│   ├── config/           # Configuration settings
│   ├── database/         # Database models and connection
│   ├── models/           # Pydantic models
│   ├── scrapers/         # News scrapers
│   ├── services/         # Business logic
│   └── utils/            # Utility functions
├── static/               # Static files (CSS, JS)
├── templates/            # HTML templates
├── tests/                # Unit tests
├── main.py               # Application entry point
├── requirements.txt      # Dependencies
└── README.md             # Project documentation
```

## Adding New Sources

To add a new news source:

1. Create a new scraper in `app/scrapers/` that inherits from `BaseScraper`
2. Implement the required methods
3. Add configuration in `app/config/settings.py`
4. Register the scraper in `app/scrapers/__init__.py`

## Environment Variables

The application can be configured using the following environment variables:

- `DEBUG`: Enable debug mode (default: True)
- `HOST`: Host to bind to (default: 127.0.0.1)
- `PORT`: Port to bind to (default: 8000)
- `DATABASE_URL`: Database connection URL (default: sqlite:///./news.db)
- `CACHE_EXPIRATION`: Cache expiration time in seconds (default: 1800)
- `JWT_SECRET`: Secret key for JWT tokens (default: news_aggregator_secret_key)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Jinja2](https://jinja.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)