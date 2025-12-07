import traceback
from typing import List, Tuple

from playwright.async_api import async_playwright

from ..core.config import (
    PLAYWRIGHT_TIMEOUT,
    JS_SCROLL_DEPTH,
    MAX_TAB_CLICKS,
)
from ..core.schemas import ErrorItem


async def js_scrape_with_interactions(
    url: str,
) -> Tuple[str, List[str], int, List[str], List[ErrorItem]]:
    """
    Returns:
        html_str, clicks, scrolls, pages, errors
    """
    clicks: List[str] = []
    pages: List[str] = []
    scrolls = 0
    errors: List[ErrorItem] = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT)
            pages.append(page.url)

            # Try clicking tab-like elements
            tab_selectors = [
                "[role='tab']",
                "[data-tab]",
            ]
            for sel in tab_selectors:
                elements = await page.query_selector_all(sel)
                for el in elements[:MAX_TAB_CLICKS]:
                    try:
                        txt = (await el.inner_text()).strip()
                        desc = f"{sel} -> '{txt[:30]}'"
                        await el.click()
                        clicks.append(desc)
                        await page.wait_for_timeout(1000)
                    except Exception:
                        errors.append(ErrorItem(message=f"Failed tab click {sel}", phase="interaction"))
                        continue

            # Try clicking “Load more” / “Show more” type buttons/links
            load_more_texts = ["load more", "show more", "more results", "next"]
            buttons = await page.query_selector_all("button, a")
            for btn in buttons[:20]:
                try:
                    txt = (await btn.inner_text()).strip().lower()
                    if any(k in txt for k in load_more_texts):
                        desc = f"click: {txt[:40]}"
                        await btn.click()
                        clicks.append(desc)
                        await page.wait_for_timeout(1500)
                except Exception:
                    continue

            # Scroll depth ≥ 3
            for _ in range(JS_SCROLL_DEPTH):
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight / 2);")
                scrolls += 1
                await page.wait_for_timeout(1500)

            pages.append(page.url)

            content = await page.content()
            await context.close()
            await browser.close()

            return content, clicks, scrolls, pages, errors

    except Exception as e:
        tb = "".join(traceback.format_exception_only(type(e), e)).strip()
        errors.append(ErrorItem(message=f"Playwright error: {tb}", phase="render"))
        return "", clicks, scrolls, pages, errors
