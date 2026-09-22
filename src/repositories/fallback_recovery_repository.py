"""SQLite persistence for governed LLM fallback recovery runs."""
import sqlite3
from datetime import datetime

from src.models.domain import FallbackRecovery


class FallbackRecoveryRepository:
    """Persist explicit LLM fallback recovery results separately from crawler evidence."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, recovery: FallbackRecovery) -> FallbackRecovery:
        """Store one governed fallback recovery result."""
        cursor = self._connection.execute(
            """
            INSERT INTO fallback_recoveries(scan_run_id,source_name,organisation,source_url,recovery_status,recovered_item_count,raw_result,created_at)
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (
                recovery.scan_run_id,
                recovery.source_name,
                recovery.organisation,
                recovery.source_url,
                recovery.recovery_status,
                recovery.recovered_item_count,
                recovery.raw_result,
                recovery.created_at.isoformat(),
            ),
        )
        self._connection.commit()
        return FallbackRecovery(
            int(cursor.lastrowid),
            recovery.scan_run_id,
            recovery.source_name,
            recovery.organisation,
            recovery.source_url,
            recovery.recovery_status,
            recovery.recovered_item_count,
            recovery.raw_result,
            recovery.created_at,
        )

    def list_for_scan_run(self, scan_run_id: int) -> list[FallbackRecovery]:
        """Return fallback recovery records for one scan run, newest first."""
        rows = self._connection.execute(
            "SELECT * FROM fallback_recoveries WHERE scan_run_id=? ORDER BY created_at DESC, id DESC",
            (scan_run_id,),
        ).fetchall()
        return [self._to_recovery(row) for row in rows]

    def list_recent(self, limit: int = 20) -> list[FallbackRecovery]:
        """Return recent fallback recovery records for IT/officer review."""
        rows = self._connection.execute(
            "SELECT * FROM fallback_recoveries ORDER BY created_at DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._to_recovery(row) for row in rows]

    def update_raw_result(self, recovery_id: int, raw_result: str) -> None:
        """Persist an updated raw JSON result for one fallback recovery record."""
        self._connection.execute(
            "UPDATE fallback_recoveries SET raw_result=? WHERE id=?",
            (raw_result, recovery_id),
        )
        self._connection.commit()

    @staticmethod
    def _to_recovery(row: sqlite3.Row) -> FallbackRecovery:
        """Convert one SQLite row into a domain object."""
        return FallbackRecovery(
            row["id"],
            row["scan_run_id"],
            row["source_name"],
            row["organisation"],
            row["source_url"],
            row["recovery_status"],
            row["recovered_item_count"],
            row["raw_result"],
            datetime.fromisoformat(row["created_at"]),
        )
