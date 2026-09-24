# Source tuning checkpoint — 2026-09-24

## Latest Cloud export review and NParks correction

- Supplied public_evidence.txt: 236 configured sources, 1,611 records / 131 organisations; count matches completion manifest. 107 Error, 65 Low evidence, 64 Healthy. Of Error sources, 63 produced some evidence and 44 produced zero. Error status does not mean all evidence from that source was lost.
- Checked actual text, not only counts: NParks included recreation/navigation and repeated anchor variants; IEEE resource descriptions and some university pages repeat text across distinct URLs. Very short catalogue records also need further review. No matches for the sampled common access-challenge markers were found, which is not a comprehensive quality certification.
- NParks routes now scope discovery to research-programme children or biodiversity-resource children/PDFs; City in Nature is standalone. Body extraction uses the observed .main-body container, including accordion text, excluding the header/footer and menus. Research seed type corrected from CATALOGUE to RESEARCH. URLs/enabled flags unchanged.
- Live check: research root 207 words, sampled biosurveillance page 584; strategy 898; biodiversity overview 879. Candidate counts 6 / 1 / 12 respectively; those are not validated full-scan evidence counts. One sampled PDF exceeded the existing 2 MB retrieval limit and was skipped; limit unchanged.
- 245 tests passed. Runtime build nparks-tuning-1 refreshes idle scanner objects. Existing sessions keep their own source-type edits; Restore default sources loads the corrected research type but also resets temporary catalogue edits.
- Next review short ISA/Energy Institute catalogue items, remaining duplicated resource descriptions and the 44 empty sources. Do not disable 107 sources merely because a partial page failure gives Error status.

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
