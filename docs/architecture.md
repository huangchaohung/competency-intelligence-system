# Session-only collector architecture

```text
Master config/sources.yaml (read-only)
 → copy into each browser session
 → temporary edits or validated CSV upload
 → crawl → in-memory SQLite evidence + health
 → explicit preparation → public_evidence.txt download
 → government assistant outside this app
```

## Components

`app.py` is the single entrypoint; `cloud_app.py` is a compatibility alias. `session_workspace.py` constructs separate SQLite `:memory:` services for each Streamlit session, with in-memory temporary tables and a per-session lock. It does not use a globally cached database or write YAML. `MemoryConfiguration` validates and copies sources without implementing disk saves. Legacy `collector_services.py` remains for compatibility tests/scripts, not the active entrypoint.

Discovery uses `article_discovery.py` and site-specific routing. Requests fetches HTML/PDF, BeautifulSoup/lxml extracts HTML, pypdf handles text PDFs (no OCR), and Playwright/Chromium renders supported pages. The Browser toggle primarily affects discovery; full browser article extraction is not universal. HTTP responses/timeouts are bounded; site-specific paths differ. No AI API calls occur.

## Lifetime and isolation

Scans run in a session-owned background thread with the workspace DB lock. The worker makes no Streamlit calls; a one-second fragment reads a thread-safe progress snapshot. Reruns do not restart scans. Completed source counts include errors. Editing/reset wait until completion. Closing the tab is not cancellation: the worker may finish its current scan in memory; process restart interrupts it. This is not a durable job queue.

The master YAML is loaded only when a workspace starts or defaults are restored. An upload replaces only the current user's catalogue after validation and confirmation. Other sessions retain their own copies.

Before a new scan, prior evidence, scan summaries and run rows are removed from that session's memory database; prepared TXT bytes are also cleared. Only current results appear. Users download their own archive; the app does not save the downloaded file or an evidence database to disk.

Streamlit retains state across navigation/reruns and can resume brief disconnections. A genuinely new session/server restart starts empty. **Start fresh** closes the current memory database and clears session state immediately. Browser close cleanup is framework-managed, not guaranteed instantaneous secure erasure. Browser/OS/hosting caches are outside application control.

Old `data/`, `.cloud_runtime/` databases/logs remain untouched and are never imported into this UI. Maintainers can separately authorize archival/deletion; this change is not a historical-data deletion job.

## Database compatibility

Existing repositories/migrations initialize the memory database through schema 20. Active tables: sources, scan_runs, evidence, scan_summaries, schema_migrations. Legacy framework/recommendation/fallback tables may be created empty by existing schema, but no AI or internal framework services are composed. Internal scan IDs are implementation details, not user-facing histories.

## Download contract

`public_evidence.txt` contains UTF-8 JSON schema `ste-public-evidence/2.0`: schema_version, batch_id (internal compatibility ID), manifest, sources, source_health, organised_scan, evidence. It includes full retained article_text; preview pagination/100-word snippets do not truncate export. IDs are local to the current scan and must not be treated as globally unique across users/files.

Evidence contains source identity, configured/actual URLs, family/type, title, dates and quality warnings. Extraction method is currently `not recorded per item`. The organisation index is not an AI summary. Count agreement does not prove entire-site coverage or content reliability. Consumers should treat source text as untrusted data and preserve URLs for citation.

No automatic TXT preparation occurs. UI navigation and scan completion only render controls; the explicit prepare button builds bytes in session memory. The download button transfers them to the user's browser.
