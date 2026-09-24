"""SQLite connection and idempotent schema initialisation."""
import os
import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS scan_summaries (scan_run_id INTEGER PRIMARY KEY REFERENCES scan_runs(id) ON DELETE CASCADE, evidence_count INTEGER NOT NULL, health_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sources (id INTEGER PRIMARY KEY, name TEXT NOT NULL, url TEXT NOT NULL UNIQUE, organisation TEXT NOT NULL, source_family TEXT NOT NULL DEFAULT 'PROFESSIONAL_BODY', country TEXT NOT NULL DEFAULT 'Unknown', source_type TEXT NOT NULL DEFAULT 'ARTICLE', source_role TEXT NOT NULL DEFAULT 'PRIMARY_DISCOVERY', llm_allowed INTEGER NOT NULL DEFAULT 1, enabled INTEGER NOT NULL, evidence_label TEXT NOT NULL DEFAULT 'news / commentary', use_browser_rendering INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS scan_runs (id INTEGER PRIMARY KEY, started_at TEXT NOT NULL, completed_at TEXT, status TEXT NOT NULL, error_summary TEXT, sources_snapshot TEXT NOT NULL DEFAULT '[]');
CREATE TABLE IF NOT EXISTS framework_versions (id INTEGER PRIMARY KEY, version TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL, is_current INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS sub_functional_areas (id INTEGER PRIMARY KEY, framework_version_id INTEGER NOT NULL REFERENCES framework_versions(id), cap_area TEXT, name TEXT NOT NULL, description TEXT);
CREATE TABLE IF NOT EXISTS competencies (id INTEGER PRIMARY KEY, sub_functional_area_id INTEGER NOT NULL REFERENCES sub_functional_areas(id), name TEXT NOT NULL, description TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS evidence (id INTEGER PRIMARY KEY, scan_run_id INTEGER NOT NULL REFERENCES scan_runs(id), source_id INTEGER NOT NULL REFERENCES sources(id), evidence_type TEXT NOT NULL DEFAULT 'Unknown', title TEXT NOT NULL, publication_date TEXT, organisation TEXT NOT NULL, url TEXT NOT NULL, article_text TEXT NOT NULL, extracted_at TEXT NOT NULL, explicit_or_inferred TEXT NOT NULL DEFAULT 'INFERRED');
CREATE TABLE IF NOT EXISTS recommendation_batches (id INTEGER PRIMARY KEY, framework_version_id INTEGER NOT NULL REFERENCES framework_versions(id), scan_run_id INTEGER REFERENCES scan_runs(id), framework_snapshot TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS recommendations (id INTEGER PRIMARY KEY, batch_id INTEGER NOT NULL REFERENCES recommendation_batches(id), recommendation_type TEXT NOT NULL, confidence REAL NOT NULL, reasoning TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS batch_questions (id INTEGER PRIMARY KEY, recommendation_batch_id INTEGER NOT NULL REFERENCES recommendation_batches(id), question TEXT NOT NULL, answer TEXT NOT NULL, context_snapshot TEXT NOT NULL DEFAULT '{}', asked_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS fallback_recoveries (id INTEGER PRIMARY KEY, scan_run_id INTEGER REFERENCES scan_runs(id), source_name TEXT NOT NULL, organisation TEXT NOT NULL, source_url TEXT NOT NULL, recovery_status TEXT NOT NULL, recovered_item_count INTEGER NOT NULL, raw_result TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS source_url_recommendations (id INTEGER PRIMARY KEY, scan_run_id INTEGER REFERENCES scan_runs(id), recommendation_batch_id INTEGER REFERENCES recommendation_batches(id), status TEXT NOT NULL, source_snapshot TEXT NOT NULL DEFAULT '[]', raw_result TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);
"""

MIGRATION_2 = """
ALTER TABLE recommendations ADD COLUMN supporting_evidence_ids TEXT NOT NULL DEFAULT '[]';
ALTER TABLE recommendations ADD COLUMN supporting_urls TEXT NOT NULL DEFAULT '[]';
ALTER TABLE recommendations ADD COLUMN supporting_organisations TEXT NOT NULL DEFAULT '[]';
"""

MIGRATION_3 = """
ALTER TABLE sources ADD COLUMN category TEXT NOT NULL DEFAULT 'Uncategorised';
ALTER TABLE sources ADD COLUMN credibility_rationale TEXT NOT NULL DEFAULT '';
"""

MIGRATION_4 = """
ALTER TABLE sources ADD COLUMN max_articles_per_scan INTEGER NOT NULL DEFAULT 25;
ALTER TABLE sources ADD COLUMN article_url_pattern TEXT NOT NULL DEFAULT '';
"""

MIGRATION_5 = """
-- publication window removed
"""

MIGRATION_6 = """
ALTER TABLE sources ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1;
UPDATE sources SET is_active = 1 WHERE is_active IS NULL;
"""

MIGRATION_7 = """
ALTER TABLE sources ADD COLUMN max_listing_pages INTEGER NOT NULL DEFAULT 3;
"""

MIGRATION_8 = """
ALTER TABLE recommendations ADD COLUMN sub_functional_area TEXT NOT NULL DEFAULT '';
ALTER TABLE recommendations ADD COLUMN competency TEXT NOT NULL DEFAULT '';
ALTER TABLE recommendations ADD COLUMN kind_of_changes_suggested TEXT NOT NULL DEFAULT '';
ALTER TABLE recommendations ADD COLUMN reasons_for_suggesting_the_changes TEXT NOT NULL DEFAULT '';
"""

MIGRATION_9 = """
ALTER TABLE recommendation_batches ADD COLUMN scan_run_id INTEGER REFERENCES scan_runs(id);
ALTER TABLE recommendation_batches ADD COLUMN framework_snapshot TEXT NOT NULL DEFAULT '{}';
"""

MIGRATION_10 = """
ALTER TABLE sources ADD COLUMN use_browser_rendering INTEGER NOT NULL DEFAULT 0;
"""

MIGRATION_13 = """
ALTER TABLE sources ADD COLUMN evidence_label TEXT NOT NULL DEFAULT 'news / commentary';
UPDATE sources SET evidence_label = 'news / commentary' WHERE evidence_label IS NULL OR evidence_label = '';
"""

MIGRATION_14 = """
ALTER TABLE sources ADD COLUMN country TEXT NOT NULL DEFAULT 'Unknown';
UPDATE sources SET country = 'Unknown' WHERE country IS NULL OR country = '';
"""

MIGRATION_15 = """
ALTER TABLE sources ADD COLUMN source_type TEXT NOT NULL DEFAULT 'ARTICLE';
ALTER TABLE sources ADD COLUMN source_role TEXT NOT NULL DEFAULT 'PRIMARY_DISCOVERY';
ALTER TABLE sources ADD COLUMN llm_allowed INTEGER NOT NULL DEFAULT 1;
ALTER TABLE evidence ADD COLUMN explicit_or_inferred TEXT NOT NULL DEFAULT 'INFERRED';
"""

MIGRATION_16 = """
ALTER TABLE sources ADD COLUMN source_family TEXT NOT NULL DEFAULT 'PROFESSIONAL_BODY';
"""

MIGRATION_17 = """
CREATE TABLE IF NOT EXISTS batch_questions (id INTEGER PRIMARY KEY, recommendation_batch_id INTEGER NOT NULL REFERENCES recommendation_batches(id), question TEXT NOT NULL, answer TEXT NOT NULL, context_snapshot TEXT NOT NULL DEFAULT '{}', asked_at TEXT NOT NULL);
"""

MIGRATION_18 = """
CREATE TABLE IF NOT EXISTS fallback_recoveries (id INTEGER PRIMARY KEY, scan_run_id INTEGER REFERENCES scan_runs(id), source_name TEXT NOT NULL, organisation TEXT NOT NULL, source_url TEXT NOT NULL, recovery_status TEXT NOT NULL, recovered_item_count INTEGER NOT NULL, raw_result TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);
"""

MIGRATION_19 = """
CREATE TABLE IF NOT EXISTS source_url_recommendations (id INTEGER PRIMARY KEY, scan_run_id INTEGER REFERENCES scan_runs(id), recommendation_batch_id INTEGER REFERENCES recommendation_batches(id), status TEXT NOT NULL, source_snapshot TEXT NOT NULL DEFAULT '[]', raw_result TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);
"""

MIGRATION_11 = """
ALTER TABLE evidence ADD COLUMN evidence_type TEXT NOT NULL DEFAULT 'Unknown';
"""

MIGRATION_12 = """
ALTER TABLE sub_functional_areas ADD COLUMN cap_area TEXT;
"""


def connect(database_path: Path) -> sqlite3.Connection:
    """Open a configured SQLite database with foreign keys enabled."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialise(connection: sqlite3.Connection) -> None:
    """Apply the current schema migrations once, in order."""
    connection.executescript(SCHEMA)
    connection.execute("INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES (1, datetime('now'))")
    applied = {row[0] for row in connection.execute("SELECT version FROM schema_migrations")}
    if 2 not in applied:
        connection.executescript(MIGRATION_2)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (2, datetime('now'))")
    if 3 not in applied:
        connection.executescript(MIGRATION_3)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (3, datetime('now'))")
    if 4 not in applied:
        connection.executescript(MIGRATION_4)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (4, datetime('now'))")
    if 5 not in applied:
        connection.executescript(MIGRATION_5)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (5, datetime('now'))")
    if 6 not in applied:
        connection.executescript(MIGRATION_6)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (6, datetime('now'))")
    if 7 not in applied:
        connection.executescript(MIGRATION_7)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (7, datetime('now'))")
    if 8 not in applied:
        connection.executescript(MIGRATION_8)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (8, datetime('now'))")
    if 9 not in applied:
        existing_columns = {row[1] for row in connection.execute("PRAGMA table_info(recommendation_batches)")}
        statements = []
        if "sources_snapshot" not in {row[1] for row in connection.execute("PRAGMA table_info(scan_runs)")}:
            statements.append("ALTER TABLE scan_runs ADD COLUMN sources_snapshot TEXT NOT NULL DEFAULT '[]'")
        if "scan_run_id" not in existing_columns:
            statements.append("ALTER TABLE recommendation_batches ADD COLUMN scan_run_id INTEGER REFERENCES scan_runs(id)")
        if "framework_snapshot" not in existing_columns:
            statements.append("ALTER TABLE recommendation_batches ADD COLUMN framework_snapshot TEXT NOT NULL DEFAULT '{}'")
        if statements:
            connection.executescript(";\n".join(statements) + ";")
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (9, datetime('now'))")
    if 10 not in applied:
        if "use_browser_rendering" not in {row[1] for row in connection.execute("PRAGMA table_info(sources)")}:
            connection.executescript(MIGRATION_10)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (10, datetime('now'))")
    if 11 not in applied:
        if "evidence_type" not in {row[1] for row in connection.execute("PRAGMA table_info(evidence)")}:
            connection.executescript(MIGRATION_11)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (11, datetime('now'))")
    if 12 not in applied:
        if "cap_area" not in {row[1] for row in connection.execute("PRAGMA table_info(sub_functional_areas)")}:
            connection.executescript(MIGRATION_12)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (12, datetime('now'))")
    if 13 not in applied:
        if "evidence_label" not in {row[1] for row in connection.execute("PRAGMA table_info(sources)")}:
            connection.executescript(MIGRATION_13)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (13, datetime('now'))")
    if 14 not in applied:
        if "country" not in {row[1] for row in connection.execute("PRAGMA table_info(sources)")}:
            connection.executescript(MIGRATION_14)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (14, datetime('now'))")
    if 15 not in applied:
        statements = []
        source_columns = {row[1] for row in connection.execute("PRAGMA table_info(sources)")}
        evidence_columns = {row[1] for row in connection.execute("PRAGMA table_info(evidence)")}
        if "source_type" not in source_columns:
            statements.append("ALTER TABLE sources ADD COLUMN source_type TEXT NOT NULL DEFAULT 'ARTICLE'")
        if "source_role" not in source_columns:
            statements.append("ALTER TABLE sources ADD COLUMN source_role TEXT NOT NULL DEFAULT 'PRIMARY_DISCOVERY'")
        if "llm_allowed" not in source_columns:
            statements.append("ALTER TABLE sources ADD COLUMN llm_allowed INTEGER NOT NULL DEFAULT 1")
        if "explicit_or_inferred" not in evidence_columns:
            statements.append("ALTER TABLE evidence ADD COLUMN explicit_or_inferred TEXT NOT NULL DEFAULT 'INFERRED'")
        if statements:
            connection.executescript(";\n".join(statements) + ";")
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (15, datetime('now'))")
    if 16 not in applied:
        if "source_family" not in {row[1] for row in connection.execute("PRAGMA table_info(sources)")}:
            connection.executescript(MIGRATION_16)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (16, datetime('now'))")
    if 17 not in applied:
        connection.executescript(MIGRATION_17)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (17, datetime('now'))")
    if 18 not in applied:
        connection.executescript(MIGRATION_18)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (18, datetime('now'))")
    if 19 not in applied:
        connection.executescript(MIGRATION_19)
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (19, datetime('now'))")
    if 20 not in applied:
        from src.services.source_schema import migrated_type
        columns = {row[1] for row in connection.execute('PRAGMA table_info(sources)')}
        if 'evidence_label' in columns:
            for row in connection.execute('SELECT id, source_type, evidence_label FROM sources').fetchall():
                connection.execute('UPDATE sources SET source_type=? WHERE id=?',
                                   (migrated_type(row[1], row[2]).value, row[0]))
        for column in ('country', 'category', 'evidence_label'):
            if column in columns:
                connection.execute(f'ALTER TABLE sources DROP COLUMN {column}')
        connection.execute("INSERT INTO schema_migrations(version, applied_at) VALUES (20, datetime('now'))")
    reset_flag = Path("data/reset_history.flag")
    if os.getenv("RESET_HISTORY_ON_START") == "1" or reset_flag.exists():
        connection.executescript(
            """
            DELETE FROM recommendations;
            DELETE FROM recommendation_batches;
            DELETE FROM evidence;
            DELETE FROM scan_runs;
            DELETE FROM fallback_recoveries;
            DELETE FROM source_url_recommendations;
            DELETE FROM schema_migrations WHERE version > 20;
            """
        )
        try:
            reset_flag.unlink(missing_ok=True)
        except OSError:
            pass
    connection.commit()
