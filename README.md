# STE Public Evidence Collector

For a small test scan, open **Source Configuration → Quick scan selection**. Choose sources and click **Enable only selected sources**. Run the scan normally, then click **Restore previous selection** to return to your earlier enabled sources. These controls affect only your session and discard unsaved editor drafts; they never modify the master list. The restore snapshot lasts only for the current session.

A Streamlit prototype for collecting public Science, Technology and Engineering evidence from professional bodies, higher-learning institutions and government agencies. Officers configure sources, scan, inspect source health and download one evidence TXT for analysis in a separately approved government AI assistant.

**Current scope: public collection and export only.** The active app does not require an OpenAI key, accept internal competency frameworks or generate AI recommendations. Legacy analysis modules remain for compatibility, not as active UI features.

## Quick start — trusted local workstation

Python 3.10+ is required. Current tests run on Windows/Python 3.10; Linux cloud/browser acceptance must also be checked.

```powershell
git clone https://github.com/huangchaohung/competency-intelligence-system.git
cd competency-intelligence-system
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python -m pytest
python -m streamlit run app.py
```

On Linux/macOS activate with `source .venv/bin/activate`. Linux browser dependencies require system installation; the cloud deployment uses Chromium from `packages.txt`.

Use **`app.py` everywhere**, locally and on Streamlit Cloud. There is no administrator mode or API key. Each browser session gets its own temporary workspace. See [deployment instructions](docs/streamlit_cloud_deployment.md).

Sources and evidence are held in a session-specific in-memory database, not saved to `.cloud_runtime/` or `data/`. Existing disk data is left untouched and never loaded by the UI. Use `app.py` for both local and Cloud deployments. New sessions start from the read-only master `config/sources.yaml` with no evidence. Brief reconnections may resume a session; **Start fresh** explicitly discards it.

## Officer workflow

1. **Source Configuration:** use defaults, temporarily edit/add/delete rows, or upload a CSV using the downloadable template. Validate and apply changes to your copy only. Restore default sources whenever needed.
2. **Scan & Download:** click **Scan enabled sources**. Inspect source health and actual extracted text, not just record counts.
3. Click **Prepare evidence TXT**, then download **public_evidence.txt**. Opening the page or completing a scan never prepares the file automatically. Starting another scan discards the previous result in your session.
4. Transfer through an approved channel and analyse against the internal framework inside the approved government environment.

The TXT contains UTF-8 JSON and full retained text, not just the shortened UI previews. The download is the officer's archive. There is no History page in the current UI.

## IT handover documentation

| Document | Purpose |
| --- | --- |
| [Architecture](docs/architecture.md) | Pipeline, module map, database and export contract |
| [Deployment](docs/streamlit_cloud_deployment.md) | Cloud secrets, access, smoke tests and storage limits |
| [Operations](docs/operations.md) | Logs, backup/restore, network and crawler troubleshooting |
| [Development](CONTRIBUTING.md) | Tests, source tuning and publication workflow |
| [Security](SECURITY.md) | Sensitive-data boundaries and outstanding hardening |
| [Tuning status](docs/source_tuning_status.md) | Verified fixes and unresolved source access |

## Repository map

```text
app.py                  Single supported local/cloud entrypoint
config/sources.yaml     Public catalogue seed
src/dashboard/         Streamlit UI; collector.py is Scan & Download
src/workflow/          Scan orchestration and catalogue workflow
src/scanner/           HTTP/browser discovery, extraction, site-specific routes
src/repositories/      SQLite persistence
src/services/          Configuration, health, export and logging
src/core/database.py   Schema migrations
tests/                 Regression tests
scripts/               Explicit maintenance/package utilities
docs/                  Technical handover
```

## Release limitations

