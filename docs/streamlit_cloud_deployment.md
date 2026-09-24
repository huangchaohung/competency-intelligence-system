# Private Streamlit Cloud deployment

Deploy the code repository, **not the original development workspace**. No database, framework, evidence exports, logs or secrets belong in Git. The active app is a public-evidence collector; government analysis is separate.

## Setup

1. Connect the reviewed repository/branch in Streamlit Community Cloud. Set entrypoint **`app.py`**. Existing `cloud_app.py` deployments remain supported through an alias to the same app; it is not a separate design.
2. Use Python 3.12 for the cloud trial and complete Linux acceptance below. Local Windows tests alone do not prove browser compatibility.
3. Set the following in the hosting secret settings (or `.streamlit/secrets.toml` only when testing locally):

   ```toml
   ADMIN_PASSWORD = "REPLACE-WITH-A-UNIQUE-RANDOM-SECRET-AT-LEAST-20-CHARACTERS"
   ```

   Never commit the real value. No OpenAI key is required. Missing/short admin secrets leave the app read-only.
4. Python dependencies install from `requirements.txt`; `packages.txt` requests Linux Chromium. Check build logs.
5. Restrict platform sharing to approved testers. The in-app admin password controls edits/scans, not viewer access to shared evidence. Do not expose the trial publicly.

The receiving team must verify available platform sharing controls and organisational approval. Official references: [deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies), [secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management), [sharing](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app).

## Acceptance after deployment

- Signed-out viewers must not see Source Configuration or the scan action. They may view/download the latest shared result.
- Sign in via Administrator access. Enable a small representative set, including one rendered source; validate/apply.
- Scan, inspect substantive evidence text and source health, download/parse the TXT.
- Opening Scan & Download alone must not prepare or start a download. Existing results require **Prepare TXT from this existing result**. A newly completed scan prepares once; the final browser download always needs a click.
- Try the small TXT under download troubleshooting from the actual government browser. If only the large file fails, record size and browser error for IT.
- In a second session confirm overlapping execution shows the busy message rather than another scan.
- Increase catalogue size only after checking memory and runtime. A full browser-heavy scan may exceed hosting resources.

## State and updates

Cloud state lives in `.cloud_runtime/`. The first startup copies only the public catalogue seed, never local history. Later repository catalogue updates do **not** overwrite edited runtime URLs. Update them through Source Configuration deliberately.

Schema 20 migrates obsolete source fields; cloud YAML migration makes a pre-migration YAML copy. This is not a database backup. Back up controlled installations before schema upgrades.

All users share the same latest result/catalogue. A file lock serializes initialization/page execution/scanning on one instance; other sessions can be busy throughout a scan. There is no background worker or distributed coordination.

Cloud filesystem storage is temporary. Restarts/redeployments can lose edits and evidence. Download archives promptly; five-batch retention is a maximum policy, not durability. Catalogue edits are not committed back to GitHub.

## Maintainer publication

Teams cloning GitHub can commit reviewed changes normally. In the original maintainer's separate working folder, `python scripts/sync_cloud.py` copies allowlisted files into `.cloud-deploy`; inspect its diff before commit/push. It does not push or delete files and is not a required setup step for other teams.

`python scripts/package_cloud.py` creates an optional code-only ZIP in `dist/`. The allowlist includes documentation/tests but excludes the historical README archive and operational data. A push is not proof of successful cloud rebuild: perform acceptance above.

For reliable production operation, replace temporary storage/shared passwords with approved durable storage, identity-based authorization, controlled egress and a background-job architecture.
