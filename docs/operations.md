# Session collector operations

## What persists

Only the master `config/sources.yaml` is a maintained application asset. Back it up with code/version control. User catalogue copies, uploaded CSVs, scan evidence and prepared TXT bytes stay in session RAM; there is no recovery guarantee. Users must download their evidence and may export their own source CSV for later reuse.

The active workspace does not instantiate the disk OperationalLogger. Standard process error logs may still include URLs/diagnostics and hosting may retain them; these are not an evidence archive. Do not claim that hosting keeps no logs. Restrict access and sanitize before sharing.

Old database/log directories are not used or automatically deleted. They may contain sensitive legacy information; removal requires a separate reviewed operation. Legacy disk-maintenance scripts must not be used to manage current user sessions.

## Troubleshooting

The page shows an App build identifier (`scan-isolation-2` for the session-runtime refresh fix). If a reported issue contradicts the current code, record that identifier and confirm the hosting branch/rebuild. Idle sessions refresh outdated workflow/job objects without removing evidence or catalogue edits; active scans are not replaced. Unexpected worker failures now log a traceback with current source/progress to the hosting console. Do not diagnose from the final exception message alone.

| Symptom | Action |
| --- | --- |
| Zero evidence | Inspect error, robots policy and extracted text; count alone is not quality |
| 403/login/challenge | Record restriction and select a permitted official alternative; no bypass |
| Cookie/menu text | Fixture-backed body extraction tuning, not larger page limits alone |
| Browser timeout | Check Chromium installation, hosting resources and site availability |
| Evidence missing | New session/restart/Start fresh or a new scan discards previous results; use downloaded archive |
| Master changes not visible | Restore default sources or Start fresh; active edits are intentionally isolated |
| Invalid upload | Use UTF-8 CSV template with Name, Organisation, Discovery URL; validate before apply |
| Download blocked | Try small TXT, record size/browser error, involve IT; do not bypass security controls |

## Networking and release

Server needs approved outbound HTTPS and browser/package dependencies. No OpenAI access is needed. For Zscaler/proxies ask IT for approved proxy/CA and allowlist configuration; do not disable TLS verification or copy cookies. Chromium and Requests may need different enterprise settings.

Run regression tests and two-session acceptance, inspect real text, then test download on the target browser. Review staged Git files for private data. Test concurrent memory/browser load before expanding access. Platform authentication, rate limits and network egress must be set by the receiving team.
