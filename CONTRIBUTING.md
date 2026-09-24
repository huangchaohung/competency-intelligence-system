# Development

Install `requirements-dev.txt`, then run `python -m pytest`. Tests use temporary state/fakes; they do not establish live-site availability, cloud IP access or government network acceptance.

## Source tuning

1. Preserve organisation and intended course/framework function; prefer official public pages/APIs.
2. Verify with the app's retrieval path. Search-engine visibility does not establish crawler access.
3. Inspect course names, learning outcomes and substantive text. Reject navigation, advertisements and challenges; do not judge by counts alone.
4. Add synthetic fixture/mocked response tests. Do not commit entire copyrighted pages or actual evidence exports.
5. Scope selectors/routes narrowly, run tests and a bounded live probe, then a small UI scan.
6. Record unresolved access restrictions. Respect robots, permissions and site terms; do not replace current courses silently with old brochures.

Do not reintroduce AI fallback crawling or internal-framework inputs into public entrypoints. Browser discovery does not guarantee rendered extraction everywhere.

## Publication

Receiving teams can use ordinary Git branches/reviews directly in their clone. `scripts/package_cloud.py` builds an allowlisted code-only ZIP. The original maintainer's `scripts/sync_cloud.py` copies into a separate checkout and is hardcoded to this repository; it does not push/delete and is not needed for normal Git development.

`scripts/apply_source_health_stage.py` is a **mutating maintenance utility**, included for compatibility/tests. It updates source enablement from a CSV in YAML and SQLite; it is not run at startup. Review and back up before invoking it.

Keep documentation current, label retired features legacy, and test migrations with temporary databases. Before release run `git diff --check`, tests and deployment acceptance. Never stage the original working directory indiscriminately.
