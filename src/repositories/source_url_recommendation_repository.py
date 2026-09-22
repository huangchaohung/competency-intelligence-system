"""Persistence for one-time per-batch source URL recommendation requests."""
import json
import sqlite3
from datetime import datetime


class SourceURLRecommendationRepository:
    """Store one governed URL-remediation response per recommendation batch."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get_for_batch(self, recommendation_batch_id: int):
        return self._connection.execute(
            "SELECT * FROM source_url_recommendations WHERE recommendation_batch_id=? ORDER BY id DESC LIMIT 1",
            (recommendation_batch_id,),
        ).fetchone()

    def add(self, scan_run_id: int | None, recommendation_batch_id: int, status: str, source_snapshot: list[dict], raw_result: dict) -> sqlite3.Row:
        if self.get_for_batch(recommendation_batch_id) is not None:
            raise ValueError("A source URL recommendation already exists for this batch")
        cursor = self._connection.execute(
            "INSERT INTO source_url_recommendations(scan_run_id,recommendation_batch_id,status,source_snapshot,raw_result,created_at) VALUES(?,?,?,?,?,?)",
            (scan_run_id, recommendation_batch_id, status, json.dumps(source_snapshot), json.dumps(raw_result), datetime.now().astimezone().isoformat()),
        )
        self._connection.commit()
        return self._connection.execute("SELECT * FROM source_url_recommendations WHERE id=?", (cursor.lastrowid,)).fetchone()
