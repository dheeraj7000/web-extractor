import time
import re
from collections import deque
from typing import List, Set
from bs4 import BeautifulSoup
from web_utils import WebUtils
from content_analyzer import ContentAnalyzer
from pdf_parser import PDFParser
from models import LinkData, PageData, CrawlResult
from config import SCORING_WEIGHTS

class WebExtractorCrawler:
    def __init__(self, allow_external: bool = False, max_depth: int = 3, polite_delay: float = 1.0):
        self.session = WebUtils.create_session()
        self.pdf_parser = PDFParser()
        self.visited: Set[str] = set()
        self.allow_external = allow_external
        self.max_depth = max_depth
        self.polite_delay = polite_delay

    def extract_links_with_context(self, url: str, phrase: str) -> List[LinkData]:
        soup = WebUtils.fetch_html(self.session, url)
        if not soup:
            return []

        links: List[LinkData] = []
        nouns = ContentAnalyzer.extract_nouns_from_phrase(phrase)

        for a in soup.find_all("a", href=True):
            link_url = WebUtils.urljoin(url, a["href"])
            link_text = a.get_text(strip=True)
            parent_ctx = a.parent.get_text(strip=True) if a.parent else ""
            combined = (link_text + " " + parent_ctx).lower()

            rel = 0
            # phrase in link text
            if phrase.lower() in link_text.lower():
                rel += 25

            # nouns in surrounding context
            noun_matches = sum(1 for n in nouns if n in combined)
            if noun_matches > 0:
                rel += noun_matches * SCORING_WEIGHTS["noun_match_unit"]

            # generic keyword boost
            for k, w in SCORING_WEIGHTS["keyword_weights"].items():
                if k in combined:
                    rel += SCORING_WEIGHTS["link_keyword_boost"]

            links.append(LinkData(
                url=link_url,
                text=link_text,
                context=parent_ctx[:200],
                relevance_score=rel,
                is_absolute=bool(WebUtils.urlparse(link_url).netloc),
                noun_matches=noun_matches
            ))
        return links

    def scrape_html_page(self, url: str, phrase: str, depth: int) -> PageData | None:
        soup = WebUtils.fetch_html(self.session, url)
        if not soup:
            return None
        title = WebUtils.get_title(soup)
        content = WebUtils.extract_clean_text(soup)
        if ContentAnalyzer.is_relevant_page(url, title, content, phrase):
            score = ContentAnalyzer.calculate_relevance_score(title, content, phrase)
            return PageData(
                url=url,
                title=title or url,
                content=content,
                relevance_score=score,
                depth=depth
            )
        return None

    def intelligent_crawl(self, base_url: str, phrase: str, max_pages: int = 10) -> CrawlResult:
        queue = deque([(base_url, 0)])
        relevant: List[PageData] = []

        while queue and len(relevant) < max_pages and len(self.visited) < 100:
            current, depth = queue.popleft()
            if current in self.visited:
                continue
            self.visited.add(current)

            # PDF handling first
            if self.pdf_parser.is_pdf_url(current):
                page = self.pdf_parser.parse_pdf(current, phrase)
                if page:
                    page.relevance_score = ContentAnalyzer.calculate_relevance_score(page.title, page.content, phrase)
                    relevant.append(page)
                time.sleep(self.polite_delay)
                continue

            # HTML page
            page = self.scrape_html_page(current, phrase, depth)
            if page:
                relevant.append(page)

            # expand links
            if depth < self.max_depth:
                links = self.extract_links_with_context(current, phrase)
                links.sort(key=lambda x: (x.relevance_score, x.noun_matches), reverse=True)

                for lk in links[:25]:
                    if lk.url in self.visited:
                        continue
                    if not self.allow_external and not WebUtils.is_same_domain(base_url, lk.url):
                        continue
                    if lk.relevance_score > SCORING_WEIGHTS["link_auto_threshold"]:
                        queue.append((lk.url, depth + 1))

            time.sleep(self.polite_delay)

        # sort final relevant pages
        relevant.sort(key=lambda p: p.relevance_score, reverse=True)
        return CrawlResult(
            phrase=phrase,
            base_url=base_url,
            pages_scanned=len(self.visited),
            relevant_pages_found=len(relevant),
            pages=relevant
        )
