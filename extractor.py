from typing import List, Dict, Any
from models import PageData

class LLMExtractor:
    """
    Placeholder for future LLM-based structured extraction/summarization.
    Integrate your Ollama / LangChain pipeline here later.
    """

    def summarize_pages(self, phrase: str, pages: List[PageData]) -> Dict[str, Any]:
        """
        Return a simple joined summary for now; replace with an LLM chain later.
        """
        top = pages[:3]
        focused_blocks = []
        for p in top:
            focused_blocks.append(f"--- PAGE: {p.title}\nURL: {p.url}\nSCORE: {p.relevance_score}\nCONTENT: {p.content}\n")
        return {
            "phrase": phrase,
            "focused_content": "\n".join(focused_blocks),
            "page_count": len(pages),
        }
