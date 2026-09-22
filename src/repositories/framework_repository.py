"""SQLite persistence for immutable framework versions."""
import sqlite3
from datetime import datetime
from src.models.domain import Competency, FrameworkVersion, SubFunctionalArea


class FrameworkRepository:
    """Persist framework entities without import or presentation rules."""
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create_version(self, version: str, created_at: datetime) -> FrameworkVersion:
        """Create and activate a new framework version."""
        self._connection.execute("UPDATE framework_versions SET is_current=0")
        cursor = self._connection.execute("INSERT INTO framework_versions(version,created_at,is_current) VALUES(?,?,1)", (version, created_at.isoformat()))
        return FrameworkVersion(cursor.lastrowid, version, created_at, True)

    def add_area(self, area: SubFunctionalArea) -> SubFunctionalArea:
        """Add a sub-functional area to a framework version."""
        cursor = self._connection.execute("INSERT INTO sub_functional_areas(framework_version_id,cap_area,name,description) VALUES(?,?,?,?)", (area.framework_version_id, area.cap_area, area.name, area.description))
        return SubFunctionalArea(cursor.lastrowid, area.framework_version_id, area.cap_area, area.name, area.description)

    def add_competency(self, competency: Competency) -> Competency:
        """Add a competency to an area."""
        cursor = self._connection.execute("INSERT INTO competencies(sub_functional_area_id,name,description) VALUES(?,?,?)", (competency.sub_functional_area_id, competency.name, competency.description))
        return Competency(cursor.lastrowid, competency.sub_functional_area_id, competency.name, competency.description)

    def get_current(self) -> FrameworkVersion | None:
        """Return the currently active version, if one exists."""
        row = self._connection.execute("SELECT * FROM framework_versions WHERE is_current=1").fetchone()
        return self._to_version(row) if row else None

    def get(self, version_id: int) -> FrameworkVersion | None:
        """Return one framework version by identity."""
        row = self._connection.execute("SELECT * FROM framework_versions WHERE id=?", (version_id,)).fetchone()
        return self._to_version(row) if row else None

    def list_versions(self) -> list[FrameworkVersion]:
        """Return framework versions newest first."""
        rows = self._connection.execute("SELECT * FROM framework_versions ORDER BY created_at DESC").fetchall()
        return [self._to_version(row) for row in rows]

    def list_areas(self, version_id: int) -> list[SubFunctionalArea]:
        """Return the areas belonging to one version."""
        rows = self._connection.execute("SELECT * FROM sub_functional_areas WHERE framework_version_id=? ORDER BY name", (version_id,)).fetchall()
        return [SubFunctionalArea(row["id"], row["framework_version_id"], row["cap_area"] if "cap_area" in row.keys() else None, row["name"], row["description"]) for row in rows]

    def list_competencies(self, area_id: int) -> list[Competency]:
        """Return the competencies belonging to one area."""
        rows = self._connection.execute("SELECT * FROM competencies WHERE sub_functional_area_id=? ORDER BY name", (area_id,)).fetchall()
        return [Competency(row["id"], row["sub_functional_area_id"], row["name"], row["description"]) for row in rows]

    def commit(self) -> None:
        """Commit the active unit of work."""
        self._connection.commit()

    def rollback(self) -> None:
        """Rollback the active unit of work."""
        self._connection.rollback()

    @staticmethod
    def _to_version(row: sqlite3.Row) -> FrameworkVersion:
        return FrameworkVersion(row["id"], row["version"], datetime.fromisoformat(row["created_at"]), bool(row["is_current"]))
