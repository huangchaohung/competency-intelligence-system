# Operations and troubleshooting

## Acceptance

Run tests, scan a small representative set, inspect body text and download/parse the TXT. Test the actual government browser/network separately. Never upload an internal framework to the collector.

## Network

The server needs outbound HTTPS to approved configured hosts and permitted redirects/assets. Package/browser installation needs separate access. Users need access to the Streamlit site and download route. No OpenAI key/endpoint is needed by current entrypoints.

For Zscaler/proxy environments, obtain approved proxy settings, enterprise CA and host allowlists from IT. Requests supports standard proxy/CA environment configuration; Chromium may need separate enterprise configuration. Do not disable TLS verification or copy login cookies into the crawler. Server retrieval success does not prove a user's download is permitted.

## Logs

Inspect `logs/operational_audit.jsonl` locally or `.cloud_runtime/logs/operational_audit.jsonl` in cloud mode. Correlate timestamps and batch/source IDs: scan/source start/completion, discovery counts and errors. Current collector events do not include active AI calls.

Rotation threshold is approximately 5 MB with three backups; one large event can exceed the threshold. Secret-pattern redaction is not DLP. Restrict log access through hosting/filesystem controls and sanitize before sharing. The app does not implement an engineer-only log viewer or filesystem authorization.

| Symptom | Action |
| --- | --- |
| Zero evidence | Inspect error, robots and body text; direct resources may need a dedicated route |
| 403/challenge/login | Record restriction; use a permitted official equivalent or manually disable. No access bypass |
| Cookie/menu text | Add fixture-backed, narrowly scoped body extraction; counts are not proof of recovery |
| Browser timeout | Check installed Chromium, resources and site availability; avoid unbounded retries |
| Catalogue unchanged after Git push | Runtime preserves edits; update Source Configuration, not forced state deletion |
| Busy message | Another session holds the single-instance lock; inspect logs if it never completes |
| Download failure | Prepare existing result explicitly, test small TXT, record browser error and size; involve IT for proxy/file limits |
| Missing old evidence | Retention or cloud state loss; use previously downloaded archive |
| Schema error | Stop, back up, verify deployed code/migrations; do not manually change migration records |

## Backup/restore

Stop the local app and ensure no process has the database open before copying the database, any remaining SQLite sidecars and matching catalogue into restricted storage outside Git. A properly managed SQLite online backup is an alternative; casually copying a live database is not.

To restore: stop the app, preserve current state, restore matched catalogue/database, start compatible code and validate migrations/counts/small scan. Code rollback does not reverse schema migrations. Cloud trial storage is not a durable backup target.

**Legacy destructive switch:** leave `RESET_HISTORY_ON_START` unset and do not create `data/reset_history.flag`. Reset code can delete history; use only a separately reviewed maintenance procedure.

## Release checklist

- Run tests in the deployment checkout, not only the original workspace.
- Inspect staged files for secrets, private paths, logs, databases and real exports.
- Back up state; record commit and migration version.
- Deploy `cloud_app.py`; verify viewer/admin separation and Linux rendered retrieval.
- Verify real TXT download on the target user's device; a Git push alone is not cloud acceptance.
- Record unresolved sources rather than claiming comprehensive coverage.

Production requires durable storage, identity-based access, egress policy, monitoring, quotas and background jobs designed by the receiving team.
