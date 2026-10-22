# Handover acceptance record

## Current handover candidate

- Build: **handover-final-1**
- Local regression validation: **468 tests passed** on 2026-10-22. Receiving environment and final Cloud smoke test remain pending.
- Status: **source tuning frozen at the user's request; receiving-officer acceptance pending**
- Latest reviewed Cloud scan: **544829126fe6** — 231 cards from 75 of 106 organisations.
- Card/status/log totals match; zero provenance discrepancies.
- Card parts: 299,772 and 198,690 characters, both below 300,000.
- Final code change: sentence-level administrative filtering and standalone honorific removal. This final change still needs a deployment smoke test; the reviewed scan predates it.
- Source configuration and scan budgets are unchanged. Historical records and compatibility modules are retained.

## Known limitations to explain

- 31 organisations produced no cards in the reviewed scan. Missing cards do not prove missing or obsolete competencies.
- PDFs can retain fragments, broken words and ambiguous table/column order despite safeguards. Check original documents.
- Catalogue excerpts can combine multiple courses; do not attribute all statements to a single programme.
- Some promotional or biographical text remains. Healthy means cards were collected, not content certification.
- Discovery and character budgets deliberately limit coverage. A last_error value can be a limit notice rather than a failed fetch.
- The institution list is configured coverage, not a verified current top-50 university ranking.
- Sessions are temporary; download all matching TXT files before leaving. No internal frameworks belong in this public app.

## Receiving-officer checklist

- [ ] Confirm Cloud is configured for this repository, main branch, app.py, and shows handover-final-1.
- [ ] Confirm source edits affect only the current session, not the master catalogue or another session.
- [ ] Confirm scan progress, source-error isolation and explicit prepare/download controls.
- [ ] Download all parts plus status/log TXT files with the same identifier; review totals and representative cards.
- [ ] Review government-assistant analysis against original source URLs, especially PDFs and mixed-course catalogues.
- [ ] Confirm repository/Cloud ownership and access with the receiving team; no credentials in handover files.
- [ ] Run python -m pytest in the receiving environment and record the result.
- [ ] Record accepted Git commit, accepting officer and date below.

Accepted Git commit: pending  
Acceptance date / accepting officer: pending

No further tuning is scheduled. Resume only through a new scoped request. The sections below are historical development records, not current acceptance results.

## Historical acceptance baseline (not the current build)

Build: `handover-rc-1`

Local validation: 446 tests passed on the final full run; 16 deployment-copy checks passed. An earlier full run had one three-second Streamlit test timeout that passed on retry. Cloud acceptance is still pending.

Accepted Git commit: pending

Acceptance date / accepting officer: pending

## Baseline

Last reviewed scan `afe358d3f3df42d884b2acccb1ca6c8b` produced 242 cards across 75 of 106 organisations. Totals and provenance matched. Coverage is incomplete, and some cards are promotional. This is a baseline, not a target or a quality certification.

## Candidate scope

- Preserve a configured seed attempt before ranked candidates.
- Exclude restricted/login/enquiry routes and narrow training-promotion cases.
- Keep source isolation, session-only storage, TXT budgets and provenance validation.
- Consolidate current documentation; no new platform features.

## Acceptance evidence

### Export review: c930a8397e2a4e608bf35a91263226fe

- Received two card parts, organisation status and URL log. All four share the identifier.
- 247 cards across 76 represented organisations; 106 organisation-status rows, including 30 with no cards.
- Status total and URL-log total both equal 247. Every card matches organisation, source ID and resolved/requested URL in the productive log entries.
- Evidence families: 47 government-agency, 124 higher-learning, 76 professional-body cards; 31 PDF URLs.
- Previous reviewed scan: 242 cards/75 organisations. Increased counts are not a quality certification.

Ten-card targeted content review (not a random sample or whole-corpus validation):

| Card | Finding |
| --- | --- |
| S13-3 BCA | Useful named skill definitions, including Computational Design and Smart Facilities Management |
| S23-1 CSA OTCCF | Useful framework purpose/gap context; not a full competency list |
| S34-1 UK-SPEC | Useful professional competence areas |
| S111-2 TUM | Useful named electrical-engineering modules; PDF columns imperfect |
| S120-1 Waterloo | Course names retained; do not infer attribute mappings from flattened matrix |
| S18-2 Berkeley | Actual electrochemistry syllabus despite misleading PDF metadata title; excerpt is fragmented |
| S30-1 EPFL | Mostly prerequisites/readings rather than learning outcomes |
| S20-1 CAAS | Product certification, not direct personnel competency evidence |
| S161-2 TU Delft | Support application form, not competency evidence |
| S118-1 URA | Land-sales disqualification policy, not personnel competency evidence |

Recommendation: freeze as an **officer-reviewed collection prototype**, not an unattended competency-analysis-ready corpus. Carry these quality limitations forward. No further broad source-tuning cycle is required before handover if the receiving officer accepts manual review.

The files demonstrate successful export, not deployment build identity, session isolation, navigation behaviour or receiving-officer acceptance. Those UI/operational checks remain pending confirmation. No release tag or accepted commit has been declared.

Record the final scan identifier, downloaded filenames, observed errors, ten-card review findings, session-isolation check and receiving officer walkthrough here.

## Known limitations to carry forward

- Restricted/robots-blocked sources may remain unavailable.
- Deterministic filters can accept weak content or miss useful pages.
- Excerpts and PDF extraction do not preserve complete inventories or table relationships.
- Session results disappear; users must download.
- Cloud hosting/security approval, dependency locking and software ownership/licensing need receiving-team decisions.

## Freeze decision

If README acceptance checks pass, record and tag the accepted commit. Do not delay solely to improve source counts. If a blocking defect remains, fix that defect, rerun relevant tests and repeat the affected acceptance check. Defer other enhancements.
