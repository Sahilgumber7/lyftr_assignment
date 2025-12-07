
---

## 📝 `design_notes.md` (root)

```md
# Design Notes

## Static vs JS Fallback

- Strategy:
  - Always attempt static scraping first using `httpx` + `BeautifulSoup`.
  - After static parsing, compute the total length of `sections[*].content.text`.
  - If the total text length is `< 500` characters OR static parsing yields no sections, we treat it as "insufficient".
  - In that case, we fall back to JS rendering with Playwright, re-extract HTML, and re-run the same parsing pipeline.

## Wait Strategy for JS

- [x] Network idle
- [x] Fixed sleep
- [x] Wait for selectors (indirectly: we wait after clicks)
- Details:
  - Initial navigation uses `page.goto(url, wait_until="networkidle", timeout=30000)`.
  - After each interaction (tab click / load more click / scroll) we wait between 1–1.5 seconds (`wait_for_timeout`) to allow content to load.
  - We do not wait for specific content selectors (to keep the logic generic), but rely on network idle and short sleeps.

## Click & Scroll Strategy

- Click flows implemented:
  - Try clicking elements that look like tabs: `[role='tab']` and `[data-tab]` (up to a small number).
  - Try clicking buttons/links whose text includes "load more", "show more", "more results", or "next".
  - Each click is recorded in `interactions.clicks` as a small description (selector + truncated text).

- Scroll / pagination approach:
  - Perform 3 scroll actions: each scroll moves half the viewport height down via `window.scrollBy`.
  - After every scroll, wait ~1.5s for new content to load.
  - Collect distinct URLs in `interactions.pages` (the initial page plus any post-interaction URL).

- Stop conditions (max depth / timeout):
  - Hard-coded limit of 3 scroll iterations.
  - We only click a bounded number of tab-like elements (up to 3).
  - We do not recursively follow pagination links beyond those interactions to keep runtime bounded.

## Section Grouping & Labels

- How you group DOM into sections:
  - Use semantic landmarks: `header`, `nav`, `main`, `section`, and `footer` as primary section boundaries.
  - If none are found, fallback to top-level `div`s or the `<body>` as a single section.
  - Each candidate section is processed into `content` fields: headings, text, links, images, lists, tables.

- How you derive section `type` and `label`:
  - `type`:
    - `header` → `hero`
    - `nav` → `nav`
    - `footer` → `footer`
    - `.pricing*` → `pricing`
    - `.faq*` → `faq`
    - `.grid*` → `grid`
    - `section` / `main` → `section`
    - Otherwise → `unknown`
  - `label`:
    - If section has headings, use the first heading text (truncated).
    - Else, derive label from the first 5–7 words of section text.
    - If both are missing, default to `"Section"`.

## Noise Filtering & Truncation

- What you filter out:
  - Simple heuristic: remove elements whose class, id, or short text sample suggests cookie banners or overlays.
  - Keywords: `cookie`, `consent`, `banner`, `gdpr`, `modal`, `popup`, `subscribe`, `newsletter`.
  - Matching elements are removed from the DOM before section extraction.

- How you truncate `rawHtml` and set `truncated`:
  - For each section, convert the element to HTML string.
  - If the string length exceeds 2000 characters, truncate to 2000 and set `truncated: true`.
  - Otherwise, keep the full HTML and set `truncated: false`.
