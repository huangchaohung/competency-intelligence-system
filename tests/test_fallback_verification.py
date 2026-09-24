"""Tests for deterministic fallback URL verification."""
from __future__ import annotations

from src.core.exceptions import ScanError
from src.models.domain import FallbackRecovery
from src.scanner.web_page_scanner import DownloadedPage
from src.services.fallback_verification import ACCESS_BLOCKED, INVALID_URL, MIN_VERIFICATION_WORDS, NEEDS_MANUAL_REVIEW, VERIFIED_BY_URL, FallbackURLVerifier, verification_rows
from src.services.fallback_verification_workflow import verify_recovery_record
import json
from datetime import datetime


class _FakeScanner:
    def __init__(self, pages=None, errors=None) -> None:
        self.pages = pages or {}
        self.errors = errors or {}

    def fetch_url(self, url: str, source_name: str) -> DownloadedPage:
        if url in self.errors:
            raise ScanError(self.errors[url])
        return DownloadedPage(url, self.pages[url])


def test_fallback_verifier_marks_reachable_matching_url_as_verified() -> None:
    """A reachable URL with matching title/summary terms can be flagged as verified."""
    assert MIN_VERIFICATION_WORDS == 25
    scanner = _FakeScanner(
        pages={
            "https://example.com/course": "<html><body>AI engineering assurance and trustworthy systems capability training with enough readable text for verification and audit review by officers. This page describes professional learning outcomes, applied methods, governance considerations, implementation practice, evaluation approaches, and capability development for science technology and engineering teams working with trusted systems.</body></html>"
        }
    )
    item = {"title": "AI Engineering Assurance", "url": "https://example.com/course", "summary": "Trustworthy systems capability training"}

    result = FallbackURLVerifier(scanner).verify_item(item)

    assert result.status == VERIFIED_BY_URL
    assert "engineering" in result.matched_terms


def test_fallback_verifier_flags_blocked_or_timeout_urls() -> None:
    """Access failures should be visible rather than treated as verified."""
    scanner = _FakeScanner(errors={"https://example.com/blocked": "403 Client Error: Forbidden"})

    result = FallbackURLVerifier(scanner).verify_item({"title": "Blocked", "url": "https://example.com/blocked"})

    assert result.status == ACCESS_BLOCKED


def test_fallback_verifier_rejects_non_https_urls() -> None:
    """Recovered fallback URLs must stay auditable through HTTPS links."""
    result = FallbackURLVerifier(_FakeScanner()).verify_item({"title": "Bad", "url": "http://example.com"})

    assert result.status == INVALID_URL


def test_fallback_verifier_flags_reachable_but_unmatched_urls_for_review() -> None:
    """Reachable pages that do not match the recovered claim still need human review."""
    scanner = _FakeScanner(
        pages={
            "https://example.com/other": "<html><body>Completely unrelated accessible public material with enough words to avoid the thin page threshold but no recovered claim vocabulary for the item.</body></html>"
        }
    )

    result = FallbackURLVerifier(scanner).verify_item({"title": "Quantum Photonics Certification", "url": "https://example.com/other", "summary": "Optical sensing"})

    assert result.status == NEEDS_MANUAL_REVIEW


def test_verification_rows_are_officer_readable() -> None:
    """Verification results can be displayed or exported directly."""
    scanner = _FakeScanner(
        pages={
            "https://example.com/course": "<html><body>AI engineering assurance and trustworthy systems capability training with enough readable text for verification and audit review by officers. This page describes professional learning outcomes, applied methods, governance considerations, implementation practice, evaluation approaches, and capability development for science technology and engineering teams working with trusted systems.</body></html>"
        }
    )
    results = FallbackURLVerifier(scanner).verify_items([{"title": "AI Engineering Assurance", "url": "https://example.com/course"}])

    rows = verification_rows(results)

    assert rows[0]["Verification"] == VERIFIED_BY_URL
    assert rows[0]["Matched terms"] != "None"


def test_verify_recovery_record_persists_item_verification_metadata() -> None:
    """Officer-triggered verification annotates and persists the saved recovery JSON."""
    scanner = _FakeScanner(
        pages={
            "https://example.com/course": "<html><body>AI engineering assurance and trustworthy systems capability training with enough readable text for verification and audit review by officers. This page describes professional learning outcomes, applied methods, governance considerations, implementation practice, evaluation approaches, and capability development for science technology and engineering teams working with trusted systems.</body></html>"
        }
    )
    recovery = FallbackRecovery(
        9,
        7,
        "Org A Catalogue",
        "Org A",
        "https://example.com/catalogue",
        "COMPLETED",
        1,
        json.dumps({"recovered_items": [{"title": "AI Engineering Assurance", "url": "https://example.com/course", "summary": "Trustworthy systems capability training"}]}),
        datetime.now(),
    )

    class _Repo:
        raw_result = ""

        def update_raw_result(self, recovery_id: int, raw_result: str) -> None:
            assert recovery_id == 9
            self.raw_result = raw_result

    repository = _Repo()

    payload = verify_recovery_record(recovery, FallbackURLVerifier(scanner), repository)

    assert payload["verification_summary"][VERIFIED_BY_URL] == 1
    assert payload["recovered_items"][0]["verification_status"] == VERIFIED_BY_URL
    assert json.loads(repository.raw_result)["verification_results"][0]["Verification"] == VERIFIED_BY_URL


def test_verify_recovery_record_logs_audit_summary() -> None:
    """Verification outcomes are available to backend maintainers without exposing secrets."""
    scanner = _FakeScanner(
        pages={
            "https://example.com/course": "<html><body>AI engineering assurance and trustworthy systems capability training with enough readable text for verification and audit review by officers. This page describes professional learning outcomes, applied methods, governance considerations, implementation practice, evaluation approaches, and capability development for science technology and engineering teams working with trusted systems.</body></html>"
        }
    )
    recovery = FallbackRecovery(
        10, 8, "Org A Catalogue", "Org A", "https://example.com/catalogue", "COMPLETED", 1,
        json.dumps({"recovered_items": [{"title": "AI Engineering Assurance", "url": "https://example.com/course", "summary": "Trustworthy systems capability training"}]}),
        datetime.now(),
    )

    class _Repo:
        def update_raw_result(self, recovery_id: int, raw_result: str) -> None:
            assert recovery_id == 10

    class _Logger:
        events: list[tuple[str, dict]] = []

        def event(self, name: str, payload: dict) -> None:
            self.events.append((name, payload))

    logger = _Logger()
    verify_recovery_record(recovery, FallbackURLVerifier(scanner), _Repo(), logger)
    assert logger.events[0][0] == "fallback_url_verification_completed"
    assert logger.events[0][1]["items_checked"] == 1
