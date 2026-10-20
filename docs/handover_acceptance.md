# Handover acceptance record

Status: **candidate; awaiting officer Cloud acceptance**.

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

Record the final scan identifier, downloaded filenames, observed errors, ten-card review findings, session-isolation check and receiving officer walkthrough here.

## Known limitations to carry forward

- Restricted/robots-blocked sources may remain unavailable.
- Deterministic filters can accept weak content or miss useful pages.
- Excerpts and PDF extraction do not preserve complete inventories or table relationships.
- Session results disappear; users must download.
- Cloud hosting/security approval, dependency locking and software ownership/licensing need receiving-team decisions.

## Freeze decision

If README acceptance checks pass, record and tag the accepted commit. Do not delay solely to improve source counts. If a blocking defect remains, fix that defect, rerun relevant tests and repeat the affected acceptance check. Defer other enhancements.
