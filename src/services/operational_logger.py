"""Backend-only structured operational logging for IT troubleshooting."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


SECRET_KEY_PATTERN = re.compile(r"(api[_-]?key|access[_-]?token|refresh[_-]?token|secret|password|credential|authorization)", re.IGNORECASE)
SECRET_VALUE_PATTERN = re.compile(r"(sk-[A-Za-z0-9_\-]{12,}|Bearer\s+[A-Za-z0-9._\-]+)", re.IGNORECASE)


class OperationalLogger:
    """Write timestamped JSONL events for backend engineers.

    The logger is intentionally file-based for the prototype: it avoids schema
    churn while giving IT staff a grep-friendly audit trail. Officer-facing UI
    should not read these files by default.
    """

    def __init__(self, log_dir: Path, filename: str = "operational_audit.jsonl", max_bytes: int = 5_000_000, backup_count: int = 3) -> None:
        self._path = log_dir / filename
        self._max_bytes = max_bytes
        self._backup_count = backup_count
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        """Return the JSONL file path for IT handover documentation."""
        return self._path

    def event(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        """Append one structured event with redacted payload values."""
        record = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "event_type": event_type,
            "payload": self._redact(payload or {}),
        }
        self._rotate_if_needed()
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def _rotate_if_needed(self) -> None:
        """Rotate the active JSONL file before it grows beyond the configured cap."""
        if self._max_bytes <= 0 or self._backup_count <= 0 or not self._path.exists():
            return
        if self._path.stat().st_size < self._max_bytes:
            return
        oldest = self._path.with_name(f"{self._path.name}.{self._backup_count}")
        if oldest.exists():
            oldest.unlink()
        for index in range(self._backup_count - 1, 0, -1):
            current = self._path.with_name(f"{self._path.name}.{index}")
            if current.exists():
                current.replace(self._path.with_name(f"{self._path.name}.{index + 1}"))
        self._path.replace(self._path.with_name(f"{self._path.name}.1"))

    @classmethod
    def _redact(cls, value: Any) -> Any:
        """Return a JSON-safe copy with likely secrets removed."""
        if isinstance(value, dict):
            redacted: dict[str, Any] = {}
            for key, item in value.items():
                if SECRET_KEY_PATTERN.search(str(key)):
                    redacted[str(key)] = "[REDACTED]"
                else:
                    redacted[str(key)] = cls._redact(item)
            return redacted
        if isinstance(value, (list, tuple, set)):
            return [cls._redact(item) for item in value]
        if isinstance(value, str):
            return SECRET_VALUE_PATTERN.sub("[REDACTED]", value)
        return value


class NullOperationalLogger:
    """No-op logger used by tests or lightweight service construction."""

    @property
    def path(self) -> Path | None:
        """Mirror OperationalLogger.path without creating files."""
        return None

    def event(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        """Ignore operational events."""
        return None
