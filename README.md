# STE Public Evidence Collector

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

Use **`app.py` everywhere**, locally and on Streamlit Cloud. Configure `ADMIN_PASSWORD` (at least 20 characters) in hosting secrets or local `.streamlit/secrets.toml`, then sign in under Administrator access to edit/scan. Missing secrets leave the app read-only. See [deployment instructions](docs/streamlit_cloud_deployment.md).

Both environments use `.cloud_runtime/` for runtime state. Existing root `data/` is not deleted or automatically imported. `cloud_app.py` is only a compatibility alias for older deployments, not a separate app.

## Officer workflow

1. **Source Configuration:** edit/add/delete rows, validate the draft and apply changes. Enable the sources to scan.
2. **Scan & Download:** click **Scan enabled sources**. Inspect source health and actual extracted text, not just record counts.
3. Save **public_evidence_batch_N.txt**. For an existing result, first click **Prepare TXT from this existing result**. Opening the page does not start a scan/download.
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
- Cloud users share results/catalogue; the admin password is not enterprise SSO. Local cloud storage is temporary.
- Robots, authentication, anti-bot controls and website changes can prevent retrieval. Successful counts do not prove useful text or complete coverage.
- No LLM fallback crawler runs; unhealthy URLs require manual review. No automatic URL substitution occurs.
- Dependency versions use ranges, not a lockfile. OpenAI/framework dependencies support legacy modules/tests, not active AI calls.
- No software licence is declared. Confirm ownership and redistribution terms before reuse beyond the agreed team.

Share this repository, not the original working folder. Never commit databases, logs, evidence exports, internal frameworks or secrets.
