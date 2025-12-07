from typing import List, Tuple

from bs4 import BeautifulSoup

from ..core.config import STATIC_TEXT_THRESHOLD
from ..core.schemas import MetaInfo, Section
from .sections import clean_noise, extract_meta, build_sections_from_soup


def static_scrape(html: str, url: str) -> Tuple[MetaInfo, List[Section]]:
    """
    Perform static HTML parsing: noise cleaning, meta extraction, section grouping.
    """
    soup = BeautifulSoup(html, "lxml")
    clean_noise(soup)
    meta = extract_meta(soup, url)
    sections = build_sections_from_soup(soup, url)
    return meta, sections


def static_content_too_weak(sections: List[Section]) -> bool:
    """
    Heuristic: if total text length is too small, fall back to JS.
    """
    total_len = sum(len(s.content.text) for s in sections)
    return total_len < STATIC_TEXT_THRESHOLD
