# Private Streamlit Community Cloud trial

## Current UI — 2026-09-24 (supersedes History references below)

Use **Scan & Download**. Administrators can scan; viewers can download the latest shared result. The TXT is automatically prepared, without a separate history/batch selector. Review source health and previews below it. Local history is preserved in storage but hidden from navigation. Source tuning is paused at the Singapore Biodesign checkpoint.

Update `app.py`, `cloud_app.py` and `src/dashboard/collector.py` in the deployed GitHub repository (or use the new clean deployment ZIP). This does not automatically change the cloud runtime source catalogue. After deployment, open Scan & Download and test the evidence TXT. Under Download troubleshooting, try the small TXT. Record the browser error, file size and whether the small test works if the real download still fails. Government filtering/proxy restrictions require IT assistance; this change does not bypass them. The app-side rerun/memory issues are addressed, but the original cloud failure has not been reproduced on the government laptop.

This deployment is the public evidence collector only. Do not upload government competency frameworks, credentials, confidential data, or local databases. Government analysis remains in the approved government environment.

## Deploy step by step

1. Extract the prepared `dist/streamlit-cloud-*.zip` into an empty folder. Review `config/sources.yaml` for public-only metadata. The archive excludes your existing database, logs, secrets, frameworks and scan exports.
2. Create a **private GitHub repository** and upload the extracted files, preserving folders. Upload the files, not the ZIP. `cloud_app.py` must be at the repository root.
3. Sign in at https://share.streamlit.io and choose **Create app**. Select the repository and branch; set the entrypoint to **cloud_app.py**, not app.py.
4. In Advanced settings select Python **3.12**. In Secrets add the following, replacing the example with a unique randomly generated password of at least 20 characters:

   ```toml
   ADMIN_PASSWORD = "REPLACE-WITH-A-LONG-RANDOM-SECRET"
   ```

   No OpenAI API key is needed. Never put the password in GitHub. Missing/short secrets leave the app read-only.
5. Deploy. Python packages install from requirements.txt and Linux Chromium from packages.txt. Check build logs for installation errors. The Windows test suite is not proof of Linux/browser compatibility: complete the checks below before inviting users.
6. Verify Sharing is **Only specific people can view this app** and invite your testers. The in-app administrator password only protects scan/configuration actions; it does not replace private app access. Do not expose this trial publicly.
7. Open Administrator access in the sidebar and sign in to edit sources or run scans. Other viewers can browse and download the shared public scan history.

## First cloud acceptance check

- Sign out: Source Configuration and Run Scan must disappear.
- Sign in and enable only 3–5 representative sources initially, including a browser-rendered source. Apply validated changes.
- Run a small scan, inspect substantive text and source health, and download the evidence TXT.
- In another browser session, confirm an overlapping operation displays the busy message rather than starting a second scan.
- Confirm History & Export works after completion. Gradually increase the source set only after checking runtime and memory. A full catalogue/browser scan may exceed Community Cloud resources.

## Important operating limits

- **Shared trial, not isolated user workspaces:** all viewers see the same history and all administrators edit the same catalogue.
- A nonblocking file lock serializes page execution, startup synchronization and scans on this single app instance. While a scan runs, other sessions may only see a busy message. This is not a distributed-worker design.
- Cloud state lives in `.cloud_runtime/`, separate from local data. Only the public source catalogue is copied on first startup. Existing local history is intentionally not deployed.
- Community Cloud local storage is **not durable**. Restarts/redeployments can lose scans and catalogue edits. Download important results immediately. Catalogue changes are not committed back to GitHub. Retention of five batches is a maximum policy, not a backup guarantee.
- Source sites may reject cloud IP addresses even when local crawling works. Robots/access restrictions remain respected. System Chromium is used on Linux; compatibility must be confirmed in the cloud smoke test. Local Windows uses the existing Playwright browser installation.
- Dependency ranges are bounded, not a reproducible lockfile. Review dependency upgrades before a wider release.
- For reliable long-term shared use, add durable storage, identity-based authorization and a background job queue. This trial does not certify government hosting/security approval.

## Local use and rebuilding

Local `streamlit run app.py` is unchanged. To test the cloud entrypoint locally, install `pip install -r requirements.txt`, configure `.streamlit/secrets.toml`, then run `streamlit run cloud_app.py`. It starts separate empty cloud history. Never commit secrets.toml.

Rebuild the clean ZIP with `python scripts/package_cloud.py`. Review the archive before uploading. Do not upload the entire working directory.

Official references: [deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies), [secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management), [sharing](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app), [storage limitations](https://docs.streamlit.io/develop/concepts/connections/connecting-to-data).
