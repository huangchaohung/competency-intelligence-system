# STE Public Evidence Collector

A Streamlit application for collecting public **Science, Technology and Engineering (STE)** competency, course, curriculum and standards evidence.

**Handover candidate: `handover-rc-1`.** This is a collection prototype for approved trials, not a government-approved production service.

## Purpose and boundaries

Officers scan public sources and download evidence for analysis in a separately approved government AI assistant. Internal competency frameworks belong in that approved environment, **not this app**.

The active app makes **no AI requests** and needs **no OpenAI API key**. Legacy AI modules remain for compatibility but are not active user features.

## Officer workflow

1. Open **Source Configuration**. Use defaults, upload a source CSV or temporarily edit your copy. Validate and apply changes.
2. For a small trial, use **Quick scan selection → Enable only selected sources**. Restore the earlier selection afterwards if needed.
3. Open **Scan & Download**, start the scan and keep the session open. Failed sources are recorded; they should not stop the remaining scan.
4. Review source health and actual card text. Counts alone do not establish quality.
5. Click the prepare-download button and download **every TXT file with the same identifier**.
6. Archive the files together and transfer them through an approved channel to the government assistant.

Each session has its own sources and in-memory SQLite database. Edits never overwrite the master catalogue. A new scan replaces current results. **Start fresh** discards the session and reloads defaults. Brief reconnections can resume a session; closing a tab is not a guaranteed immediate deletion mechanism. Download before leaving.

## Download format

| File | Contents |
| --- | --- |
| `cards_part_001_<identifier>.txt` and subsequent parts | UTF-8 JSON arrays of evidence excerpts, source URLs and metadata |
| `organisation_status_<identifier>.txt` | CSV-formatted coverage and failures for scanned organisations |
| `url_log_<identifier>.txt` | CSV-formatted request/skip decisions, HTTP status, requested/resolved URLs and rejection diagnostics |

Do not mix identifiers. The exporter checks totals and card-to-log provenance. Each card part is below **300,000 characters** without splitting a card.

Native scan limits are **3,000 serialized characters/card**, **four cards/source**, and **15,000 characters/organisation**. Metadata counts towards these limits. Excerpts select whole blocks or sentences, not full inventories. Dates/countries remain unknown when unavailable. Resource-type priority is not a credibility score.

PDF tables may lose relationships; there is no OCR. Missing cards do not prove missing or obsolete competencies. Automatically selected evidence still requires officer review.

## Technical pipeline

```text
Session sources + matching scan-plan settings
    → configured seed + bounded sitemap discovery
    → ranked candidate queue
    → HTTP / conditional browser fetch
    → HTML or PDF extraction and deterministic filters
    → cards, organisation status and URL log
    → offline TXT preparation and download
```

- HTTP uses `requests`; redirects are followed with domain/robots checks.
- HTML extraction uses BeautifulSoup and removes recognised navigation/cookie elements.
- PDF extraction uses `pypdf`, not OCR or reliable table reconstruction.
- Browser rendering uses Playwright/Chromium. Optional escalation targets sparse JavaScript shells; explicitly required rendering remains supported. Images, fonts and media are blocked.
- The configured seed gets an attempt before inferred candidates. The ranked queue is capped at 100 candidates with pruning logged.
- SCAN/RETEST generally consider at most the card limit plus one content candidate; DISCOVER considers up to 15. Robots, sitemaps, redirects and browser assets are additional requests.
- Download bounds remain 8 MB/35 seconds; PDF extraction is limited to 300 pages.
- Relevance decisions use URL, heading and body signals—not an LLM. Login/member-only, enquiry, search/faceted and known non-resource pages are excluded.
- Authentication, robots and anti-bot restrictions are **not bypassed**. Improved retrieval is not proof of representative coverage.

## Install and run

Python 3.10+ is required. Windows/Python 3.10 is the tested local environment.

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

