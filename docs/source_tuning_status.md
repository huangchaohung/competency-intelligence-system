# Source tuning checkpoint — 2026-09-24

## Ngee Ann engineering / SMU follow-up — 2026-09-28

- Ngee Ann engineering root is accessible locally. Scoped discovery follows only the nine direct full-time course/programme links in its actual listing, deduplicating card links and respecting robots and article caps. General site links are excluded.
- Course extraction retains about/overview/learning sections, not admissions, testimonials or video promotions. All nine linked pages returned 123–807 words locally. Eight diploma pages have empty server-rendered module accordions: evidence explicitly says some module details require interactive loading and were not retrieved. These are useful course overviews, NOT verified complete syllabuses.
- SMU Master of Sustainability remains empty through permission-checked HTTP even though the official page is indexed. No verified replacement or access workaround claimed; URL unchanged.
- Build `np-curriculum-1`. No master catalogue changes. Cloud acceptance remains pending; continue remaining empty-source review before a consolidated scan.

## ICE / HKUST zero-output follow-up — 2026-09-28

- Both configured official pages now return readable text through local permission-checked HTTP: ICE `/join-ice/attributes-for-professionally-qualified-membership` and HKUST `/students/sustainability-education`. This does not establish why the earlier Cloud scan failed or guarantee Cloud access.
- Added exact-page standalone routing, avoiding generic secondary navigation. ICE extraction retains the three attribute tabs (IEng, CEng, EngTech), excluding related event cards: 1,641 words locally. HKUST retains its education article: 1,374 words, including programme/credit and learning-outcome information; this is an overview, not every linked course syllabus.
- Missing content containers, insufficient text and off-resource redirects are rejected rather than treated as evidence. Robots restrictions remain enforced. No master URLs or enabled flags changed; the separate legacy ICE `/attributes` source remains unresolved.
- 254 tests passed. Build `structured-pages-1`; Cloud acceptance remains pending. Continue reviewing remaining zero-output sources before requesting a consolidated scan.

## Duplicate descriptions — 2026-09-28

- Latest supplied export contains three IEEE PES webinar video/slides pairs with identical public descriptions (three redundant records). Keep the first representative URL within a scan only when the webinar path matches after removing the slides suffix, organisation/query match, and whitespace-normalised text is identical.
- Different webinar IDs, different descriptions and other websites are not merged. These remain public landing descriptions, not downloaded videos/slides or full training materials. The duplicate guard resets for every scan.
- 252 tests passed, including workflow repeat-scan coverage. Runtime build `description-dedup-1`. No source URLs or enabled flags changed this round; next priority remains reviewing the 44 zero-output sources. A full scan is not yet needed solely for this cleanup.

## Catalogue cleanup — 2026-09-28

- Energy Institute's LMS yielded policy pages, test categories, staff training and bespoke training along with technical listings. The exact configured root now discovers only nine verified public technical category links; no admin/policy/test/staff categories. The original URL remains unchanged. These are course-title lists, not full syllabuses; sampled energy category remains a useful 43-word listing. The alternative public academy site's robots endpoint returned 403, so no replacement there was made.
- Four ISA IC32 product pages yielded only headings. Scoped ISA product extraction now rejects pages without substantive body text. Added official `https://programs.isa.org/ic32-cyber-training` as an enabled standalone catalogue source; live extraction returns 341 words with learning outcomes and course topics. Existing ISA certificate source retained. This is a public course description, not retrieved training materials.
- Runtime build catalogue-tuning-2. New sessions receive the new master source; active sessions require Restore default sources (which resets their source edits) or may add the ISA URL manually. No global short-text threshold was raised, preserving concise legitimate course lists.

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
