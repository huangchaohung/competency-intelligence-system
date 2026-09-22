"""Governed LLM fallback recovery for sources deterministic crawling could not use."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.parse import urlparse

from openai import OpenAI, OpenAIError

from src.core.exceptions import RecommendationError
from src.services.operational_logger import NullOperationalLogger, OperationalLogger
from src.services.source_health_service import fallback_prompt_payload


ALLOWED_RECOVERY_CLASSES = {
    "competency_or_standard",
    "course_programme_or_resource",
    "research_or_capability",
    "signal_or_topic",
}
ALLOWED_EXPLICITNESS = {"EXPLICIT", "INFERRED"}
MAX_RECOVERED_ITEMS = 25
MAX_SUMMARY_CHARS = 1_200
MAX_REPLACEMENT_URLS = 5
FALLBACK_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "organisation": {"type": "string"},
        "source_url": {"type": "string"},
        "recovered_items": {
            "type": "array",
            "maxItems": MAX_RECOVERED_ITEMS,
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "url": {"type": "string"},
                    "evidence_class": {"type": "string", "enum": sorted(ALLOWED_RECOVERY_CLASSES)},
                    "summary": {"type": "string"},
                    "explicit_or_inferred": {"type": "string", "enum": sorted(ALLOWED_EXPLICITNESS)},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["title", "url", "evidence_class", "summary", "explicit_or_inferred", "confidence"],
                "additionalProperties": False,
            },
        },
        "source_maintenance_advice": {
            "type": "object",
            "properties": {
                "recommendation_type": {
                    "type": "string",
                    "enum": [
                        "KEEP_CURRENT_SOURCE",
                        "REPLACE_SOURCE_URL",
                        "DISABLE_SOURCE",
                        "NEEDS_IT_ACCESS_REVIEW",
                        "USE_BROWSER_RENDERING",
                        "USE_PDF_OR_RESOURCE_HUB",
                        "NO_CLEAR_ADVICE",
                    ],
                },
                "recommended_replacement_urls": {"type": "array", "maxItems": MAX_REPLACEMENT_URLS, "items": {"type": "string"}},
                "reason": {"type": "string"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            },
            "required": ["recommendation_type", "recommended_replacement_urls", "reason", "confidence"],
            "additionalProperties": False,
        },
        "recovery_notes": {"type": "string"},
    },
    "required": ["organisation", "source_url", "recovered_items", "source_maintenance_advice", "recovery_notes"],
    "additionalProperties": False,
}
ALLOWED_SOURCE_MAINTENANCE_ADVICE = {
    "KEEP_CURRENT_SOURCE",
    "REPLACE_SOURCE_URL",
    "DISABLE_SOURCE",
    "NEEDS_IT_ACCESS_REVIEW",
    "USE_BROWSER_RENDERING",
    "USE_PDF_OR_RESOURCE_HUB",
    "NO_CLEAR_ADVICE",
}


@dataclass(frozen=True)
class RecoveredFallbackItem:
    """One provenance-preserving item recovered by a governed fallback pass."""

    title: str
    url: str
    evidence_class: str
    summary: str
    explicit_or_inferred: str
    confidence: float


@dataclass(frozen=True)
class FallbackRecoveryResult:
    """Validated fallback recovery result for one source candidate."""

    organisation: str
    source_url: str
    recovered_items: tuple[RecoveredFallbackItem, ...]
    source_maintenance_advice: dict
    recovery_notes: str


class OpenAIFallbackRecoverer:
    """Run an explicit, officer-approved LLM recovery pass for one source."""

    def __init__(self, model: str | None = None, operational_logger: OperationalLogger | NullOperationalLogger | None = None) -> None:
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-5.6-terra")
        self._operational_logger = operational_logger or NullOperationalLogger()

    def recover(self, candidate: dict) -> FallbackRecoveryResult:
        """Recover structured STE source items for one approved fallback candidate."""
        if not os.getenv("OPENAI_API_KEY"):
            raise RecommendationError("OPENAI_API_KEY is not configured")
        payload = fallback_prompt_payload(candidate)
        prompt = self._build_prompt(payload)
        self._operational_logger.event(
            "llm_fallback_recovery_request",
            {
                "model": self._model,
                "endpoint": "responses.create",
                "source": payload["source"],
                "scan_health": payload["scan_health"],
                "prompt": prompt,
            },
        )
        try:
            response = OpenAI().responses.create(
                model=self._model,
                input=prompt,
                text={"format": {"type": "json_schema", "name": "fallback_recovery", "schema": FALLBACK_RESPONSE_SCHEMA, "strict": True}},
            )
        except OpenAIError as error:
            self._operational_logger.event("llm_fallback_recovery_error", {"model": self._model, "source": payload["source"], "error": str(error)})
            raise RecommendationError(f"OpenAI fallback recovery failed: {error}") from error
        if not response.output_text:
            self._operational_logger.event("llm_fallback_recovery_empty_response", {"model": self._model, "source": payload["source"], "usage": self._serialise_usage(response)})
            raise RecommendationError("OpenAI returned no fallback recovery content")
        self._operational_logger.event(
            "llm_fallback_recovery_response",
            {
                "model": self._model,
                "source": payload["source"],
                "raw_response": response.output_text,
                "usage": self._serialise_usage(response),
            },
        )
        try:
            result = parse_fallback_recovery_response(response.output_text)
        except RecommendationError as error:
            self._operational_logger.event("llm_fallback_recovery_parse_error", {"model": self._model, "source": payload["source"], "error": str(error), "raw_response": response.output_text})
            raise
        self._operational_logger.event(
            "llm_fallback_recovery_parsed",
            {
                "model": self._model,
                "source": payload["source"],
                "recovered_item_count": len(result.recovered_items),
                "evidence_classes": [item.evidence_class for item in result.recovered_items],
            },
        )
        return result

    @staticmethod
    def _build_prompt(payload: dict) -> str:
        """Build the governed fallback prompt from the existing preview payload."""
        instructions = (
            "You are performing an explicitly approved LLM fallback recovery pass for an STE competency intelligence prototype. "
            "Use the source information and constraints below. Recover only Science, Technology, and Engineering competency intelligence. "
            "Prioritise explicit competency frameworks, standards, courses, programmes, certifications, official resources, and research capability material. "
            "Treat news or publications only as signal_or_topic evidence. "
            "Do not invent source URLs, organisations, courses, competencies, or standards. "
            "If useful content cannot be reliably recovered, return an empty recovered_items array and explain why in recovery_notes. "
            "Also assess whether the configured source URL itself should be kept, replaced, disabled, reviewed by IT, browser-rendered, or redirected toward a PDF/resource hub. "
            "If you recommend replacement URLs, provide only exact official HTTP(S) URLs from the same organisation or clearly relevant official subdomain. Do not invent URLs. "
            "Source-maintenance advice is advisory only; it will not automatically update the source catalogue. "
            "Return only JSON that conforms to the provided schema."
        )
        return f"{instructions}\n\nFALLBACK_REQUEST:\n{json.dumps(payload)}"

    @staticmethod
    def _serialise_usage(response) -> dict:
        """Return OpenAI usage metadata when available without depending on SDK shape."""
        usage = getattr(response, "usage", None)
        if usage is None:
            return {}
        if hasattr(usage, "model_dump"):
            return usage.model_dump()
        if isinstance(usage, dict):
            return usage
        return {key: getattr(usage, key) for key in dir(usage) if key.endswith("tokens") and not key.startswith("_")}


def fallback_recovery_result_payload(result: FallbackRecoveryResult) -> dict:
    """Return a JSON-safe payload for UI display and download."""
    source_maintenance_advice = dict(result.source_maintenance_advice)
    source_maintenance_advice["recommended_replacement_urls"] = list(source_maintenance_advice.get("recommended_replacement_urls", ()))
    return {
        "organisation": result.organisation,
        "source_url": result.source_url,
        "recovered_item_count": len(result.recovered_items),
        "recovered_items": [
            {
                "title": item.title,
                "url": item.url,
                "evidence_class": item.evidence_class,
                "summary": item.summary,
                "explicit_or_inferred": item.explicit_or_inferred,
                "confidence": item.confidence,
            }
            for item in result.recovered_items
        ],
        "source_maintenance_advice": source_maintenance_advice,
        "recovery_notes": result.recovery_notes,
    }


def parse_fallback_recovery_response(text: str) -> FallbackRecoveryResult:
    """Strictly validate a fallback recovery JSON response."""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        raise RecommendationError("Fallback recovery response was not valid JSON") from error
    if not isinstance(payload, dict) or set(payload) != {"organisation", "source_url", "recovered_items", "source_maintenance_advice", "recovery_notes"}:
        raise RecommendationError("Fallback recovery response has an invalid top-level shape")
    if not isinstance(payload["organisation"], str) or not payload["organisation"].strip():
        raise RecommendationError("Fallback recovery response must include an organisation")
    if not _is_http_url(payload["source_url"]):
        raise RecommendationError("Fallback recovery response must include a valid source URL")
    items = payload["recovered_items"]
    if not isinstance(items, list) or len(items) > MAX_RECOVERED_ITEMS:
        raise RecommendationError("Fallback recovery response has an invalid recovered_items list")
    recovered_items: list[RecoveredFallbackItem] = []
    for item in items:
        recovered_items.append(_parse_recovered_item(item))
    source_maintenance_advice = _parse_source_maintenance_advice(payload["source_maintenance_advice"])
    if not isinstance(payload["recovery_notes"], str):
        raise RecommendationError("Fallback recovery response must include recovery notes")
    return FallbackRecoveryResult(payload["organisation"].strip(), payload["source_url"].strip(), tuple(recovered_items), source_maintenance_advice, payload["recovery_notes"].strip())


def _parse_recovered_item(item: object) -> RecoveredFallbackItem:
    """Validate one recovered fallback item."""
    if not isinstance(item, dict) or set(item) != {"title", "url", "evidence_class", "summary", "explicit_or_inferred", "confidence"}:
        raise RecommendationError("Fallback recovery item has an invalid shape")
    confidence = item["confidence"]
    if not isinstance(confidence, (float, int)) or not 0 <= confidence <= 1:
        raise RecommendationError("Fallback recovery item has an invalid confidence")
    if item["evidence_class"] not in ALLOWED_RECOVERY_CLASSES:
        raise RecommendationError("Fallback recovery item has an invalid evidence class")
    if item["explicit_or_inferred"] not in ALLOWED_EXPLICITNESS:
        raise RecommendationError("Fallback recovery item has an invalid explicit/inferred label")
    if not isinstance(item["title"], str) or not item["title"].strip():
        raise RecommendationError("Fallback recovery item must include a title")
    if not _is_http_url(item["url"]):
        raise RecommendationError("Fallback recovery item must include a valid URL")
    if not isinstance(item["summary"], str) or not item["summary"].strip() or len(item["summary"]) > MAX_SUMMARY_CHARS:
        raise RecommendationError("Fallback recovery item must include a concise summary")
    return RecoveredFallbackItem(
        item["title"].strip(),
        item["url"].strip(),
        item["evidence_class"],
        item["summary"].strip(),
        item["explicit_or_inferred"],
        float(confidence),
    )


def _parse_source_maintenance_advice(advice: object) -> dict:
    """Validate source-link maintenance advice returned by fallback recovery."""
    if not isinstance(advice, dict) or set(advice) != {"recommendation_type", "recommended_replacement_urls", "reason", "confidence"}:
        raise RecommendationError("Fallback recovery source maintenance advice has an invalid shape")
    if advice["recommendation_type"] not in ALLOWED_SOURCE_MAINTENANCE_ADVICE:
        raise RecommendationError("Fallback recovery source maintenance advice has an invalid recommendation type")
    urls = advice["recommended_replacement_urls"]
    if not isinstance(urls, list) or len(urls) > MAX_REPLACEMENT_URLS or not all(_is_http_url(url) for url in urls):
        raise RecommendationError("Fallback recovery source maintenance advice contains an invalid replacement URL")
    confidence = advice["confidence"]
    if not isinstance(confidence, (float, int)) or not 0 <= confidence <= 1:
        raise RecommendationError("Fallback recovery source maintenance advice has an invalid confidence")
    if not isinstance(advice["reason"], str) or not advice["reason"].strip():
        raise RecommendationError("Fallback recovery source maintenance advice must include a reason")
    return {
        "recommendation_type": advice["recommendation_type"],
        "recommended_replacement_urls": tuple(url.strip() for url in urls),
        "reason": advice["reason"].strip(),
        "confidence": float(confidence),
        "requires_officer_approval": True,
        "application_note": "Review and apply manually through Source Configuration; this advice does not update the catalogue automatically.",
    }


def _is_http_url(value: object) -> bool:
    """Return whether a value is an HTTP(S) URL."""
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
