"""SQLite persistence for scan runs and evidence."""
import sqlite3
from datetime import datetime
import json
from src.models.domain import Evidence, ScanRun, ScanStatus, SourceHealth


class ScanRepository:
    """Persist scan status and extracted evidence."""
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create_run(self, started_at: datetime, sources_snapshot: list[dict] | None = None) -> ScanRun:
        """Create a running scan record."""
        cursor = self._connection.execute(
            "INSERT INTO scan_runs(started_at,status,sources_snapshot) VALUES(?,?,?)",
            (started_at.isoformat(), ScanStatus.RUNNING, json.dumps(sources_snapshot or [])),
        )
        self._connection.commit()
        return ScanRun(cursor.lastrowid, started_at, None, ScanStatus.RUNNING, None, tuple(sources_snapshot or ()))

    def complete_run(self, run: ScanRun, status: ScanStatus, error_summary: str | None) -> ScanRun:
        """Finish a scan record."""
        completed_at = datetime.now().astimezone()
        self._connection.execute("UPDATE scan_runs SET completed_at=?,status=?,error_summary=? WHERE id=?", (completed_at.isoformat(), status, error_summary, run.id))
        completed = ScanRun(run.id, run.started_at, completed_at, status, error_summary, run.sources_snapshot)
        from src.services.source_health_service import source_health_rows
        evidence = self.list_evidence_for_run(run.id or 0)
        fields = ('Status', 'Evidence items', 'Source', 'Organisation', 'Source URL', 'Reason')
        health = [{key: row[key] for key in fields} for row in source_health_rows(completed, evidence)]
        self._connection.execute(
            "INSERT OR IGNORE INTO scan_summaries(scan_run_id,evidence_count,health_json) VALUES(?,?,?)",
            (run.id, len(evidence), json.dumps(health)))
        self._connection.commit()
        return ScanRun(run.id, run.started_at, completed_at, status, error_summary, run.sources_snapshot)

    def get_summary(self, scan_run_id: int) -> dict | None:
        """Return original completion counts, never reconstructed from pruned text."""
        row = self._connection.execute('SELECT evidence_count,health_json FROM scan_summaries WHERE scan_run_id=?', (scan_run_id,)).fetchone()
        return {'evidence_count': row['evidence_count'], 'health': json.loads(row['health_json'])} if row else None

    def clear_evidence(self) -> int:
        """Delete all stored evidence records."""
        deleted = self._connection.execute("DELETE FROM evidence").rowcount
        self._connection.commit()
        return deleted

    def prune_evidence_to_recent_runs(self, keep_runs: int = 5) -> int:
        """Delete evidence outside the most recent scan runs while keeping scan history."""
        if keep_runs < 1:
            raise ValueError("keep_runs must be at least 1")
        deleted = self._connection.execute(
            """
            DELETE FROM evidence
            WHERE scan_run_id NOT IN (
                SELECT id
                FROM scan_runs
                ORDER BY started_at DESC, id DESC
                LIMIT ?
            )
            """,
            (keep_runs,),
        ).rowcount
        self._connection.commit()
        return deleted

    def add_evidence(self, evidence: Evidence) -> Evidence:
        """Store clean evidence."""
        cursor = self._connection.execute("INSERT INTO evidence(scan_run_id,source_id,evidence_type,title,publication_date,organisation,url,article_text,extracted_at,explicit_or_inferred) VALUES(?,?,?,?,?,?,?,?,?,?)", (evidence.scan_run_id,evidence.source_id,evidence.evidence_type,evidence.title,evidence.publication_date,evidence.organisation,evidence.url,evidence.article_text,evidence.extracted_at.isoformat(),evidence.explicit_or_inferred))
        self._connection.commit()
        return Evidence(cursor.lastrowid, evidence.scan_run_id, evidence.source_id, evidence.evidence_type, evidence.title, evidence.publication_date, evidence.organisation, evidence.url, evidence.article_text, evidence.extracted_at, evidence.explicit_or_inferred)

    def list_evidence(self) -> list[Evidence]:
        """Return stored evidence newest first."""
        rows = self._connection.execute("SELECT * FROM evidence ORDER BY extracted_at DESC").fetchall()
        return [Evidence(r["id"],r["scan_run_id"],r["source_id"],r["evidence_type"] if "evidence_type" in r.keys() else "Unknown",r["title"],r["publication_date"],r["organisation"],r["url"],r["article_text"],datetime.fromisoformat(r["extracted_at"]),r["explicit_or_inferred"] if "explicit_or_inferred" in r.keys() else "INFERRED") for r in rows]

    def list_evidence_for_run(self, scan_run_id: int) -> list[Evidence]:
        """Return stored evidence for one run, newest first within the run."""
        rows = self._connection.execute("SELECT * FROM evidence WHERE scan_run_id=? ORDER BY extracted_at DESC", (scan_run_id,)).fetchall()
        return [Evidence(r["id"],r["scan_run_id"],r["source_id"],r["evidence_type"] if "evidence_type" in r.keys() else "Unknown",r["title"],r["publication_date"],r["organisation"],r["url"],r["article_text"],datetime.fromisoformat(r["extracted_at"]),r["explicit_or_inferred"] if "explicit_or_inferred" in r.keys() else "INFERRED") for r in rows]

    def list_evidence_for_source(self, source_id: int) -> list[Evidence]:
        """Return stored evidence for one source, newest first."""
        rows = self._connection.execute("SELECT * FROM evidence WHERE source_id=? ORDER BY extracted_at DESC", (source_id,)).fetchall()
        return [Evidence(r["id"],r["scan_run_id"],r["source_id"],r["evidence_type"] if "evidence_type" in r.keys() else "Unknown",r["title"],r["publication_date"],r["organisation"],r["url"],r["article_text"],datetime.fromisoformat(r["extracted_at"]),r["explicit_or_inferred"] if "explicit_or_inferred" in r.keys() else "INFERRED") for r in rows]

    def list_runs(self, limit: int = 10) -> list[ScanRun]:
        """Return recent scan runs, newest first."""
        rows = self._connection.execute("SELECT * FROM scan_runs ORDER BY started_at DESC LIMIT ?", (limit,)).fetchall()
        return [ScanRun(row["id"], datetime.fromisoformat(row["started_at"]), datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None, ScanStatus(row["status"]), row["error_summary"], tuple(json.loads(row["sources_snapshot"])) if "sources_snapshot" in row.keys() and row["sources_snapshot"] else ()) for row in rows]

    def evidence_exists(self, url: str) -> bool:
        """Return whether evidence for this canonical URL is already stored."""
        return self._connection.execute("SELECT 1 FROM evidence WHERE url=? LIMIT 1", (url,)).fetchone() is not None

    def count_evidence(self) -> int:
        """Return the total number of stored evidence records."""
        return int(self._connection.execute("SELECT COUNT(*) FROM evidence").fetchone()[0])

    def list_source_health(self) -> dict[int, SourceHealth]:
        """Return evidence volume and recency for each configured source."""
        rows = self._connection.execute("SELECT source_id, COUNT(*) AS evidence_count, MAX(extracted_at) AS last_evidence_at FROM evidence GROUP BY source_id").fetchall()
        return {row["source_id"]: SourceHealth(row["source_id"], row["evidence_count"], datetime.fromisoformat(row["last_evidence_at"]) if row["last_evidence_at"] else None) for row in rows}
