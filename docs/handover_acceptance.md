# Handover acceptance record

Status: **handover cleanup in progress; final officer acceptance pending**.

Current development build: `pdf-prose-1`. Adds conservative within-page PDF prose joining. Source configuration and scan budgets are unchanged. Quick scan selection remains removed. Review fresh Cloud PDF excerpts against originals before acceptance; ambiguous layouts and tables are not reconstructed.

Current local validation: **459 tests passed**, including four PDF-block and extraction-path checks. No fresh live PDF corpus scan was run during this change; Cloud content-quality acceptance remains pending.

Previous local validation (cleanup build): **455 tests passed**. The first sandboxed run encountered six file-rename permission failures; rerunning with filesystem permissions passed the full suite.

Latest reviewed Cloud export: `fe07f21b096845d6a9a80c2f991c7a0a` — 229 cards from 74 of 106 organisations; card/status/log totals match and no provenance discrepancies were found. Both card files are below 300,000 characters. BCA retains all six named skill definitions; EPFL learning outcomes are no longer duplicated. These targeted checks do not certify every card or source. 32 organisations produced no cards; KIT coverage declined from the preceding run. Keep these gaps visible rather than claiming complete coverage.

Before handover: verify the new visible build, smoke-test scan/prepare/download and session isolation, and have the receiving officer review the government-assistant output. Preserve raw attempt logs: `last_error` can include bounded-discovery notices and is not, by itself, proof that an organisation failed.

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
