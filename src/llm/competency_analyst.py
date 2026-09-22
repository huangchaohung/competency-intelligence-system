"""OpenAI adapter for structured competency analysis."""
import json
import logging
import os
from dataclasses import dataclass
from typing import Protocol
from openai import OpenAI, OpenAIError
from src.core.exceptions import RecommendationError
from src.services.operational_logger import NullOperationalLogger, OperationalLogger

LOGGER = logging.getLogger(__name__)
ALLOWED_TYPES = {"ALREADY_COVERED", "NEW_COMPETENCY", "EXPAND_COMPETENCY", "MERGE_RECOMMENDATION", "DEPRECATION_CANDIDATE", "NEW_SUB_FUNCTIONAL_AREA", "OUTLIER_SIGNAL_DETECTED", "INSUFFICIENT_EVIDENCE"}
MAX_EVIDENCE_ITEMS = 60
MAX_CHARS_PER_EVIDENCE = 1_800
MIN_SUPPORTING_SOURCES_WHEN_AVAILABLE = 4
MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION = 10
MIN_DEPRECATION_SUPPORTING_SOURCES = 4
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "recommendations": {
                "type": "array",
                "maxItems": 20,
            "items": {
                "type": "object",
                "properties": {
                    "recommendation_type": {"type": "string", "enum": sorted(ALLOWED_TYPES)},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "reasoning": {"type": "string"},
                    "sub_functional_area": {"type": "string"},
                    "competency": {"type": "string"},
                    "kind_of_changes_suggested": {"type": "string"},
                    "reasons_for_suggesting_the_changes": {"type": "string"},
                    "supporting_evidence_ids": {"type": "array", "maxItems": MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION, "items": {"type": "integer"}},
                    "supporting_urls": {"type": "array", "maxItems": MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION, "items": {"type": "string"}},
                    "supporting_organisations": {"type": "array", "maxItems": MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION, "items": {"type": "string"}},
                },
                "required": [
                    "recommendation_type",
                    "confidence",
                    "reasoning",
                    "sub_functional_area",
                    "competency",
                    "kind_of_changes_suggested",
                    "reasons_for_suggesting_the_changes",
                    "supporting_evidence_ids",
                    "supporting_urls",
                    "supporting_organisations",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["recommendations"],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class RecommendationDraft:
    """Validated recommendation before it receives a database identity."""
    recommendation_type: str
    confidence: float
    reasoning: str
    sub_functional_area: str
    competency: str
    kind_of_changes_suggested: str
    reasons_for_suggesting_the_changes: str
    supporting_evidence_ids: tuple[int, ...]
    supporting_urls: tuple[str, ...]
    supporting_organisations: tuple[str, ...]


class CompetencyAnalyst(Protocol):
    """Port for generating validated recommendation drafts."""
    def analyse(self, framework: dict, evidence: dict) -> list[RecommendationDraft]:
        """Analyse framework and evidence without modifying application state."""
    def answer_question(self, context: dict, question: str) -> str:
        """Answer a follow-up question using batch-grounded context."""


class OpenAICompetencyAnalyst:
    """Call the Responses API and validate its JSON-only output locally."""
    def __init__(self, model: str | None = None, operational_logger: OperationalLogger | NullOperationalLogger | None = None) -> None:
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-5.6-terra")
        self._operational_logger = operational_logger or NullOperationalLogger()

    def analyse(self, framework: dict, evidence: dict) -> list[RecommendationDraft]:
        """Generate recommendation drafts from approved input data."""
        if not os.getenv("OPENAI_API_KEY"):
            raise RecommendationError("OPENAI_API_KEY is not configured")
        prompt = self._build_prompt(framework, evidence)
        self._operational_logger.event(
            "llm_recommendation_request",
            {
                "model": self._model,
                "endpoint": "responses.create",
                "prompt": prompt,
                "framework_version": framework.get("version"),
                "selected_evidence_count": len(evidence.get("selected_evidence", [])),
                "organised_scan_quality": evidence.get("organised_scan", {}).get("quality_summary", {}),
            },
        )
        try:
            response = OpenAI().responses.create(model=self._model, input=prompt, text={"format": {"type": "json_schema", "name": "competency_recommendations", "schema": RESPONSE_SCHEMA, "strict": True}})
        except OpenAIError as error:
            self._operational_logger.event("llm_recommendation_error", {"model": self._model, "error": str(error)})
            raise RecommendationError(f"OpenAI request failed: {error}") from error
        LOGGER.info("Received recommendation response from model '%s'", self._model)
        if not response.output_text:
            self._operational_logger.event("llm_recommendation_empty_response", {"model": self._model, "usage": self._serialise_usage(response)})
            raise RecommendationError("OpenAI returned no recommendation content")
        self._operational_logger.event(
            "llm_recommendation_response",
            {
                "model": self._model,
                "raw_response": response.output_text,
                "usage": self._serialise_usage(response),
            },
        )
        try:
            drafts = self._parse_response(response.output_text)
        except RecommendationError as error:
            self._operational_logger.event("llm_recommendation_parse_error", {"model": self._model, "error": str(error), "raw_response": response.output_text})
            raise
        self._operational_logger.event(
            "llm_recommendation_parsed",
            {
                "model": self._model,
                "recommendation_count": len(drafts),
                "recommendation_types": [draft.recommendation_type for draft in drafts],
            },
        )
        return drafts

    def answer_question(self, context: dict, question: str) -> str:
        """Answer a batch-grounded follow-up question from the current scan context."""
        if not os.getenv("OPENAI_API_KEY"):
            raise RecommendationError("OPENAI_API_KEY is not configured")
        prompt = (
            "You are helping a government officer review the current STE competency scan batch. "
            "Use only the provided batch context. Be careful, concise, and evidence-grounded. "
            "Use recommendation_summary and each recommendation's support_profile to understand support breadth before reading the longer evidence text. "
            "Use organised_scan_quality to explain the mix of the included cited evidence, not the entire scan. "
            "Only recommendation-cited evidence is included. Missing or uncited evidence is unavailable, not proof of absence. "
            "When diagnostic_scope specifies summary counts only, do not infer individual source failures or maintenance actions from those counts. Detailed source diagnostics are not supplied. "
            "Use support_coverage when the question asks whether recommendations are broadly supported or concentrated in a few organisations/source families. "
            "Use source_health and source_health_counts when the question asks about scan reliability, weak sources, crawler quality, or whether a source may need tuning or LLM fallback. "
            "Use llm_fallback_candidates, llm_fallback_readiness_counts, and llm_fallback_request_preview when the question asks which sources are eligible for fallback recovery or what a future fallback pass would try to recover. "
            "Use llm_fallback_recoveries when the question asks whether a fallback recovery was already run, what it recovered, or how AI-recovered source interpretation differs from deterministic crawler evidence. "
            "Use recent_question_history only for same-batch conversational continuity; it is not source evidence and must not replace citations to original evidence IDs or URLs. "
            "Evidence items contain article_preview fields, not necessarily full article text; if article_preview_truncated is true, avoid over-claiming details beyond the preview. "
            "If the question asks for more evidence, cite the relevant evidence items from the batch context. "
            "If the question challenges a recommendation, compare it back to the batch evidence and the framework snapshot. "
            "If the question is about outlier signals, explain why those signals may matter without overstating certainty. "
            "Do not invent sources or framework content. "
            "Return a plain-text answer with short supporting bullets when useful."
            f"\n\nBATCH CONTEXT:\n{json.dumps(context, ensure_ascii=False)}\n\nQUESTION:\n{question}"
        )
        # Conservative byte ceiling, not a model-specific token estimate.
        # Reject unexpected oversized snapshots before any paid API request.
        if len(prompt.encode('utf-8')) > 300_000:
            raise RecommendationError("Ask AI context is still too large after selecting cited evidence. Please reduce the framework/context size; no request was sent.")
        self._operational_logger.event(
            "llm_batch_question_request",
            {
                "model": self._model,
                "endpoint": "responses.create",
                "question": question,
                "prompt": prompt,
                "batch_id": context.get("recommendation_batch", {}).get("id") if isinstance(context.get("recommendation_batch"), dict) else None,
            },
        )
        try:
            response = OpenAI().responses.create(model=self._model, input=prompt, max_output_tokens=4096)
        except OpenAIError as error:
            self._operational_logger.event("llm_batch_question_error", {"model": self._model, "question": question, "error": str(error)})
            raise RecommendationError(f"OpenAI request failed: {error}") from error
        if not response.output_text:
            self._operational_logger.event("llm_batch_question_empty_response", {"model": self._model, "question": question, "usage": self._serialise_usage(response)})
            raise RecommendationError("OpenAI returned no answer content")
        answer = response.output_text.strip()
        self._operational_logger.event(
            "llm_batch_question_response",
            {
                "model": self._model,
                "question": question,
                "raw_response": response.output_text,
                "displayed_answer": answer,
                "usage": self._serialise_usage(response),
            },
        )
        return answer

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

    @staticmethod
    def _build_prompt(framework: dict, evidence: dict) -> str:
        instructions = (
            "You are a Competency Framework Analyst helping a government officer identify future STE capability needs. "
            "Analyse the full supplied framework, including every sub-functional area, cap area, competency, and definition, together with the full supplied evidence corpus. "
            "The evidence input has two layers: ORGANISED_SCAN summarises the full batch by organisation and evidence class, while SELECTED_EVIDENCE gives citation-ready item text for detailed support. "
            "Treat ORGANISED_SCAN as the full-batch coverage map. Read across all organisations before deciding, and do not anchor on the first few selected evidence items. "
            "Use ORGANISED_SCAN.quality_summary to judge whether the batch is structured-heavy, mixed, or signal-heavy before deciding how strongly to rely on trend/news evidence. "
            "Use SELECTED_EVIDENCE and ORGANISED_SCAN item IDs for citations. The supporting_evidence_ids are the authoritative citation keys; supporting_urls and supporting_organisations must correspond to those same evidence IDs. "
            "Each evidence item may include a source_family, source_type, source_role, country, evidence_type, and explicit_or_inferred label. Use those signals to judge reliability, intent, and whether the item is a primary source or a supporting outlier signal. "
            "Source family should matter: professional bodies, higher learning, and government agencies are stronger signals than generic news, commentary, or soft marketing material. "
            "Source types such as FRAMEWORK, CATALOGUE, INDEX, and TREND are clues about what the source is best used for, but they do not replace your own reasoning. "
            "Prefer evidence that is explicit, directly relevant, and corroborated by multiple sources, multiple source families, or multiple organisations whenever possible. "
            "For weaker or noisier evidence types, use them mainly as support, validation, or outlier hints rather than as the sole basis for a recommendation. "
            "Your job is to find gaps, adjacencies, and emerging capabilities that are NOT already in the framework. "
            "Prioritise recommendations in this order: "
            "1) genuinely NEW_SUB_FUNCTIONAL_AREA proposals for STE capability areas not represented in the current framework; "
            "2) NEW_COMPETENCY proposals within an existing sub-functional area; "
            "3) OUTLIER_SIGNAL_DETECTED items where credible organisations show repeated or unusual STE course/capability combinations that are worth monitoring but not yet broad enough for immediate framework change; "
            "4) EXPAND_COMPETENCY proposals where the current competency exists but is too narrow; "
            "5) DEPRECATION_CANDIDATE only when there is strong positive evidence that an existing competency is obsolete, superseded, explicitly discontinued, or replaced; "
            "6) MERGE_RECOMMENDATION only when the framework clearly needs consolidation. "
            "Do not spend most of the output re-stating already covered competencies. "
            "Aim for 12 to 20 visible actionable recommendations when the evidence supports them. Diversify across cap areas and sub-functional areas; avoid clustering more than three recommendations under the same sub-functional area unless the evidence strongly warrants it. "
            "Do not invent evidence or URLs. Every recommendation must be supported by the supplied evidence only, and every recommendation must include at least one supporting_evidence_id. "
            "Where the evidence is available, cite 4 to 10 supporting_evidence_ids per recommendation so officers can inspect legitimacy across several sources. "
            "Use fewer than 4 only when there are genuinely fewer than 4 relevant supporting sources for that specific recommendation. Do not pad with weak or irrelevant evidence. "
            "Never cite more than 10 supporting_evidence_ids for one recommendation. The supporting_evidence_ids should point to as many relevant evidence items as genuinely justify the recommendation. "
            "For DEPRECATION_CANDIDATE, do not rely on absence of evidence. Only recommend deprecation when at least 4 supplied evidence items positively show that the competency is obsolete, superseded, explicitly discontinued, replaced by a newer standard/practice, or repeatedly removed from authoritative competency/course guidance. "
            "Phrase DEPRECATION_CANDIDATE as a human-review deprecation candidate, never as an automatic deletion instruction. "
            "Prefer multiple supporting sources, multiple organisations, and multiple source families whenever the claim is cross-sourced. "
            "When evidence is sparse for a claim, say so internally and lower confidence rather than padding the output. "
            "Push beyond the exact existing competency list: look for adjacent STE themes, missing sub-functional areas, emerging methods, enabling technologies, regulatory or standards needs, and capability shifts implied by the evidence. "
            "If evidence is weak or repetitive, do not force a recommendation. "
            "Treat news and publication material as supporting outlier signals only unless the article itself is a clear standards, guidance, catalogue, or research source. "
            "Use OUTLIER_SIGNAL_DETECTED for credible but still-emerging STE signals, such as a new combination of courses, programmes, standards topics, or research capability appearing in a reputable organisation but not yet broadly across the source pool. "
            "For OUTLIER_SIGNAL_DETECTED, describe what officers should monitor next and avoid wording it as an immediate framework update. "
            "When a source is a catalogue, training hub, standards page, competency framework, or research hub, treat that as structurally stronger than a generic article. "
            "First organise the source material conceptually into: explicit competencies/standards, courses/programmes/resources, research reports/capability statements, and supporting trend/outlier signals. "
            "If a source does not present a clean competency/course list, infer the likely STE competency or course concepts from the source text, tied back to that organisation. "
            "Then compare those organised source concepts against the current framework. "
            "Return up to 20 recommendations. Each recommendation must conform exactly to the supplied JSON schema and must include: recommendation_type, confidence (0 through 1), sub_functional_area, competency, kind_of_changes_suggested, reasons_for_suggesting_the_changes, reasoning, supporting_evidence_ids, supporting_urls, and supporting_organisations. "
            "Use recommendation_type values only from: ALREADY_COVERED, NEW_COMPETENCY, EXPAND_COMPETENCY, MERGE_RECOMMENDATION, DEPRECATION_CANDIDATE, NEW_SUB_FUNCTIONAL_AREA, OUTLIER_SIGNAL_DETECTED, INSUFFICIENT_EVIDENCE. "
            "Treat ALREADY_COVERED and INSUFFICIENT_EVIDENCE as internal assessment categories when useful, but focus the final output on the strongest actionable gaps. "
            "Each list item must contain only values present in the supplied evidence and framework."
        )
        return f"{instructions}\n\nFRAMEWORK:\n{json.dumps(framework)}\n\nORGANISED_SCAN:\n{json.dumps(evidence.get('organised_scan', {}))}\n\nSELECTED_EVIDENCE:\n{json.dumps(evidence.get('selected_evidence', []))}"

    @staticmethod
    def _parse_response(text: str) -> list[RecommendationDraft]:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as error:
            raise RecommendationError("Model response was not valid JSON") from error
        if not isinstance(payload, dict) or set(payload) != {"recommendations"} or not isinstance(payload["recommendations"], list):
            raise RecommendationError("Model response must contain a recommendations array")
        drafts: list[RecommendationDraft] = []
        for item in payload["recommendations"]:
            if not isinstance(item, dict) or set(item) - {"recommendation_type", "confidence", "sub_functional_area", "competency", "kind_of_changes_suggested", "reasons_for_suggesting_the_changes", "reasoning", "supporting_evidence_ids", "supporting_urls", "supporting_organisations"}:
                raise RecommendationError("Model response has an invalid recommendation shape")
            confidence = item["confidence"]
            if item["recommendation_type"] not in ALLOWED_TYPES or not isinstance(confidence, (float, int)) or not 0 <= confidence <= 1 or not isinstance(item["reasoning"], str) or not item["reasoning"].strip():
                raise RecommendationError("Model response contains invalid recommendation values")
            evidence_ids = item["supporting_evidence_ids"]
            urls = item["supporting_urls"]
            organisations = item["supporting_organisations"]
            if not isinstance(evidence_ids, list) or not isinstance(urls, list) or not isinstance(organisations, list):
                raise RecommendationError("Model response contains invalid support references")
            if len(evidence_ids) > MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION or len(urls) > MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION or len(organisations) > MAX_SUPPORTING_SOURCES_PER_RECOMMENDATION:
                raise RecommendationError("Model response cites too many supporting sources")
            if not all(isinstance(value, int) for value in evidence_ids) or not all(isinstance(value, str) for value in urls + organisations):
                raise RecommendationError("Model response contains invalid support references")
            recommendation_type = _guard_deprecation_type(item["recommendation_type"], evidence_ids)
            reasoning = item["reasoning"].strip()
            reasons_for_change = str(item.get("reasons_for_suggesting_the_changes", "")).strip()
            if recommendation_type != item["recommendation_type"]:
                reasoning = f"{reasoning} Local guardrail: weak deprecation candidate downgraded because it cited fewer than {MIN_DEPRECATION_SUPPORTING_SOURCES} supporting evidence items."
                reasons_for_change = f"{reasons_for_change} Local guardrail: deletion/deprecation requires strong positive evidence and officer review."
            drafts.append(RecommendationDraft(
                recommendation_type,
                float(confidence),
                reasoning,
                str(item.get("sub_functional_area", "")).strip(),
                str(item.get("competency", "")).strip(),
                str(item.get("kind_of_changes_suggested", "")).strip(),
                reasons_for_change,
                tuple(evidence_ids),
                tuple(urls),
                tuple(organisations),
            ))
        return drafts


def _guard_deprecation_type(recommendation_type: str, evidence_ids: list[int]) -> str:
    """Hide weak deprecation suggestions unless they meet the local evidence threshold."""
    if recommendation_type == "DEPRECATION_CANDIDATE" and len(set(evidence_ids)) < MIN_DEPRECATION_SUPPORTING_SOURCES:
        return "INSUFFICIENT_EVIDENCE"
    return recommendation_type
