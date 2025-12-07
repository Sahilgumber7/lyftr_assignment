# Universal Website Scraper — Lyftr AI Full-stack Assignment

This project is an MVP **universal website scraper** that extracts **structured JSON** from any public webpage.  
It supports static scraping, JavaScript rendering, scrolling, click flows, section grouping, metadata extraction, and interaction logging.  
A lightweight React UI is included for exploring the output.

---

# How to Set Up & Run the Project

### 1. Make `run.sh` executable

```bash
chmod +x run.sh
./run.sh
```

The script automatically:

- Creates & activates a Python virtual environment  
- Installs backend dependencies  
- Runs Playwright install (downloads Chromium/Firefox/WebKit)  
- Starts the FastAPI backend → http://localhost:8000  
- Starts the React frontend → http://localhost:3000  

> No additional setup is required.

---

# Tech Stack

- Language: Python 3.10+  
- Backend: FastAPI  
- HTTP client: `httpx`  
- HTML parsing: `BeautifulSoup4` + `lxml`  
- JS rendering & interactions: Playwright (Python)  
- Frontend: React App using CRA  
- Server runtime: `uvicorn`  

---

# Primary Testing URLs

These URLs were used during development and represent a good spread of webpage types.

### 1. https://en.wikipedia.org/wiki/Artificial_intelligence
- Mostly static HTML  
- Rich use of headings, tables, paragraphs  
- Validates:
  - Section detection  
  - Metadata extraction  
  - Text parsing  

### 2. https://vercel.com/
- JavaScript-heavy marketing site  
- Dynamic components, tabs, animations  
- Validates:
  - Static → JS fallback  
  - Click-flow detection  
  - JS-rendered DOM extraction  

### 3. https://news.ycombinator.com/
- Pagination-heavy list site  
- Minimal JS  
- Good for testing:
  - Pagination via scrolling  
  - Link extraction  
  - Section grouping for list content  
