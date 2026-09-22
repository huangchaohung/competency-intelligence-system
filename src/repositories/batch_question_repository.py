"""SQLite persistence for batch question / answer interactions."""
from __future__ import annotations

import sqlite3
from datetime import datetime


class BatchQuestionRepository:
    """Store follow-up questions attached to a recommendation batch."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, recommendation_batch_id: int, question: str, answer: str, context_snapshot: str, asked_at: datetime) -> int:
        """Persist one answered batch question."""
        cursor = self._connection.execute(
            "INSERT INTO batch_questions(recommendation_batch_id,question,answer,context_snapshot,asked_at) VALUES(?,?,?,?,?)",
            (recommendation_batch_id, question, answer, context_snapshot, asked_at.isoformat()),
        )
        self._connection.commit()
        return int(cursor.lastrowid)

    def list_by_batch(self, recommendation_batch_id: int) -> list[sqlite3.Row]:
        """Return saved questions for one recommendation batch, newest first."""
        rows = self._connection.execute(
            "SELECT * FROM batch_questions WHERE recommendation_batch_id=? ORDER BY asked_at DESC, id DESC",
            (recommendation_batch_id,),
        ).fetchall()
        return list(rows)
