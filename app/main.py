from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from .api.routes_health import router as health_router
from .api.routes_scrape import router as scrape_router

# 1. Create the FastAPI app
app = FastAPI(title="Lyftr Universal Scraper MVP")

# 2. Add CORS middleware (for e.g. if you hit it from 5500 or other origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # you can restrict this later if you want
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 4. Routers
app.include_router(health_router)
app.include_router(scrape_router)


# 5. Frontend index page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Simple JSON viewer:
    - URL input
    - Scrape button
    - Loading state
    - Error display
    - Accordion of sections with pretty JSON
    - Download JSON button
    """
    return templates.TemplateResponse("index.html", {"request": request})
