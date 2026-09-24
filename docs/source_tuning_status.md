# Source tuning checkpoint — 2026-09-24

This is not a certification that every source is healthy. Local/cloud IP behavior differs; inspect exported text.

| Source | Verified work / limitation |
| --- | --- |
| NUS Urban Planning / Urban Design | Narrow rendered-body route, course codes/units and curriculum tables inspected locally; adjacent menus excluded. Cloud browser flags/retrieval still need acceptance |
| Singapore Biodesign | Official fellowship discovery/body extraction improved; programme text inspected |
| A*STAR MedTech / SIMTech | Scoped research discovery/extraction; short/blocked pages remain distinguishable |
| SIT engineering short courses | Five course pages returned access-block notices in standard browser checks. No verified accessible same-course substitute; unchanged, not claimed recovered |
| Oxford / CUGE linked resources | Useful root text does not imply access to blocked linked courses/PDFs |

## SIT follow-up — 2026-09-24

- Permission-checked HTTP probe of the configured Grid-Connected Solar Photovoltaic Systems page: no readable HTML. The official course portal at `https://sitlearn.singaporetech.edu.sg/courseforindividuals/` also returned no readable HTML through the app's HTTP path.
- Normal Chromium checks of that portal and `https://www.singaporetech.edu.sg/energy-efficiency-technology-centre` both returned HTTP 403 with an Incapsula notice (six visible words), not course evidence. No challenge bypass attempted.
- Search indexing exposes relevant official course material, but this is not proof of crawler access. The centre/portal therefore cannot yet replace the five specific course sources. A historical 2024 Smart Grids partner brochure is not a verified current-course replacement.
- Decision: keep the existing URLs unchanged and record the unresolved access restriction. Do not enable Browser globally or accept access-block text to raise evidence counts.

Next: inspect the latest successful Cloud scan's `public_evidence.txt` for remaining source failures and content quality. Batch-46 local results predate the session-only and failure-isolation changes; do not use those old counts as current Cloud health. A fresh full scan is unnecessary if the current completed scan is still available to download.

This review changes no URLs or enablement flags. Each current session retains its own catalogue copy; new sessions start from the read-only master.
