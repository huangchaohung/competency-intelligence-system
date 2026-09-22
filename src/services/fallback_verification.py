"""Deterministic verification helpers for LLM-assisted fallback URLs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from src.core.exceptions import CompetencyIntelligenceError


VERIFIED_BY_URL = "✅ Verified by URL"
NEEDS_MANUAL_REVIEW = "🟡 Needs manual review"
ACCESS_BLOCKED = "🟠 Access blocked"
INVALID_URL = "🔴 Invalid URL"
MIN_VERIFICATION_WORDS = 25


@dataclass(frozen=True)
class FallbackVerificationResult:
    """Verification outcome for one LLM-recovered source URL."""

    title: str
    url: str
    status: str
    reason: str
    matched_terms: tuple[str, ...] = ()


class FallbackURLVerifier:
    """Verify LLM-recovered URLs without asking the LLM again."""

    def __init__(self, scanner) -> None:
        self._scanner = scanner

    def verify_items(self, items: list[dict[str, Any]], source_name: str = "LLM fallback recovery") -> list[FallbackVerificationResult]:
        """Verify every recovered item URL with a bounded deterministic fetch."""
        return [self.verify_item(item, source_name) for item in items]

    def verify_item(self, item: dict[str, Any], source_name: str = "LLM fallback recovery") -> FallbackVerificationResult:
        """Verify one recovered item by fetching its cited URL and matching key terms."""
        title = str(item.get("title") or "Untitled")
        url = str(item.get("url") or "")
        if not _is_https_url(url):
            return FallbackVerificationResult(title, url, INVALID_URL, "Recovered item does not contain a valid HTTPS URL.")
        try:
            page = self._scanner.fetch_url(url, source_name)
        except CompetencyIntelligenceError as error:
            return FallbackVerificationResult(title, url, _blocked_or_review_status(str(error)), str(error))
        text = " ".join((page.html or "").split()).lower()
        matched_terms = _matched_terms(item, text)
        if len(text.split()) < MIN_VERIFICATION_WORDS:
            return FallbackVerificationResult(title, url, NEEDS_MANUAL_REVIEW, "URL was reachable but returned too little readable text for verification.", matched_terms)
        if matched_terms:
            return FallbackVerificationResult(title, url, VERIFIED_BY_URL, "URL was reachable and contained terms from the recovered title or summary.", matched_terms)
        return FallbackVerificationResult(title, url, NEEDS_MANUAL_REVIEW, "URL was reachable but the recovered claim could not be matched clearly in the page text.", matched_terms)


def verification_rows(results: list[FallbackVerificationResult]) -> list[dict[str, str]]:
    """Return officer/IT-readable verification rows."""
    return [
        {
            "Title": result.title,
            "URL": result.url,
            "Verification": result.status,
            "Reason": result.reason,
            "Matched terms": ", ".join(result.matched_terms) if result.matched_terms else "None",
        }
        for result in results
    ]


def _is_https_url(value: str) -> bool:
    """Return whether a value is a valid HTTPS URL."""
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def _blocked_or_review_status(error: str) -> str:
    """Classify fetch failures into officer-facing verification status."""
    lowered = error.lower()
    if any(marker in lowered for marker in ("403", "forbidden", "cloudflare", "timeout", "timed out", "robots", "blocked", "ssl", "certificate")):
        return ACCESS_BLOCKED
    return NEEDS_MANUAL_REVIEW


def _matched_terms(item: dict[str, Any], text: str) -> tuple[str, ...]:
    """Return compact title/summary terms found in fetched page text."""
    title_terms = _important_terms(str(item.get("title") or ""))
    summary_terms = _important_terms(str(item.get("summary") or ""))
    matches: list[str] = []
    for term in [*title_terms[:6], *summary_terms[:8]]:
        if term in text and term not in matches:
            matches.append(term)
    return tuple(matches[:8])


def _important_terms(text: str) -> list[str]:
    """Extract rough meaningful words for lightweight URL verification."""
    stop_words = {"and", "the", "for", "with", "from", "this", "that", "into", "about", "course", "programme", "program", "resource"}
    terms: list[str] = []
    for raw in text.lower().replace("/", " ").replace("-", " ").split():
        term = "".join(char for char in raw if char.isalnum())
        if len(term) < 4 or term in stop_words:
            continue
        if term not in terms:
            terms.append(term)
    return terms
