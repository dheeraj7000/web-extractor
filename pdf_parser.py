import io
import re
import requests
from typing import Optional
from models import PageData
from config import USER_AGENT, MAX_TEXT_LENGTH, REQUEST_TIMEOUT

class PDFParser:
    def __init__(self):
        self.supported_extensions = [".pdf"]

    def is_pdf_url(self, url: str) -> bool:
        return any(url.lower().endswith(ext) for ext in self.supported_extensions)

    def download_pdf(self, url: str) -> Optional[bytes]:
        try:
            headers = {
                "User-Agent": USER_AGENT,
                "Accept": "application/pdf, */*",
            }
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            ctype = resp.headers.get("content-type", "").lower()
            if "pdf" in ctype or url.lower().endswith(".pdf"):
                return resp.content
            return None
        except Exception:
            return None

    def _extract_with_pymupdf(self, pdf_content: bytes) -> Optional[str]:
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            parts = []
            for page in doc:
                txt = page.get_text()
                if txt:
                    parts.append(txt)
            doc.close()
            return "\n".join(parts) if parts else None
        except Exception:
            return None

    def _extract_with_pdfplumber(self, pdf_content: bytes) -> Optional[str]:
        try:
            import pdfplumber
            parts = []
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        parts.append(t)
            return "\n".join(parts) if parts else None
        except Exception:
            return None

    def _extract_with_pypdf(self, pdf_content: bytes) -> Optional[str]:
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(pdf_content))
            parts = []
            for pg in reader.pages:
                t = pg.extract_text()
                if t:
                    parts.append(t)
            return "\n".join(parts) if parts else None
        except Exception:
            return None

    def parse_pdf(self, url: str, phrase: str) -> Optional[PageData]:
        pdf = self.download_pdf(url)
        if not pdf:
            return None

        text = (
            self._extract_with_pymupdf(pdf)
            or self._extract_with_pdfplumber(pdf)
            or self._extract_with_pypdf(pdf)
        )
        if not text or len(text.strip()) < 100:
            return None

        cleaned = re.sub(r"\s+", " ", text).strip()[:MAX_TEXT_LENGTH]
        return PageData(
            url=url,
            title=f"PDF: {url.split('/')[-1]}",
            content=cleaned,
            relevance_score=50,  # neutral baseline; final ranking comes from analyzer in crawler
            depth=0,
        )
