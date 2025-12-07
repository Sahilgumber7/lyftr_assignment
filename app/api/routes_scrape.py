import datetime
import traceback
from typing import List
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, HTTPException

from ..core.config import HTTP_TIMEOUT
from ..core.schemas import (
    ScrapeRequest,
    ScrapeResponse,
    ScrapeResult,
    MetaInfo,
    Section,
    Interactions,
    ErrorItem,
)
from ..services.scraper_static import static_scrape, static_content_too_weak
from ..services.scraper_js import js_scrape_with_interactions

router = APIRouter()


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_endpoint(body: ScrapeRequest):
    url = str(body.url)

    # Validate scheme
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http(s) URLs are supported")

    errors: List[ErrorItem] = []
    interactions = Interactions(clicks=[], scrolls=0, pages=[])

    # 1. Static fetch
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        tb = "".join(traceback.format_exception_only(type(e), e)).strip()
        errors.append(ErrorItem(message=f"HTTP fetch error: {tb}", phase="fetch"))
        meta = MetaInfo(title="", description="", language="en", canonical=None)

        result = ScrapeResult(
            url=url,
            scrapedAt=datetime.datetime.utcnow().isoformat() + "Z",
            meta=meta,
            sections=[],
            interactions=interactions,
            errors=errors,
        )
        return ScrapeResponse(result=result)

    # 2. Static parse
    try:
        meta, sections = static_scrape(html, url)
    except Exception as e:
        tb = "".join(traceback.format_exception_only(type(e), e)).strip()
        errors.append(ErrorItem(message=f"Static parse error: {tb}", phase="parse"))
        meta = MetaInfo(title="", description="", language="en", canonical=None)
        sections = []

    # 3. JS fallback if needed
    used_js = False
    if not sections or static_content_too_weak(sections):
        js_html, clicks, scrolls, pages, js_errors = await js_scrape_with_interactions(url)
        errors.extend(js_errors)
        interactions.clicks.extend(clicks)
        interactions.scrolls = scrolls
        interactions.pages = pages or [url]

        if js_html:
            used_js = True
            try:
                meta, sections = static_scrape(js_html, url)
            except Exception as e:
                tb = "".join(traceback.format_exception_only(type(e), e)).strip()
                errors.append(ErrorItem(message=f"JS parse error: {tb}", phase="parse"))
        else:
            if not sections:
                interactions.pages = interactions.pages or [url]
    else:
        # static only
        interactions.pages = [url]

    # Ensure at least one section exists
    if not sections:
        dummy_section = Section(
            id="unknown-0",
            type="unknown",
            label="Page",
            sourceUrl=url,
            content={
                "headings": [],
                "text": "",
                "links": [],
                "images": [],
                "lists": [],
                "tables": [],
            },
            rawHtml="",
            truncated=False,
        )
        # Let Pydantic coerce dict -> SectionContent
        sections = [dummy_section]

    scraped_at = datetime.datetime.utcnow().isoformat() + "Z"

    if used_js and not meta.description:
        meta.description = "(JS-rendered content used; static fallback insufficient)"

    result = ScrapeResult(
        url=url,
        scrapedAt=scraped_at,
        meta=meta,
        sections=sections,
        interactions=interactions,
        errors=errors,
    )
    return ScrapeResponse(result=result)
