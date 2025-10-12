from pydantic import BaseModel
from typing import List

class LinkData(BaseModel):
    url: str
    text: str
    context: str
    relevance_score: int
    is_absolute: bool
    noun_matches: int

class PageData(BaseModel):
    url: str
    title: str
    content: str
    relevance_score: int
    depth: int

class CrawlResult(BaseModel):
    phrase: str
    base_url: str
    pages_scanned: int
    relevant_pages_found: int
    pages: List[PageData]
