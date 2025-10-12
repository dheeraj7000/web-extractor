import re
from typing import List
from config import SCORING_WEIGHTS

class ContentAnalyzer:
    @staticmethod
    def extract_nouns_from_phrase(phrase: str) -> List[str]:
        """
        Lightweight 'noun-like' token extractor:
        - split to words
        - drop common stop words
        - keep tokens length > 3
        - include short prefixes for longer tokens to capture partials
        """
        stop_words = {
            "foundation", "award", "program", "scholarship", "grant", "fellowship",
            "prize", "fund", "in", "for", "and", "the", "of", "to", "on", "with",
            "by", "from", "about", "this", "that", "these", "those", "using",
            "use", "a", "an", "or", "not", "into", "over", "under", "as"
        }
        words = re.split(r"\W+", phrase.lower())
        tokens = [w for w in words if w and w not in stop_words and len(w) > 3]

        expanded = []
        for t in tokens:
            expanded.append(t)
            if len(t) > 6:
                expanded.append(t[:5])
        return list(set(expanded))

    @staticmethod
    def calculate_relevance_score(title: str, content: str, phrase: str) -> int:
        """
        Title/content scoring using general keywords (config) + phrase exact match boosts.
        """
        score = 0
        ct_phrase = phrase.lower()
        ct_body = (content or "").lower()
        ct_title = (title or "").lower()

        # Phrase exact matches
        if ct_phrase in ct_title:
            score += 30
        if ct_phrase in ct_body:
            score += 20

        # Keyword weights (general-purpose)
        for kw, wt in SCORING_WEIGHTS["keyword_weights"].items():
            if kw in ct_title:
                score += wt
            if kw in ct_body:
                score += wt // 2

        return score

    @classmethod
    def is_relevant_page(cls, url: str, title: str, content: str, phrase: str) -> bool:
        """
        Keep the core strategies:
        - Strategy 1: exact phrase match (auto-pass)
        - Strategy 2: long substring match (>= 60% of phrase length)
        """
        clean_phrase = phrase.lower().strip()
        combined = ((title or "") + " " + (content or "")).lower()

        score = 0

        # Strategy 1: Exact match
        if clean_phrase and clean_phrase in combined:
            score += SCORING_WEIGHTS["exact_match"]

        # Strategy 2: Long substring
        words = clean_phrase.split()
        if len(words) > 1:
            min_len = max(3, int(len(clean_phrase) * 0.6))
            for i in range(len(words)):
                for j in range(i + 1, len(words) + 1):
                    sub = " ".join(words[i:j])
                    if len(sub) >= min_len and sub in combined and len(sub) > len(clean_phrase) * 0.5:
                        score += SCORING_WEIGHTS["substring_match"]

        # Auto-qualify checks
        if clean_phrase and clean_phrase in combined:
            return True

        if len(words) > 1:
            min_len = max(3, int(len(clean_phrase) * 0.6))
            for i in range(len(words)):
                for j in range(i + 1, len(words) + 1):
                    sub = " ".join(words[i:j])
                    if len(sub) >= min_len and sub in combined and len(sub) > len(clean_phrase) * 0.5:
                        return True

        # Fallback threshold (kept same as original behavior)
        return score >= 12
