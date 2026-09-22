"""Officer-controlled verification workflow for saved LLM fallback recoveries."""
from __future__ import annotations

from datetime import datetime
import json

from src.services.fallback_verification import FallbackURLVerifier, verification_rows
from src.services.operational_logger import NullOperationalLogger, OperationalLogger


def verify_recovery_record(
    recovery,
    verifier: FallbackURLVerifier,
    repository,
    operational_logger: OperationalLogger | NullOperationalLogger | None = None,
) -> dict:
    """Verify one saved fallback recovery record and persist verification metadata.

    This function performs deterministic URL fetches. Call it only from an
    explicit officer action, never during ordinary page rendering.
    """
    logger = operational_logger or NullOperationalLogger()
    try:
        payload = json.loads(recovery.raw_result or "{}")
    except json.JSONDecodeError:
        payload = {"raw_result": recovery.raw_result, "recovered_items": []}
    recovered_items = list(payload.get("recovered_items", []) or [])
    results = verifier.verify_items(recovered_items, recovery.source_name)
    rows = verification_rows(results)
    for item, result in zip(recovered_items, results):
        item["verification_status"] = result.status
        item["verification_reason"] = result.reason
        item["verification_matched_terms"] = list(result.matched_terms)
        item["verification_checked_at"] = datetime.now().astimezone().isoformat()
    payload["recovered_items"] = recovered_items
    payload["verification_results"] = rows
    payload["verification_checked_at"] = datetime.now().astimezone().isoformat()
    payload["verification_summary"] = _verification_summary(rows)
    if recovery.id is not None:
        repository.update_raw_result(recovery.id, json.dumps(payload))
    logger.event(
        "fallback_url_verification_completed",
        {
            "recovery_id": recovery.id,
            "scan_run_id": recovery.scan_run_id,
            "source": recovery.source_name,
            "organisation": recovery.organisation,
            "items_checked": len(rows),
            "verification_summary": payload["verification_summary"],
        },
    )
    return payload


def _verification_summary(rows: list[dict[str, str]]) -> dict[str, int]:
    """Count verification labels for compact display/export."""
    summary: dict[str, int] = {}
    for row in rows:
        label = row.get("Verification", "Unknown")
        summary[label] = summary.get(label, 0) + 1
    return summary
