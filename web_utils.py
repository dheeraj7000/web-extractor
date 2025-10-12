import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin as _urljoin, urlparse as _urlparse
from typing import Optional, Tuple
from config import USER_AGENT, REQUEST_TIMEOUT, MAX_TEXT_LENGTH

class WebUtils:
    @staticmethod
    def create_session() -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        return session

    @staticmethod
    def fetch_html(session: requests.Session, url: str) -> Optional[BeautifulSoup]:
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            ctype = resp.headers.get("content-type", "").lower()
            if "html" not in ctype:
                return None
            return BeautifulSoup(resp.content, "html.parser")
        except Exception:
            return None

    @staticmethod
    def extract_clean_text(soup: BeautifulSoup, max_length: int = MAX_TEXT_LENGTH) -> str:
        page_text = soup.get_text(separator=" ")
        cleaned_text = re.sub(r"\s+", " ", page_text).strip()[:max_length]
        return cleaned_text

    @staticmethod
    def is_same_domain(base_url: str, test_url: str) -> bool:
        base_domain = _urlparse(base_url).netloc
        test_domain = _urlparse(test_url).netloc
        return base_domain == test_domain

    @staticmethod
    def urljoin(base_url: str, relative_url: str) -> str:
        return _urljoin(base_url, relative_url)

    @staticmethod
    def urlparse(url: str):
        return _urlparse(url)

    @staticmethod
    def get_title(soup: BeautifulSoup) -> str:
        title = ""
        if soup and soup.title and soup.title.string:
            title = soup.title.string.strip()
        return title
