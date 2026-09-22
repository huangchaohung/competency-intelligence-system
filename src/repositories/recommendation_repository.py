"""SQLite persistence for recommendation batches and recommendations."""
import json
import sqlite3
from datetime import datetime
from src.models.domain import Recommendation, RecommendationBatch


class RecommendationRepository:
    """Persist AI output without making AI or workflow decisions."""
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def _has_column(self, table_name: str, column_name: str) -> bool:
        return any(row[1] == column_name for row in self._connection.execute(f"PRAGMA table_info({table_name})"))

    def create_batch(self, framework_version_id: int, created_at: datetime, scan_run_id: int | None = None, framework_snapshot: dict | None = None) -> RecommendationBatch:
        """Create a batch for one recommendation run."""
        cursor = self._connection.execute(
            "INSERT INTO recommendation_batches(framework_version_id,scan_run_id,framework_snapshot,created_at) VALUES(?,?,?,?)",
            (framework_version_id, scan_run_id, json.dumps(framework_snapshot or {}), created_at.isoformat()),
        )
        self._connection.commit()
        return RecommendationBatch(cursor.lastrowid, framework_version_id, scan_run_id, created_at, json.dumps(framework_snapshot or {}))

    def add(self, recommendation: Recommendation) -> Recommendation:
        """Store one validated recommendation."""
        cursor = self._connection.execute("INSERT INTO recommendations(batch_id,recommendation_type,confidence,reasoning,sub_functional_area,competency,kind_of_changes_suggested,reasons_for_suggesting_the_changes,supporting_evidence_ids,supporting_urls,supporting_organisations) VALUES(?,?,?,?,?,?,?,?,?,?,?)", (recommendation.batch_id, recommendation.recommendation_type, recommendation.confidence, recommendation.reasoning, recommendation.sub_functional_area, recommendation.competency, recommendation.kind_of_changes_suggested, recommendation.reasons_for_suggesting_the_changes, json.dumps(recommendation.supporting_evidence_ids), json.dumps(recommendation.supporting_urls), json.dumps(recommendation.supporting_organisations)))
        self._connection.commit()
        return Recommendation(cursor.lastrowid, recommendation.batch_id, recommendation.recommendation_type, recommendation.confidence, recommendation.reasoning, recommendation.sub_functional_area, recommendation.competency, recommendation.kind_of_changes_suggested, recommendation.reasons_for_suggesting_the_changes, recommendation.supporting_evidence_ids, recommendation.supporting_urls, recommendation.supporting_organisations)

    def list_all(self) -> list[Recommendation]:
        """Return recommendations newest first."""
        rows = self._connection.execute("SELECT r.* FROM recommendations r JOIN recommendation_batches b ON b.id=r.batch_id ORDER BY b.created_at DESC, r.id DESC").fetchall()
        return [self._to_recommendation(row) for row in rows]

    def list_batches(self) -> list[sqlite3.Row]:
        """Return recommendation batches newest first with recommendation counts."""
        snapshot_select = ", b.framework_snapshot" if self._has_column("recommendation_batches", "framework_snapshot") else ""
        snapshot_group = ", b.framework_snapshot" if self._has_column("recommendation_batches", "framework_snapshot") else ""
        return self._connection.execute(
            f"SELECT b.id, b.framework_version_id{snapshot_select}, b.created_at, COUNT(r.id) AS recommendation_count "
            f"FROM recommendation_batches b LEFT JOIN recommendations r ON r.batch_id=b.id "
            f"GROUP BY b.id, b.framework_version_id{snapshot_group}, b.created_at ORDER BY b.created_at DESC, b.id DESC"
        ).fetchall()

    def list_by_batch(self, batch_id: int) -> list[Recommendation]:
        """Return recommendations belonging to one batch."""
        rows = self._connection.execute("SELECT * FROM recommendations WHERE batch_id=? ORDER BY id DESC", (batch_id,)).fetchall()
        return [self._to_recommendation(row) for row in rows]

    def get_batch_for_scan_run(self, scan_run_id: int) -> sqlite3.Row | None:
        """Return the newest recommendation batch tied to one scan run, if any."""
        snapshot_select = ", b.framework_snapshot" if self._has_column("recommendation_batches", "framework_snapshot") else ""
        snapshot_group = ", b.framework_snapshot" if self._has_column("recommendation_batches", "framework_snapshot") else ""
        return self._connection.execute(
            f"SELECT b.id, b.framework_version_id, b.scan_run_id{snapshot_select}, b.created_at, COUNT(r.id) AS recommendation_count "
            f"FROM recommendation_batches b LEFT JOIN recommendations r ON r.batch_id=b.id WHERE b.scan_run_id=? "
            f"GROUP BY b.id, b.framework_version_id, b.scan_run_id{snapshot_group}, b.created_at ORDER BY b.created_at DESC, b.id DESC LIMIT 1",
            (scan_run_id,),
        ).fetchone()

    def get(self, recommendation_id: int) -> Recommendation | None:
        """Return one recommendation by identity, if it exists."""
        row = self._connection.execute("SELECT * FROM recommendations WHERE id=?", (recommendation_id,)).fetchone()
        return self._to_recommendation(row) if row else None

    @staticmethod
    def _to_recommendation(row: sqlite3.Row) -> Recommendation:
        return Recommendation(row["id"], row["batch_id"], row["recommendation_type"], row["confidence"], row["reasoning"], row["sub_functional_area"] if "sub_functional_area" in row.keys() else "", row["competency"] if "competency" in row.keys() else "", row["kind_of_changes_suggested"] if "kind_of_changes_suggested" in row.keys() else "", row["reasons_for_suggesting_the_changes"] if "reasons_for_suggesting_the_changes" in row.keys() else "", tuple(json.loads(row["supporting_evidence_ids"])), tuple(json.loads(row["supporting_urls"])), tuple(json.loads(row["supporting_organisations"])))
