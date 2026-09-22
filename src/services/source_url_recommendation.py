"""Strict validation for AI-suggested replacement source URLs."""
from __future__ import annotations

import json
from urllib.parse import urlparse

from src.core.exceptions import RecommendationError


def parse_replacement_url_response(text: str, organisation: str) -> dict:
    """Parse a fixed URL-advice response while preserving organisation provenance."""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        raise RecommendationError("URL recommendation response was not valid JSON") from error
    if not isinstance(payload, dict) or set(payload) != {"organisation", "recommendations"}:
        raise RecommendationError("URL recommendation response has an invalid shape")
    if payload["organisation"].strip() != organisation.strip():
        raise RecommendationError("URL recommendation changed the organisation")
    if not isinstance(payload["recommendations"], list):
        raise RecommendationError("URL recommendations must be an array")
    recommendations = []
    for item in payload["recommendations"]:
        if not isinstance(item, dict) or set(item) != {"url", "reason"}:
            raise RecommendationError("URL recommendation item has an invalid shape")
        url = str(item["url"]).strip()
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise RecommendationError("URL recommendation must contain a valid HTTPS URL")
        recommendations.append({"url": url, "reason": str(item["reason"]).strip()})
    return {"organisation": organisation, "recommendations": recommendations}
