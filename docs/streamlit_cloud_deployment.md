# Streamlit Cloud deployment — session workspaces

1. Deploy the reviewed GitHub repository/branch using **app.py**. cloud_app.py is only a compatibility alias.
2. Install from requirements.txt and packages.txt (Linux Chromium). Python 3.12 is the cloud trial target; local Windows tests are not Linux/browser acceptance.
3. No ADMIN_PASSWORD or OpenAI key is needed. Old ADMIN_PASSWORD secrets are unused and may be removed.
4. Restrict platform sharing to approved users. Removing the in-app administrator panel does not mean the crawler is hardened for anonymous internet traffic. See SECURITY.md.

## State

Every new Streamlit session gets an isolated memory database and a copy of master sources. Uploaded CSVs, temporary edits, evidence and prepared TXT bytes are not written to the master or runtime files. The UI never loads existing disk history. A Git update to the master takes effect in newly started workspaces or after Restore default sources, not by overwriting active edits.

There is no batch history or shared latest scan. A new scan replaces only that session's old result. Brief reconnections may resume state; Start fresh explicitly resets. Do not promise instant disposal at browser-close or secure memory erasure. Download before leaving.

## Acceptance

- Open two separate browser sessions: both should start without evidence and without an admin panel.
- Edit/upload sources in one. Confirm the other session and master YAML do not change.
- Validate CSV before applying. Invalid input must not replace the current list. Test Restore default sources.
- Run a small scan including a rendered source; inspect actual body text and health.
- Entering Scan & Download and finishing a scan must not automatically prepare TXT. Click Prepare evidence TXT, then Download evidence TXT.
- Confirm the other session has no access to those results. Start fresh must show defaults/no evidence.
- Confirm actual government-browser download. Test small TXT if the full file fails and report file size/error to IT.

Each active session consumes server RAM and concurrent scans multiply browser/network load. This remains an approved-user trial, without a global queue, per-user quotas or distributed jobs. Load-test and enforce hosting/network limits before wider use.

## Publication

Receiving teams can use normal Git workflows. The original maintainer's scripts/sync_cloud.py copies an explicit allowlist into a separate checkout; it does not push/delete. scripts/package_cloud.py creates an optional code-only ZIP. Never upload databases, evidence exports, logs or secrets. Confirm cloud rebuild and acceptance after pushing.
