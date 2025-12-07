from typing import List, Tuple, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from ..core.config import RAW_HTML_LIMIT
from ..core.schemas import MetaInfo, Section, SectionContent, LinkItem, ImageItem


def is_noise(tag: Tag) -> bool:
    """Very simple noise filter: cookie banners, modals, popups etc."""
    cls = " ".join(tag.get("class", [])).lower()
    id_ = (tag.get("id") or "").lower()
    text_sample = " ".join(tag.stripped_strings).lower()[:80]

    keywords = [
        "cookie", "consent", "banner", "gdpr",
        "modal", "popup", "subscribe", "newsletter"
    ]
    for kw in keywords:
        if kw in cls or kw in id_ or kw in text_sample:
            return True
    return False


def clean_noise(soup: BeautifulSoup) -> None:
    candidates = soup.find_all(True)
    for tag in candidates:
        try:
            if is_noise(tag):
                tag.decompose()
        except Exception:
            continue


def extract_meta(soup: BeautifulSoup, base_url: str) -> MetaInfo:
    # Title
    title_tag = soup.find("title")
    og_title = soup.find("meta", attrs={"property": "og:title"})
    title = (title_tag.string or "").strip() if title_tag else ""
    if og_title and og_title.get("content"):
        title = og_title["content"].strip() or title

    # Description
    desc_tag = soup.find("meta", attrs={"name": "description"})
    og_desc = soup.find("meta", attrs={"property": "og:description"})
    description = ""
    if desc_tag and desc_tag.get("content"):
        description = desc_tag["content"].strip()
    elif og_desc and og_desc.get("content"):
        description = og_desc["content"].strip()

    # Language
    html_tag = soup.find("html")
    language = "en"
    if html_tag and html_tag.get("lang"):
        language = html_tag.get("lang").strip()

    # Canonical
    canonical_tag = soup.find("link", rel="canonical")
    canonical = canonical_tag.get("href").strip() if canonical_tag and canonical_tag.get("href") else None
    if canonical:
        canonical = urljoin(base_url, canonical)

    return MetaInfo(
        title=title or "",
        description=description or "",
        language=language or "en",
        canonical=canonical,
    )


def extract_text(tag: Tag) -> str:
    return " ".join(tag.stripped_strings)


def extract_lists(section: Tag) -> List[List[str]]:
    lists: List[List[str]] = []
    for ul in section.find_all(["ul", "ol"]):
        items = [li.get_text(strip=True) for li in ul.find_all("li")]
        if items:
            lists.append(items)
    return lists


def extract_tables(section: Tag) -> List[Any]:
    tables: List[Any] = []
    for table in section.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    return tables


def make_absolute_links(section: Tag, base_url: str) -> List[LinkItem]:
    links: List[LinkItem] = []
    for a in section.find_all("a", href=True):
        href_abs = urljoin(base_url, a["href"])
        text = a.get_text(strip=True)
        links.append(LinkItem(text=text, href=href_abs))
    return links


def extract_images(section: Tag, base_url: str) -> List[ImageItem]:
    images: List[ImageItem] = []
    for img in section.find_all("img", src=True):
        src_abs = urljoin(base_url, img["src"])
        alt = img.get("alt", "").strip()
        images.append(ImageItem(src=src_abs, alt=alt))
    return images


def guess_section_type(tag: Tag) -> str:
    name = tag.name.lower()
    cls = " ".join(tag.get("class", [])).lower()

    if name == "header":
        return "hero"
    if name == "nav":
        return "nav"
    if name == "footer":
        return "footer"
    if "pricing" in cls:
        return "pricing"
    if "faq" in cls:
        return "faq"
    if "grid" in cls:
        return "grid"
    if name in ("section", "main"):
        return "section"
    return "unknown"


def derive_label(headings: List[str], text: str) -> str:
    if headings:
        return headings[0][:80]
    words = text.split()
    return " ".join(words[:7]) if words else "Section"


def section_candidates(soup: BeautifulSoup) -> List[Tag]:
    tags: List[Tag] = []
    for name in ["header", "nav", "main", "section", "footer"]:
        tags.extend(soup.find_all(name))
    # fallback to body if nothing else
    if not tags:
        if soup.body:
            tags = [soup.body]
        else:
            tags = [soup]
    return tags


def html_snippet(tag: Tag, limit: int = RAW_HTML_LIMIT) -> Tuple[str, bool]:
    html = str(tag)
    if len(html) > limit:
        return html[:limit], True
    return html, False


def build_sections_from_soup(soup: BeautifulSoup, base_url: str) -> List[Section]:
    sections: List[Section] = []
    candidates = section_candidates(soup)

    for idx, sec in enumerate(candidates):
        headings_tags = sec.find_all(["h1", "h2", "h3"])
        headings = [ht.get_text(strip=True) for ht in headings_tags if ht.get_text(strip=True)]
        text = extract_text(sec)

        # Skip sections with almost no text and no headings
        if len(text) < 20 and not headings:
            continue

        links = make_absolute_links(sec, base_url)
        images = extract_images(sec, base_url)
        lists = extract_lists(sec)
        tables = extract_tables(sec)
        raw_html, truncated = html_snippet(sec)
        sec_type = guess_section_type(sec)
        label = derive_label(headings, text)

        sections.append(
            Section(
                id=f"{sec_type}-{idx}",
                type=sec_type,
                label=label,
                sourceUrl=base_url,
                content=SectionContent(
                    headings=headings,
                    text=text,
                    links=links,
                    images=images,
                    lists=lists,
                    tables=tables,
                ),
                rawHtml=raw_html,
                truncated=truncated,
            )
        )

    return sections
