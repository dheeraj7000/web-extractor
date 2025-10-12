# --- Runtime / HTTP ---
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)
REQUEST_TIMEOUT = 10  # seconds
MAX_TEXT_LENGTH = 2000  # characters to keep per page for scoring

# --- Scoring Weights (general-purpose; not scholarship-specific) ---
SCORING_WEIGHTS = {
    # exact match of the full phrase in title/body
    "exact_match": 100,
    # long substring of the phrase (>= 60% of phrase length)
    "substring_match": 80,
    # keyword weights used by ContentAnalyzer.calculate_relevance_score
    "keyword_weights": {
        # general discovery/overview words
        "overview": 4,
        "introduction": 4,
        "background": 3,
        "summary": 3,
        # documentation / specs / research
        "documentation": 5,
        "specification": 5,
        "guide": 4,
        "tutorial": 4,
        "research": 4,
        "results": 4,
        "paper": 3,
        # usage / how-to
        "install": 3,
        "usage": 3,
        "example": 3,
        "demo": 3,
        # logistics / details
        "contact": 3,
        "faq": 3,
        "download": 3,
        "requirements": 3,
        "references": 3,
        # context
        "news": 2,
        "press": 2,
        "announcement": 2,
    },
    # link-level boosts
    "link_keyword_boost": 5,
    "noun_match_unit": 8,
    "link_auto_threshold": 3,
}
