"""Governed one-shot AI recommendations for replacing weak source URLs."""
from __future__ import annotations

import json
import os

from openai import OpenAI, OpenAIError

from src.core.exceptions import RecommendationError
from src.services.operational_logger import NullOperationalLogger, OperationalLogger
from src.services.source_url_recommendation import parse_replacement_url_response


SOURCE_URL_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "organisation": {"type": "string"},
                    "source_name": {"type": "string"},
                    "current_url": {"type": "string"},
                    "recommendations": {"type": "array", "items": {"type": "object", "properties": {"url": {"type": "string"}, "reason": {"type": "string"}}, "required": ["url", "reason"], "additionalProperties": False}},
                },
                "required": ["organisation", "source_name", "current_url", "recommendations"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["recommendations"],
    "additionalProperties": False,
}


class OpenAISourceURLRecommender:
    """Make one explicit, fixed-prompt URL recommendation request per batch."""

    def __init__(self, model: str | None = None, operational_logger: OperationalLogger | NullOperationalLogger | None = None) -> None:
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-5.6-terra")
        self._logger = operational_logger or NullOperationalLogger()

    def recommend(self, sources: list[dict]) -> dict:
        if not sources:
            raise RecommendationError("No unhealthy sources were supplied")
        if not os.getenv("OPENAI_API_KEY"):
            raise RecommendationError("OPENAI_API_KEY is not configured")
        prompt = self._build_prompt(sources)
        self._logger.event("llm_source_url_recommendation_request", {"model": self._model, "source_count": len(sources), "prompt": prompt})
        try:
            response = OpenAI().responses.create(model=self._model, input=prompt, text={"format": {"type": "json_schema", "name": "source_url_recommendations", "schema": SOURCE_URL_RESPONSE_SCHEMA, "strict": True}})
        except OpenAIError as error:
            self._logger.event("llm_source_url_recommendation_error", {"model": self._model, "error": str(error)})
            raise RecommendationError(f"OpenAI source URL recommendation failed: {error}") from error
        if not response.output_text:
            raise RecommendationError("OpenAI returned no source URL recommendations")
        self._logger.event("llm_source_url_recommendation_response", {"model": self._model, "raw_response": response.output_text, "usage": self._serialise_usage(response)})
        try:
            payload = json.loads(response.output_text)
            if not isinstance(payload, dict) or not isinstance(payload.get("recommendations"), list):
                raise RecommendationError("Source URL recommendation response has an invalid shape")
            validated = []
            for item in payload["recommendations"]:
                if not isinstance(item, dict):
                    raise RecommendationError("Source URL recommendation item is invalid")
                matching = next((source for source in sources if source.get("Organisation") == item.get("organisation") and source.get("Source") == item.get("source_name")), None)
                if matching is None:
                    raise RecommendationError("Source URL recommendation changed or invented a source organisation")
                if item.get("current_url") != matching.get("Current URL"):
                    raise RecommendationError("Source URL recommendation changed the current URL provenance")
                checked = parse_replacement_url_response(json.dumps({"organisation": item["organisation"], "recommendations": item.get("recommendations", [])}), item["organisation"])
                validated.append({**item, "recommendations": checked["recommendations"]})
            return {"recommendations": validated}
        except RecommendationError:
            raise
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            raise RecommendationError("Source URL recommendation response was not valid JSON") from error

    @staticmethod
    def _serialise_usage(response) -> dict:
        """Extract SDK token usage without assuming one SDK response shape."""
        usage = getattr(response, "usage", None)
        if usage is None:
            return {}
        if hasattr(usage, "model_dump"):
            return usage.model_dump()
        if hasattr(usage, "__dict__"):
            return dict(usage.__dict__)
        return {}

    @staticmethod
    def _build_prompt(sources: list[dict]) -> str:
        return "You are recommending replacement URLs only for the exact organisations supplied. Do not change organisations. Return official public HTTPS STE pages only. Do not invent URLs. The officer must review suggestions manually and the application will not update its catalogue automatically. Return one recommendation object per supplied source.\n\nFLAGGED SOURCES:\n" + json.dumps(sources, ensure_ascii=False)
