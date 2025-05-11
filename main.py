import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes import api_router
from app.config.settings import settings

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

app = FastAPI(title="NewsStation", description="Real-time news aggregator")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render the main page of the application
    """
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "NewsStation - Real-time News Aggregator"}
    )

@app.get("/c/{category}", response_class=HTMLResponse)
async def category_view(request: Request, category: str):
    """
    Render the category page
    """
    return templates.TemplateResponse(
        "category.html", 
        {"request": request, "title": f"NewsStation - {category.capitalize()}", "category": category}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 