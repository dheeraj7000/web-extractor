import json
import argparse
from typing import Optional
from crawler import WebExtractorCrawler
from extractor import LLMExtractor

def run(phrase: str, base_url: str, max_pages: int, allow_external: bool, depth: int, summarize: bool):
    crawler = WebExtractorCrawler(allow_external=allow_external, max_depth=depth, polite_delay=1.0)
    result = crawler.intelligent_crawl(base_url, phrase, max_pages=max_pages)

    output = {
        "phrase": result.phrase,
        "base_url": result.base_url,
        "pages_scanned": result.pages_scanned,
        "relevant_pages_found": result.relevant_pages_found,
        "pages": [p.model_dump() for p in result.pages],
    }

    if summarize:
        llm = LLMExtractor()  # placeholder – no LLM call yet
        output["summary"] = llm.summarize_pages(phrase, result.pages)

    print(json.dumps(output, indent=2, ensure_ascii=False))

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Web Extractor: phrase-based focused crawler for any topic or website (domain-scoped by default)."
    )
    parser.add_argument("--phrase", required=True, help="Phrase/sentence to search for.")
    parser.add_argument("--url", required=True, help="Base URL to start crawling from.")
    parser.add_argument("--max-pages", type=int, default=10, help="Maximum relevant pages to return.")
    parser.add_argument("--allow-external", action="store_true", help="Allow following external links.")
    parser.add_argument("--depth", type=int, default=3, help="Maximum crawl depth.")
    parser.add_argument("--summarize", action="store_true", help="Include a simple (LLM-ready) focused summary.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run(
        phrase=args.phrase,
        base_url=args.url,
        max_pages=args.max_pages,
        allow_external=args.allow_external,
        depth=args.depth,
        summarize=args.summarize,
    )
