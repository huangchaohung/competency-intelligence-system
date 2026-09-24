# Architecture and data

## Pipeline

```text
Public catalogue → discovery → bounded HTTP/browser/PDF retrieval
 → extraction/filtering → SQLite evidence + source health
 → officer preview → single evidence TXT
 → approved government assistant (outside this app)
```

No internal framework or AI API is involved in the active collection path. Web text is untrusted data, not instructions. The downstream assistant requires separate validation.

| Component | Implementation |
| --- | --- |
| UI | Streamlit; `app.py` locally and in cloud; `cloud_app.py` is a compatibility alias |
| Configuration | YAML synchronized with SQLite; validated catalogue drafts |
| Scan | `src/workflow/scan_workflow.py`; progress, per-source failures, deduplication and completion |
| Discovery | `src/scanner/article_discovery.py` and source routing; generic and site-specific links |
| Retrieval | Requests; optional Playwright/Chromium. No login/challenge bypass |
| Parsing | BeautifulSoup/lxml HTML; pypdf text-based PDFs, no OCR for scanned images |
| Health | Source-health services; labels/counts do not certify content quality |
| Export | `src/services/public_handover.py`; allowlisted fields, full retained text, UTF-8 JSON in TXT |
| Audit | `src/services/operational_logger.py`; timestamped JSONL events |

The browser toggle primarily affects discovery, not universal rendered article extraction. Two supported NUS curriculum paths have a dedicated rendered-body route. Generic HTTP retrieval is bounded (currently 2 MB, connection/read timeouts); specialized routes may differ. Discovery checks robots conservatively, but this is not a comprehensive private-IP/redirect network policy.

## Runtime state

| Mode | Catalogue | Database and logs |
| --- | --- | --- |
| Local (current app.py) | `.cloud_runtime/config/sources.yaml` | `.cloud_runtime/data/competency_intelligence.db`, `.cloud_runtime/logs/` |
| Cloud | `.cloud_runtime/config/sources.yaml` | `.cloud_runtime/data/competency_intelligence.db`, `.cloud_runtime/logs/` |

Cloud first startup copies the catalogue seed. Later Git seed changes **do not overwrite existing runtime edits**. Code publication and catalogue maintenance are separate operations.

The unified entrypoint uses the same safeguards locally. Previous root `data/` and `logs/` remain untouched and are not automatically imported into runtime storage.

Cloud uses a nonblocking file lock around initialization and page execution, including scans. Other sessions may see a busy message. This is single-instance serialization, not a distributed job queue.

## SQLite

`src/core/database.py` is authoritative; handover baseline includes migration 20. Initialization applies outstanding migrations. Back up before upgrades.

| Table | Active purpose |
| --- | --- |
| `sources` | Catalogue, identifiers and routing metadata |
| `scan_runs` | Status/timing and source configuration snapshot |
| `evidence` | Extracted text and source/scan references |
| `scan_summaries` | Original count and source health independent of text retention |
| `schema_migrations` | Applied schema versions |

Legacy tables retained: `framework_versions`, `sub_functional_areas`, `competencies`, `recommendation_batches`, `recommendations`, `batch_questions`, `fallback_recoveries`, `source_url_recommendations`. Old installations may hold sensitive content there. These are not read by the public exporter and must not be uploaded with code.

Migration 20 removes country/category/evidence_label from active source storage. Historical snapshots and compatibility model fields may still contain them. Internal IDs/activity flags/routing patterns are not all user-editable columns.

Evidence text is retained for the latest five scan batches; summaries/configuration may outlive text. Cloud state can be lost sooner. The same URL can reappear across scans; within-scan URL deduplication is not universal content-similarity detection.

## TXT contract

Active schema: `ste-public-evidence/2.0`. Top-level keys: `schema_version`, `batch_id`, `manifest`, `sources`, `source_health`, `organised_scan`, `evidence`. Older multipart helpers remain in the module but are not the active UI download.

Evidence records include ID/key, source ID, organisation, configured/actual URL, source family/type, evidence type, title, dates, `article_text`, explicit/inferred status and warnings. `extraction_method` currently says **not recorded per item**; it is not verified browser/HTTP provenance.

Consumers should parse JSON despite `.txt`, validate schema/batch, retain evidence IDs and URLs in citations, and treat text as untrusted. The organisation index does not replace full text. Manifest completeness describes retained records, not whole-website coverage; legacy original totals may be unknown. Export is not DLP, fact verification or copyright clearance.