On Linux/macOS use `source .venv/bin/activate`; Chromium also needs system libraries. Streamlit Cloud uses `requirements.txt` and `packages.txt`.

Use **`app.py` everywhere**, including Streamlit Cloud. The original developer workspace's `.cloud-deploy` folder is a publishing checkout, not another app entrypoint. Share this GitHub repository rather than the developer's working folder.

## Maintainer code map

| Location | Responsibility |
| --- | --- |
| `app.py` | Entry point, navigation and session lifecycle |
| `config/sources.yaml` | Read-only master catalogue; JSON-formatted YAML |
| `config/competency_scan_plan.json` | Matching organisation/URL modes and domain settings |
| `src/services/session_workspace.py` | Session services and visible build label |
| `src/services/scan_job.py` | Background scan and progress |
| `src/workflow/competency_scan_workflow.py` | Active orchestration and card budgets |
| `src/scanner/competency_pilot.py` | Active collector despite its historical “pilot” filename |
| `src/services/competency_export.py` | TXT export and provenance validation |
| `src/dashboard/collector.py` | Scan/result/download interface |
| `tests/` | Regression tests |
| `docs/development_blueprint.md` | Progress and deferred work |

When changing master URLs, review matching scan-plan entries too. User-added/changed URLs without a plan default to SCAN and their host boundary. Never invent evidence or silently substitute an unverified source.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Old Cloud build | Deployed repository, `main` branch, `app.py` entrypoint and deployment logs. A Git push does not confirm deployment. |
| New build, old results | Download anything needed, then Start fresh and rescan. Old scans are not reprocessed automatically. |
| Zero cards | URL-log reasons: distinguish policy/access failures, relevance rejection and budget limits. |
| Export validation error | Preserve error/build information; inspect organisation, source IDs and requested/resolved URLs. Do not disable validation. |
| Browser unavailable | Chromium installation locally or Cloud packages/startup logs. |
| Poor PDF text | Review manually; image PDFs and complex tables may need approved manual handling. |
| Lost result | Session memory is not archival storage. The downloaded TXT files are the officer's archive. |

Logs may include public-text samples and URL query strings. Review before sharing. Never commit evidence exports, databases, logs, secrets or internal frameworks.

## Final acceptance and freeze

**Do one final Cloud acceptance run, then freeze features.** Perfect coverage of all organisations is not a release condition.

- [ ] Visible build is `handover-rc-1`.
- [ ] Temporary edits do not change a separate session's sources.
- [ ] A failed source does not stop the scan; progress completes.
- [ ] Preparation stays on Scan & Download and all TXT files download.
- [ ] Identifiers and totals agree, including redirected sources.
- [ ] Officer reviews ten cards across source families, including a PDF, and records weak cards/no-card organisations as known limitations.
- [ ] Receiving officer can use the app and understands the TXT analysis handover.
- [ ] Record accepted commit, build, acceptance date and known issues in `docs/handover_acceptance.md`.

After acceptance, tag the accepted commit. Change only reproducible blocking defects or security issues. Larger budgets, manual-file ingestion and further source tuning belong in a later maintenance cycle. **This candidate is not yet a verified Cloud freeze.**

## Security and ownership

Session separation is not authentication or an enterprise security boundary. The receiving IT team must approve hosting, network access, data transfers and downstream AI use. Dependencies have version ranges, not a lockfile. No software licence is declared; confirm ownership and redistribution permission.

## Other documentation

- [Handover acceptance](docs/handover_acceptance.md)
- [Development blueprint](docs/development_blueprint.md)
- [Deployment](docs/streamlit_cloud_deployment.md), [security](SECURITY.md), [contributing](CONTRIBUTING.md)
- [Architecture](docs/architecture.md), [operations](docs/operations.md), [source-tuning history](docs/source_tuning_status.md)

Supporting documents may contain historical workflows. This README describes the current operating procedure, entrypoint and export format.
