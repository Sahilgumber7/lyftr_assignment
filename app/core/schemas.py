from typing import List, Optional, Any

from pydantic import BaseModel, HttpUrl


class ScrapeRequest(BaseModel):
    url: HttpUrl


class LinkItem(BaseModel):
    text: str
    href: str


class ImageItem(BaseModel):
    src: str
    alt: str


class ErrorItem(BaseModel):
    message: str
    phase: str


class SectionContent(BaseModel):
    headings: List[str]
    text: str
    links: List[LinkItem]
    images: List[ImageItem]
    lists: List[List[str]]
    tables: List[Any]


class Section(BaseModel):
    id: str
    type: str
    label: str
    sourceUrl: str
    content: SectionContent
    rawHtml: str
    truncated: bool


class MetaInfo(BaseModel):
    title: str
    description: str
    language: str
    canonical: Optional[str] = None


class Interactions(BaseModel):
    clicks: List[str]
    scrolls: int
    pages: List[str]


class ScrapeResult(BaseModel):
    url: str
    scrapedAt: str
    meta: MetaInfo
    sections: List[Section]
    interactions: Interactions
    errors: List[ErrorItem]


class ScrapeResponse(BaseModel):
    result: ScrapeResult