- **Private trial, not government-approved production hosting.** The receiving team must approve hosting, transfers and downstream AI use.
- Users do not share catalogues/results. Session memory is temporary; download before leaving. This is not authentication or an enterprise security boundary. Keep hosting restricted to approved users and enforce network egress controls.
- Robots, authentication, anti-bot controls and website changes can prevent retrieval. Successful counts do not prove useful text or complete coverage.
- No LLM fallback crawler runs; unhealthy URLs require manual review. No automatic URL substitution occurs.
- Dependency versions use ranges, not a lockfile. OpenAI/framework dependencies support legacy modules/tests, not active AI calls.
- No software licence is declared. Confirm ownership and redistribution terms before reuse beyond the agreed team.

Share this repository, not the original working folder. Never commit databases, logs, evidence exports, internal frameworks or secrets.
# Compact government transfer (2026-10-13)

Scan & Download now prepares numbered TXT parts, each at most 400,000 characters. Download all parts. Every evidence ID and URL is retained, but text is whitespace-normalised and shortened to distributed excerpts with explicit omission flags. This is not an AI summary or a guarantee that all competencies are preserved. Reading priority follows source metadata, not credibility. Use the current `docs/government_assistant_guide.txt` for part-by-part cited-ledger analysis; uploading multiple parts does not enlarge the assistant's context window. The existing full-text exporter remains an internal compatibility function, not the default download. Source tuning is temporarily paused.

# Current Cloud download format

## V5 default collection plan

Build `master-v5-cards-1` uses 164 enabled URLs for 106 organisations. V5 provides leaf URLs for eight organisations; the remaining URLs are resolved from the v4/v2 registries and existing catalogue, with provenance in `config/competency_scan_plan.json`. No URLs are invented and no organisation is dropped. `DROP_OR_DISCOVER` means bounded DISCOVER. Some inherited seeds remain unverified or unsuitable and may yield zero cards.

The Cloud scanner now uses the bounded competency collector: SCAN follows a small candidate set, RETEST can use normal browser rendering, DISCOVER considers at most 15 candidates plus bounded sitemap discovery. Domain/robots policies remain enforced. Existing sessions preserve edits; click **Start fresh** after deployment to load the new defaults. User-added/changed URLs default to SCAN and the entered host boundary.

Native v5 runs export actual request/skip logs and organisation statuses alongside cards, without shortening the cards a second time. Failed sources are isolated; zero-card scans can still download their logs/status. Four cards per source, 1,000 serialized characters per card, 5,000 per organisation and <300,000 characters per card file are ceilings, not promises of substantive coverage. Automatic filtering is not the historical manual review. Internal frameworks and AI calls remain outside the app.

The legacy export behaviour below applies only to older in-memory scans without native collector results.

Build `competency-txt-1` prepares competency cards from the current session only. On **Scan & Download**, click **Prepare download files**, then download every TXT button. Preparation is offline and does not make AI requests or start another scan.

- `cards_part_001.txt` onward: JSON arrays of selective competency/course excerpts, each file below 300,000 characters. Complete cards are limited to 1,000 characters, four per configured source and 5,000 characters per organisation.
- `organisation_status.txt`: current-scan coverage, including organisations with no qualifying exported cards. This does not prove no public resource exists.
- `url_log.txt`: retained-evidence export decisions, including budget exclusions. This is **not a complete network-attempt log**; HTTP statuses/rendering details unavailable in stored evidence are not invented.

Use all files with the government assistant. Excerpts omit information and can lose PDF table relationships. Do not infer missing competencies, obsolescence or matrix mappings. Keep any separately self-searched material labelled and do not use it alone to support recommendations or to support deletion. Counts are computed from this session, not the historical reviewed corpus. Deterministic filtering does not replace content review.

# Current card export update

New Cloud scans use up to 3,000 serialized characters per card and 15,000 per organisation. Excerpts retain whole selected blocks/sentences, not full inventories. Missing dates and countries are explicitly unknown. Resource-type priority does not establish credibility.

Download **all files sharing the same scan identifier**: cards parts, organisation status and URL log. Do not mix earlier downloads. The exporter checks card totals before download. Each part remains under 300,000 characters. Start a new scan to benefit from longer excerpts; previously discarded text cannot be recovered from old cards.

