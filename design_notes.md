# Design Notes

## Static vs JS Fallback

- Strategy:
  - Always attempt static scraping first using `httpx` + `BeautifulSoup`.
  - After static parsing, compute the total length of `sections[*].content.text`.
  - If the total text length is `< 500` characters **or** static parsing yields **zero** sections, treat the result as “insufficient”.
  - In that case, fall back to JS rendering with Playwright, re-extract HTML, and re-run the same parsing pipeline without modifying logic.

## Wait Strategy for JS

- [x] Network idle  
- [x] Fixed sleep  
- [x] Wait for selectors (indirectly via pauses after interactions)

- Details:
  - Initial navigation uses  
    `page.goto(url, wait_until="networkidle", timeout=30000)`
  - After each interaction (tab click, load-more click, scroll), wait **1–1.5 seconds** via `wait_for_timeout` to give the page a chance to load new DOM.
  - No selector-specific waits are used to keep logic generic; the scraper relies on network-idle and short deterministic sleeps.

## Click & Scroll Strategy

- **Click flows implemented:**
  - Attempt clicking tab-like elements: `[role='tab']`, `[data-tab]` (bounded: up to 3).
  - Attempt clicking buttons/links containing:  
    `"load more"`, `"show more"`, `"more results"`, `"next"`.
  - Every click is logged in `interactions.clicks` with a short description: selector + truncated text.

- **Scroll / pagination approach:**
  - Perform **3 scroll iterations**, each scrolling half the viewport height with `window.scrollBy`.
  - After each scroll, wait ~**1.5 seconds** for content to load.
  - Record distinct URLs in `interactions.pages` (initial + any URL changes after interactions).

- **Stop conditions (max depth / timeout):**
  - Max **3 scrolls**.
  - Max **3 tab-like clicks**.
  - No recursive pagination; interactions are bounded for predictable runtime.

## Section Grouping & Labels

- **How DOM is grouped into sections:**
  - Use semantic landmarks: `header`, `nav`, `main`, `section`, `footer` as top-level section boundaries.
  - If none exist, use top-level `div`s; otherwise treat the whole `<body>` as a single section.
  - Each section is processed into structured `content`: headings, text, lists, tables, images, and links.

- **How `type` and `label` are derived:**
  - `type` inference:
    - `header` → `hero`
    - `nav` → `nav`
    - `footer` → `footer`
    - `.pricing*` → `pricing`
    - `.faq*` → `faq`
    - `.grid*` → `grid`
    - `section` / `main` → `section`
    - Otherwise → `unknown`
  - `label`:
    - Prefer the first heading inside the section (trimmed).
    - Fallback: first 5–7 words of section body text.
    - If empty: `"Section"`.

## Noise Filtering & Truncation

- **Noise filtering:**
  - Remove DOM elements likely to be cookie banners or overlays.
  - Keywords checked in class/id/text:  
    `cookie`, `consent`, `banner`, `gdpr`, `modal`, `popup`, `subscribe`, `newsletter`.
  - Matched elements are removed before section extraction.

- **Truncating `rawHtml` and setting `truncated`:**
  - Convert each section’s element to an HTML string.
  - If the HTML string length is **> 2000 characters**, truncate to **2000 chars** and set:  
    `truncated: true`
  - Otherwise keep full HTML and set:  
    `truncated: false`
