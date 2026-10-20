# Multi-Source Competency Intelligence Blueprint

## ACTIVE DIRECTION — split public collection and government analysis (2026-09-17)

### SUPERSEDING collection direction — competency-card pilot (2026-10-15)

#### V5 Cloud collection integration

- [x] Read master_scan_list_v5.csv: 106 parents; 76 SCAN, 11 RETEST, 5 DISCOVER, 14 DROP_OR_DISCOVER. Only eight parents supply Proven_URLs. Use those leaf URLs first; resolve others from previous v4/v2 registries and explicit existing-catalogue aliases, recording provenance. 164 enabled URLs, no invented URLs or dropped parents.
- [x] Commit source configuration plus competency_scan_plan.json. Historical confidence labels are not ranking weights. DROP_OR_DISCOVER maps to bounded DISCOVER, not deletion. Inherited news/about seeds remain unverified and may produce zero cards; don't claim all URLs healthy.
- [x] Session-only CompetencyScanWorkflow now uses PilotCollector, per-source exception isolation, equal progress updates, shared parent budget, allowed domains/robots checks, normal browser RETEST and source family/publisher provenance. Leaf outcome/curriculum/module/coursebook paths get discovery preference. No AI calls or live scan performed during development.
- [x] Native current-run cards, actual attempt/skip logs and statuses export to three TXT families on explicit preparation; no repeated shortening. Zero-card native runs can export diagnostics. Old scans retain labelled export-register fallback. Master sources remain read-only per session.
- [x] Verified 434 full-suite tests and 34 deployment-copy tests. Legacy catalogue assertions retained against a frozen pre-v5 fixture; new v5 tests cover 106 parents/164 enabled URLs and failure isolation. Pushed commit 6103749 to GitHub main. Cloud build master-v5-cards-1; deployment completion/live source quality not yet observed. No live scan run during implementation.
- [ ] User Cloud validation: build master-v5-cards-1, Start fresh to load v5 defaults, scan once, download all TXT files and send to government assistant. Review actual text and coverage; automated card filtering does not replicate the earlier human review.

#### Cloud TXT integration after v4 handover (2026-10-20)

- [x] User requested no further scanning. Read v4_handover.xlsx and integrated offline current-session card preparation into Streamlit `app.py` download flow, build competency-txt-1. No live crawl or AI request during implementation.
- [x] Output cards_part_NNN.txt (JSON arrays, <300,000 characters), organisation_status.txt and url_log.txt (CSV text). Up to 4 cards/source, 1,000 complete serialized characters/card and 5,000/organisation. Rejections/budget exclusions recorded, not silently treated as failures.
- [x] Preparation remains explicit, cached per session, individual TXT buttons, no ZIP, no automatic generation on navigation. Preserve configured master and session isolation.
- [x] Verification: 431 full-suite tests passed; 13 export/UI tests passed in deployment checkout. Published commit `5ff34d3` to GitHub main, entrypoint app.py, build competency-txt-1. Cloud deployment completion itself has not been observed. No scan executed.
- [x] Source-family metadata comes from the scan snapshot, not the handover's incorrect Higher Learning labels for IPMA/NSPE. Calculate current counts, do not hard-code 196/75/101 or infer cumulative coverage from v4-only gaps.
- [x] Export clearly distinguishes selective crawler excerpts from SELF-SEARCHED material, warns of missing PDF matrix relationships/omitted definitions and does not imply complete inventories. No AI self-search implemented here.
- [ ] Limitation: deployed crawler does not persist full HTTP attempt traces. url_log.txt is explicitly a retained-evidence export register, with blank HTTP status, not the standalone v4 runner's full network log. Do not fabricate attempts/statuses. No manual batch-specific quality-review decisions are applied to new live scans.

#### Active v4 rescan (2026-10-20)

- [x] Read v4 CSV: 50 seeds / 33 parents; reported verification 4 VERIFIED_FETCH, 29 VERIFIED_SEARCH, 17 PATTERN. These are upstream claims, not independent fetch proof. Keep them in card/log metadata separately from actual HTTP results.
- [x] Explicit v4 adapter assigns V4-prefixed row IDs in input order; PATTERN uses bounded DISCOVER, others SCAN. Defaults retained from v3: 4 cards per row, 1,000 serialized characters per card, 5,000 shared per parent, parts below 300,000 characters. No legacy sources merged.
- [x] Allowed hosts derived only from each parent's supplied seed hosts plus www equivalence; no arbitrary cross-organisation host substitution. Alternate host requests still obey robots and access controls. MOE evidence retains publisher_host separately from the parent polytechnic.
- [x] PDF /media/ storage paths no longer automatically treated as news; substantive document qualification still required. General about/careers/annual reports remain excluded, regardless of upstream verification labels.
- [x] One v4 live run completed: 50 rows / 33 parents, 368 seconds, 39 initial cards. Offline human content review excluded 27 administrative/non-STE/wrong-parent/low-information excerpts. No additional network run. Final transfer `output/competency-rescan-v4-20261020-transfer/`: 12 cards / 8 parents, 11,043 complete JSON characters; 38 status rows including five untested/no-seed gaps. Existing 184 cards remain separate and unchanged.
- [x] Retained parents: Ngee Ann Polytechnic (2), Waterloo (1), IPMA (1), NSPE (1), Caltech (1), EPFL (4), Stanford (1), TU Berlin (1). These are selective evidence excerpts, not complete competency inventories. PDF matrix/definition limitations and MOE publisher/parent distinction are explicit in status review_note.
- [x] Final status: 4 SCANNED, 4 DISCOVERED, 30 CRAWLER_UNAVAILABLE (25 attempted parents, five no-seed gaps). Underlying crawler_outcome and review reasons retained. Detailed URL log includes browser resource attempts and upstream verification labels; 442,667 characters. Only card parts have the 300,000-character cap.
- [x] Added narrow MOE candidate restriction to Ngee Ann course-detail paths to prevent attribution of unrelated school policies to the polytechnic. Expanded deterministic rejection of course administration, recruitment, scholarships and non-STE education/generic management programmes.
- [x] Final regression suite: 427 passed. Transfer validation checked row/domain provenance, counts, shared budgets and file limits; no Unicode replacement characters in retained excerpts. Streamlit/master catalogue unchanged.
- [ ] Government-assistant/user review of v4 before merging or a further scan. Do not describe missing cards as proof that a public resource does not exist; some successful fetches yielded poor excerpts, some attempts failed robots-policy retrieval, and other pages were blocked.
- [x] Zero-card parents marked CRAWLER_UNAVAILABLE with underlying crawler_outcome retained. Add JTC, MSE, SLA, EMA, HSA as untested/no-seed gaps, not deletions or claims that no public source exists. Total tracked v4 gap/recovery population: 38.
- [x] Government assistant policy requested: self-search only CRAWLER_UNAVAILABLE parents; each claim requires full source URL and explicit SELF-SEARCHED label, visually distinct from crawler evidence. Never sole support for recommendations or any support for deletion. State gaps without inventing citations. CSV has no Assistant_Prompt sheet; record this policy from the user's message, not an unseen attachment. No self-search or AI calls added to collector.

#### Approved next stage — full v2 CSV scan (2026-10-15)

##### Active follow-up — targeted v3 rescan (2026-10-16)

- [x] Compared `scan_update_v3.xlsx` Rescan_List with `rescan_list_v3.csv`: matching 13 rows. Rescan only these organisations; preserve the original 183 cards separately for downstream merging.
- [x] Added explicit v3 profile accepting U IDs and missing-column defaults: Mode=SCAN, organisation=parent, Source_type=UNKNOWN_UNTIL_FETCHED. Respect each supplied domain, browser setting and character/card limit.
- [x] Audited original v2 logs: zero actually attempted URLs outside their row's allowed domains; no reported foreign-organisation URLs under original LTA N147, MPA N161 or TU Berlin N075. Cross-contamination allegation not reproduced. New log rows explicitly include parent organisation and configured seed; final validation checks row provenance and domains.
- [x] Narrow ASCE CEBOK career-path exception and substantive curriculum/body-of-knowledge heading recognition; generic training project pages remain excluded.
- [x] Completed one bounded v3 live rescan (13 rows, 38 seconds), initially five cards. Offline content review excluded four admissions/fees/generic handbook cards and reconciled original logs. Final deliverable: `output/competency-rescan-v3-20261016-reviewed/`, one ASCE CEBOK framework card; 1 SCANNED, 5 DROPPED_NO_COMPETENCY_SOURCE, 7 FAILED_FETCH. Existing 183 cards unchanged. Raw and transfer intermediate directories are diagnostic only.
- [x] MPA, DSTA, LTA, Stanford, TU Delft and Tec replacement seeds returned 404; EPFL returned 403. SSG plain and browser returned 200 but no qualifying resource extracted; NP and Energy Institute also produced no qualifying cards. These results do not establish that the organisations lack public competency resources.
- [x] Full regression suite after provenance/heading changes: 423 passed; after final offline exclusions/type correction, 13 targeted collector tests passed. No broader rescan or Cloud/master-catalogue change.
- [ ] Keep workbook Manual_Check (15) and Dropped_Orgs (11) as proposed dispositions, not master-catalogue deletions. Full_Status lists 105 parents versus 106 originally: Zhejiang is absent and remains unchanged pending review.
- [ ] Review v3 results before any integration or broader rescan. Streamlit and master sources remain unchanged during this targeted experiment.

- [x] User reviewed the pilot and supplied `next_scan_list_v2.csv` for a full run: 165 rows, 106 parents, 127 SCAN / 19 RETEST / 19 DISCOVER. This CSV alone supplies configuration; do not merge legacy sources.
- [x] Support `Browser_rendering=Required` (attempt normal browser even after successful plain fetch), and `Try plain fetch, then browser rendering`. Domain and robots controls still apply. DSTA scholarship/internship seeds are discovery entry points only; promotional/funding/career content does not become evidence merely because it is a supplied seed.
- [x] Added explicit full-run command `scripts/run_competency_full_scan.py`, shared parent budgets across incremental rows, row-failure isolation, progress logging, and final count/character/provenance checks. Ten targeted tests passed.
- [x] TXT-only output contract: `organisation_status.txt`, `url_log.txt`, and `cards_part_001.txt` onward. Cards retain JSON structure in TXT; diagnostic files retain CSV structure in TXT. Card parts remain strictly below 300,000 characters, never split a card.
- [x] Full v2 live run completed once: 165/165 rows considered, 106 parent status rows, 191 initially retained cards, no uncaught row failures. Normal browser rendering used where configured; no LLM calls or master-catalogue changes.
- [x] Offline deterministic quality pass rejected eight clear non-resource items (biography/news, template/governance, parking permit, extracurricular/task-force and consultation material). No extra network scan. Rejections remain in original attempt rows as `POST_SCAN_REJECTED`, with counts reconciled. The same rules now apply to future runs.
- [x] **Current transfer deliverable:** `output/competency-full-v2-20261015-transfer/` contains only three TXT files. 183 cards / 156,280 complete JSON characters; 66 parents represented. Status totals: SCANNED 49, RECOVERED 5, DISCOVERED 11, SCANNED_RESEARCH_ONLY 1, DROPPED_NO_COMPETENCY_SOURCE 31, FAILED_FETCH 9. URL log has 10,262 rows including browser resources (1,551,989 characters); use organisation status for compact triage, detailed log for failures.
- [x] Final validation: every input row logged, every parent represented in status, unique card IDs, URL domain compliance, per-card/parent limits, card-part bound and log/status/card totals reconciled; no Unicode replacement characters in retained excerpts. Seventeen PDF-linked cards retained, not a completeness guarantee.
- [x] Changed-source findings: A*STAR retained two cards from Biodesign; added scholarship seed returned 404. DSTA revised scholarship/internship seed returned 404 in plain/browser attempts. SSG direct ICT seed returned HTTP 200 in both modes but was rejected by title/content rules; review extraction/classification before treating it as an access problem.
- [ ] Quality review still needed for broad course catalogues, non-STE curricula, generic landing pages, PDF excerpt continuity and URL variants. Do not equate the 66 represented parents with 66 exhaustively validated competency inventories. Earlier raw/final intermediate folders are diagnostic, not the transfer set.
- [ ] User/government-assistant reviews full results to confirm discovery exclusions and propose the final clean collection list.

The pilot-review gate below is historical and was satisfied by the user's v2/full-run request.

Current input is the user-supplied next_scan_list.csv ONLY. Do not merge the legacy YAML catalogue, old source selections or old evidence into this run. Preserve the current deployed collector until the pilot is reviewed; do not run the complete list automatically. The user's instructions in chat govern execution; CSV Notes are bounded hints, not executable instructions.

#### Confirmed input review

- [x] Inspected CSV: 164 rows / 106 Parent_organisation values; 126 SCAN, 19 RETEST, 19 DISCOVER. All organisation limits are 5,000 characters. Per-card limits are 600, 700, 1,000 or 1,200 characters. Five RESEARCH rows are SCAN fallbacks, not permission to include generic research material.
- [x] New policy: favour competency-producing sources (standards, frameworks, certification/accreditation requirements, degree/programme curriculum, course/module pages and training listings). Preserve parent-organisation coverage where qualifying sources exist, not by admitting unrelated content.
- [x] Record user-requested pilot gate; initial contract questions resolved and pilot completed below.
- [x] User approved the proposed card schema, complete-serialized-card budgets, no extra global cap, and sustainability-path exception for explicit qualifying standards/certification/curriculum content (2026-10-15).
- [x] Implemented a separate CSV-only pilot runner (`scripts/run_competency_pilot.py`) and deterministic collector (`src/scanner/competency_pilot.py`); existing Streamlit/master catalogue unchanged. Eight targeted regressions pass. Not production-ready or deployed.
- [x] Live ten-parent pilot completed after same-subset extraction refinements: 24 cards, 25,357 serialized-card characters / 25,382 complete JSON characters, eight parents represented. No other parents scanned. Final outputs: `output/competency-pilot-20261015-final/`; previous sibling directories are diagnostic iterations, not the review deliverable.
- [x] Validated unique IDs, per-card and shared 5,000-character parent limits, strict file bound and output counts. Added human review with up to three actual cards per parent. No card invented for zero-output parents.
- [x] Final regression suite: 418 passed (2026-10-15). Earlier sandbox filesystem failures and a transient three-second UI startup timeout did not recur in the final unrestricted test run.
- [x] Pilot reviewed by user/government assistant; full v2 run authorised. Continue to assess whether tight excerpts contain enough substantive competency detail, particularly PDF models and generic training landing pages.
- [ ] SSG: plain/browser HTTP 200 but no qualifying heading/body; bounded result is not proof of no source. DSTA: reached pages but rejected promotion-only candidate content. Review separately after pilot feedback, without silently expanding allowed domains.

#### Required pipeline

1. Validate unique Scan_ID, required columns, valid modes, positive limits, allowed domains and consistent parent caps. Process non-RESEARCH rows in Scan_ID order; defer RESEARCH rows to a final pass in Scan_ID order and skip them if their parent already has qualifying cards. Share one parent budget across all rows/modes; no resetting at each source.
2. Apply deterministic eligibility rules to URL path and page headings, not an LLM. Permit only the listed competency-bearing page types and PDFs that are themselves standards/frameworks/codes of practice/syllabi. Reject news/press/blog/magazine/publication lists/annual reports/events/careers/general about/funding and generic sustainability content. Do not treat every PDF or every page with 'skills' in a navigation menu as qualifying.
3. SCAN: retrieve the configured seed and either use eligible headed content or follow bounded qualifying child links. Respect Max_cards. Apply recognised Notes hints such as headed sections, browser attempt or following course links; record unsupported hints rather than interpreting arbitrary instructions.
4. RETEST: plain fetch, then bounded browser rendering when needed. Record each attempt's actual HTTP status when available, rendering method and failure/rejection reason. DNS/timeout/robots failures have no fabricated HTTP status. Never bypass authentication, robot challenges, CAPTCHAs or publisher access restrictions.
5. DISCOVER: seed with/without www only inside the approved domain boundary; read robots and sitemap where available; evaluate at most 15 candidate content pages selected from navigation/search/sitemaps using competency/framework/skills/standard/certification/accreditation/curriculum/programme/course/module/syllabus/learning-outcomes/training hints and Page_types_to_find. Log tried URLs and rejection reasons. Bound sitemap traversal, response size, redirects, timeouts and browser work too.
6. Enforce Allowed_domains BEFORE requests and on every redirect and browser request, including linked PDFs. Domain suffix checks must respect label boundaries, never substring matching. Disallowed redirects are logged and not followed. No unrelated search-engine or external CDN requests without explicit policy support. Robots checks remain required; failed robots retrieval is not proof of a publisher prohibition.
7. Produce short provenance-preserving cards with original source URL, organisation and exact excerpt evidence; add parent_organisation, scan_id and mode. Do not use the existing distributed full-page excerpt routine unchanged: select eligible headed learning/competency sections, preserve course names/requirements and explicitly mark omitted material. A card is not a claim that the full document has been read. Deduplicate within a run without conflating independent organisations.
8. Enforce row card limits, per-card/parent/global character budgets using the confirmed counting basis. Log budget skips and omissions; never silently truncate. Global cap exhaustion must log every skipped row. A budget skip is not FAILED_FETCH or evidence that no competency source exists.

#### Output and acceptance

- Three output families: cards.json (or numbered parts, each strictly below 300,000 serialized Unicode characters; never split a card), organisation_status.csv and url_log.csv. More than three physical files are possible if cards are split. Earlier TXT-only government upload restriction must be considered at Cloud integration; do not silently replace the requested JSON/CSV pilot outputs.
- organisation_status: one row per selected parent with SCANNED / RECOVERED / DISCOVERED / SCANNED_RESEARCH_ONLY / DROPPED_NO_COMPETENCY_SOURCE / FAILED_FETCH; cards_produced, chars_produced, urls_tried, last_error. Define mixed-mode status precedence and distinguish capacity skips from zero-qualified results in accompanying reasons.
- url_log: Scan_ID, URL, actual HTTP status if available, rendering_used, cards_produced, chars, reason_if_rejected. Preserve one row for each attempt (plain and rendered attempts separately), plus explicit unattempted row budget skips. Escape spreadsheet-formula-like values on CSV export; do not export credentials or raw error secrets.
- [x] Pilot parents: A*STAR, BCA, CAAS, CSA, IMDA, NASA (SCAN); SSG and Michigan (RETEST); DSTA and GovTech (DISCOVER). Included all 18 CSV rows for those parents with shared caps.
- [x] Pilot report: card/character totals and up to three actual sample cards per organisation in `output/competency-pilot-20261015-final/pilot_review.md`. Browser used normally (15 content attempts); restricted requests recorded. Stopped for review before the other 96 organisations.
- [ ] Tests: domain/redirect/browser restrictions, blocked content, heading/path eligibility conflicts, parent caps spanning rows, fallback ordering, duplicate provenance, card and serialized-file bounds, skipped-row logs, all fetch attempts and status aggregation.
- [ ] After pilot acceptance, integrate the new pipeline into Streamlit and run the full input list only with user approval. No automatic master catalogue replacement yet.

#### Confirmed contract (user approved all three)

1. Cards retain identity/title/type/organisation/URL/article_text and omission flag, plus parent_organisation/scan_id/mode. No LLM summaries or invented competencies.
2. No additional global cap. Per-card and organisation limits count complete compact serialized cards; file-part cap counts complete serialized JSON including array delimiters. Each file must be strictly below 300,000 characters. No token-count guarantee.
3. Explicit certification/standard/curriculum headings can qualify on a sustainability path; generic sustainability pages remain excluded. RESEARCH fallbacks must still pass the same competency-content test.

Earlier source-tuning and compact-export checkpoints below remain historical implementation records, not the new pilot's source configuration.

### Current priority — compact government-assistant transfer (2026-10-13)

- [x] Compact preparation now reports represented/shortened records and original versus excerpt body-character counts, embedded consistently in every part. Explicitly excludes metadata and does not claim token savings or complete fact retention. compact-download-4; government portal evaluation remains pending.

- [x] Compact download preparation now reads session records directly instead of building/parsing a full multi-megabyte JSON first. Part packing serializes each compact record once for size accounting, retaining strict bounds and validation. Regression verifies identical compact output and rejects invalid provenance/URLs/counts. compact-download-3; portal quality validation still pending.

- [x] Cloud UI integration confirmed: Prepare download files automatically compacts/sorts/splits current scan, then exposes individually numbered TXT download buttons and file-count confirmation. Prepared parts cached across reruns; entering the page does not start preparation. UI regression added. compact-download-2.

- [x] Source tuning paused at user request; no release freeze declared.
- [x] Export (11) measured: 13,629,593 characters / 1,627 records; PDF-derived text approximately 18% of extracted body text, not 48%. Largest PDFs include relevant NUS/IChemE/NASA competency and course material; do not delete for size alone.
- [x] Compact schema 3.0: all record IDs/URLs retained; whitespace/repeated paragraphs compacted; bounded distributed excerpts, explicitly not AI summaries. Reading priority by configured type, not credibility. Split serialized TXT including metadata at 400,000 characters maximum.
- [x] UI offers all numbered parts; no automatic preparation or AI call. Government guide updated for part-ledger processing, omitted-text caveats and unchanged DOCX layout. Current export benchmark: 6 parts / 2,006,885 characters (about 85% smaller).
- [ ] Government portal acceptance: character limit is not a token budget; evaluate recommendation quality and gaps before calling compaction validated. Excerpts may miss important competencies.
- [ ] Complete PDF semantic relevance review before deleting sources; distinguish irrelevant child PDF from useful parent catalogue. Preserve useful large frameworks. No source deletions in this export-only change.

### Current development pointer — 2026-09-22

### ACTIVE checkpoint — 2026-09-24

### SUPERSEDING direction — personal temporary collector workspaces

### Agreed release gate — 2026-10-12 (supersedes indefinite source tuning)

### Current pointer — consolidated validation requested 2026-10-13

- [x] Catalogue audit: 258 total / 204 enabled / 54 disabled, no duplicate enabled URLs; all three families and broad STE topics retained. Detailed counts/caveats in source_tuning_status.md.
- [x] Prior-export content spot-check across framework/course/report sources completed (not exhaustive). NASA menu contamination fixed with exact-page scope; live result 274 words. release-validation-3.
- [x] Request final consolidated Cloud scan with restored defaults, 204 enabled. Supersedes earlier no-scan instructions. Do not enable all paused sources.
- [ ] Receive validation export; reconcile counts, inspect content quality and access-uncertain sources. Catalogue presence is not proof of coverage or retrieval quality.
- [ ] Complete final exclusion archival/physical cleanup only after validation, then announce freeze. No further speculative source expansion during this release gate.

### Prior release-review checkpoints (historical; current pointer above takes precedence)

- [x] 2026-10-13 HDB/IPMA final dispositions: untargeted HDB homepage paused with review trail; IPMA ICB4 locally useful overview retained with direct-page routing. release-audit-13.
- [ ] Next checkpoint: consolidate active/excluded counts and STE/family coverage, preserve exclusion monitoring list before any physical catalogue cleanup, then request the final Cloud validation scan. ISA remains unchanged; GeoWorks/Tokyo and local-only successes are explicitly unverified in Cloud.

- [x] 2026-10-13 Tokyo undergraduate div-based overview diagnosed from live HTML; exact-page structured extraction/routing added with regression checks. release-audit-12.
- [ ] Verify Tokyo extraction in Cloud; post-fix local request timed out. HDB/IPMA final dispositions and final coverage/validation remain outstanding.

- [x] 2026-10-13 NP/SLA/Tokyo bounded review: OneMap moved to same-product official SLA page with local extraction; NP discovery and Tokyo graduate locally work. GeoWorks DNS failure distinguished from robots prohibition. release-audit-11; register updated.
- [ ] Resolve Tokyo undergraduate extraction failure and remaining HDB/IPMA dispositions; GeoWorks Programmes needs network/Cloud recheck. Consolidated validation remains pending.

- [x] 2026-10-13 Remaining six NUS repeat-zero sources individually checked and paused; official alternative checks also blocked. Original URLs and alternatives recorded for future monitoring, not classified obsolete. release-audit-10. NUS zero-source review disposition complete; non-NUS queue and coverage/final Cloud gates still open.

- [x] 2026-10-13 Four NUS CDE repeat-zero sources individually rechecked and paused: MSc Project Management, ECE Industry 4.0, CET and CET Learning. Official CHBE Industry 4.0 alternative also blocked. Monitoring register updated; other NUS unchanged. release-audit-9; remaining review and final Cloud validation pending.

- [x] 2026-10-13 SAE root/Mobilus alternative show explicit robot-verification notice; source paused, review trail retained. HDB locally reachable and short technical page genuine; left unchanged pending usefulness/Cloud check. release-audit-8. Do not infer access notices from word counts alone.

- [x] 2026-10-13 EMA media source and A*STAR general research root reviewed and paused; official alternatives respectively blocked / same low-detail overview. URLs/reasons preserved; other organisation sources unchanged. release-audit-7; remaining review and release validation still pending.

- [x] 2026-10-13 UCLA/Polimi four-source local recheck successful; retained rather than declaring permanent robots blocks. Registry records counts and uncertainty. No catalogue changes.
- [x] 2026-10-13 Resolved local scope issues using official replacements: Polimi civil-engineering-1 MSc; UCLA majors/minors catalogue. URLs updated with regression checks, originals preserved in review register. release-audit-6.
- [ ] Cloud acceptance for replacements and other access-uncertain sources in consolidated validation; UCLA directory includes mixed disciplines, not all STE/full syllabi.

- [x] 2026-10-13 Five SITLearn courses individually rechecked and paused after repeated Cloud zeros and local security shells. Related official microcredential also blocked. Original URLs retained in register; no speculative equivalent or access workaround. release-audit-5. Remaining queue/coverage review still pending.

- [x] 2026-10-13 SMU two repeat-zero entries paused with URLs/reasons retained. Official CIS programme overview accessible locally but lacks equivalent curriculum, not substituted. Other SMU source unchanged. release-audit-4; remaining queue and consolidated validation pending.

- [x] Three further repeat-zero NUS course sources reviewed and paused: Process Engineering, Executive FM, Graduate Certificate Applied GIS. Original/official directory alternatives return security shells; registry updated, no broader exclusion. release-audit-3. Remaining queue and final consolidated scan still pending.

- [x] Final-review subset: two SkillsFuture entries paused after repeat Cloud zero and local empty root/FAQ/sector responses; TPGateway directory not misrepresented as detailed framework. Registry records reasons. IPMA locally readable but Cloud-unverified; unchanged. release-audit-2. Continue remaining queue before final catalogue removal/freeze.

- [x] User approved a bounded release-validation round. GitHub main verified at ac6f538 before a normal deployment-checkpoint push; build release-validation-1. No crawling behaviour or source flags changed by this checkpoint.
- [x] Canonical ICE Cloud checkpoint finished: release-validation-1, 2026-10-12 08:04, zero evidence / HTTP 403. Canonical entry disabled, legacy alias remains disabled; monitoring register begun in source_tuning_status.md. release-validation-2. No further identical ICE test.
- [x] Full Cloud export (10) received: 230 sources, 1,601 records, 193 productive / 37 zero. Counts reconciled. Preliminary content sampling found A*STAR volume-index contamination; exact exclusion added in release-audit-1. All 37 zero-source URLs recorded in docs/source_review_register.md, still pending final disposition. Do not delete 62 partially successful Error sources en masse.
- [ ] Review actual content as well as failures and counts; reject access notices, navigation and unrelated material. Check coverage across STE disciplines and the three organisation families.
- [ ] Perform one final targeted official-equivalent URL review for unresolved sources; do not bypass access controls or equate search visibility/local success with Cloud success.
- [ ] Before removing persistent failures from the user-facing master catalogue, preserve them in a repository source monitoring register: organisation, source name, original URL, intended information, exclusion reason, last-check date, verified replacement if any, and active/replaced/excluded-pending-review status.
- [ ] Validate the cleaned catalogue in a final Cloud scan, then explicitly announce release freeze. No blanket deletion before review/register preservation. Subsequent maintenance is periodic (suggested quarterly) or prompted by reported failures.

### Prior tuning checkpoints

- [x] 2026-10-12 Consolidated ICE defaults: legacy alias retained disabled, canonical attributes source enabled; local extraction verified 1,641 words. ice-canonical-1. Tokyo access intermittent; alternative not confirmed equivalent, unchanged.
- [x] Cloud acceptance attempted and failed with HTTP 403; superseded by recorded ICE exclusion above. Local retrieval did not establish Cloud recovery.

- [x] 2026-10-12 Further NUS review: official biomedical course list, degree-design page, SCALE Civil programme and AY2026/27 SCALE bulletin all returned access blocks through permitted bounded requests. URLs/results recorded in source_tuning_status.md. No speculative replacement or additional exclusion; no new Cloud scan required for these candidates.
- [ ] Continue independent review of remaining failed sources. NUS Biomedical/SCALE remain unresolved; search-index visibility is not retrieval validation.

- [x] 2026-10-12 User-approved default exclusion of NUS CEE civil courses and three SIT undergraduate sources; URLs and access-review reasons retained, other sources unchanged. nus-sit-excluded-1.

- [x] 2026-10-12 Reviewed four official NUS/SIT programme alternatives; all normal permitted requests returned Incapsula shells. Recorded URLs and programme-equivalence cautions. No replacement or broad exclusion made.
- [x] User approved pausing the configured NUS CEE civil course list plus three SIT undergraduate sources; implemented in nus-sit-excluded-1. Other NUS/SIT sources remain independently reviewable. Avoid repeat identical scans while access conditions are unchanged.

- [x] 2026-10-12 Representative NUS civil-course and SIT civil-programme failures identified as empty Incapsula-script responses; improved diagnostic classification with no challenge execution or content-filter loosening. security-shell-1. Short genuine pages preserved.
- [ ] Review remaining NUS/SIT URLs individually for official equivalent accessible content; no blanket exclusion authorised or applied this round.

- [x] 2026-10-12 User approved disabling the three A*STAR Cloud-unavailable sources. URLs retained with diagnostics in tuning notes; no confirmed security-layer attribution. Other A*STAR sources unchanged; retired test preset. astar-excluded-1.
- [ ] Continue with unresolved NUS/SIT sources from export (4). Do not repeat A*STAR/IMDA tests without materially new access information.

- [x] 2026-10-12 Confirmed A*STAR three-source Cloud run fails all reviewed body selectors. Added payload-free diagnostic counts/flags, not permissive extraction or a claimed repair. astar-diagnostics-1.
- [ ] Inspect new A*STAR diagnostic errors before choosing browser rendering, selector repair or access exclusion; existing three-source preset remains available.

- [x] 2026-10-12 Three A*STAR failing sources checked locally: existing selectors/extractor work. Added exact three-source quick-test preset; astar-test-1. No Cloud fix claimed or broad extraction fallback introduced.
- [ ] Obtain current A*STAR-only Cloud export and raw recorded errors to distinguish missing/challenge/rendered responses from layout changes.

- [x] 2026-10-12 User-approved IMDA GenAI default exclusion after both official URLs failed Cloud PDF validation; preserved URL and reasons in tuning notes. IChemE verified, kept enabled. Retired PDF test preset; general session selection/restore retained. imda-excluded-1.
- [ ] Next: A*STAR structured-body failures in export (4); IMDA paused pending materially new access evidence, not another identical scan.

- [x] 2026-10-12 Found official IMDA GenAI alternative URL, locally byte-identical to original (2,804,080 bytes; hash logged in tuning notes). Default catalogue/preset now use alternative; old session URL still routed directly. imda-alternate-1.
- [ ] Test official alternative IMDA URL on Cloud using fresh default catalogue and two-source preset. Preserve access/signature limits; local success is not Cloud verification.

- [x] Export (8) confirms all three IChemE documents recovered on Cloud. Exact-source health now recognises document-set completeness instead of the generic five-item minimum, while retaining errors and explicit content-review caveat. icheme-health-1.
- [ ] IMDA GenAI Cloud response is HTML (2,407 bytes). Investigate an official equivalent accessible source later; no claim of recovery, bypass or automatic replacement.

- [x] Removed legacy cloud_app.py alias locally and from deployment; app.py is the only supported entrypoint. Updated packaging, active documentation and regression tests. Imported scanner modules contain the recent fixes; alias removal is not itself a cure for stale Cloud deployment.

- [x] 2026-10-08 Export (6): two IChemE PDFs recovered. Added exact linked-document discovery to include Learning Outcomes and exclude navigation. IMDA non-PDF Cloud response remains unresolved; safe format/byte-count diagnostics added, validation retained. icheme-documents-1; test with existing two-source preset.

- [x] 2026-10-08 Session-only Quick scan selection: arbitrary multiselect, one-click IChemE competency PDFs/IMDA GenAI preset, restore previous enabled flags. Repeated selections preserve original snapshot; restore keeps source edits/new rows. Master and other sessions unchanged. Snapshot expires with session; restore defaults clears it. 370 tests passed.

- [x] 2026-10-08 IChemE competency PDF size failure diagnosed: three reviewed linked PDFs are 2.47–3.04MB and text-extractable. Added exact final URL exceptions to existing bounded PDF allowance; icheme-pdf-1, Cloud acceptance pending.
- [ ] Recheck IChemE Knowledge and Competence and IMDA GenAI on Cloud. IMDA succeeds locally with valid PDF; export (4) invalid-response cause is not yet established. Do not bypass signature/access checks.

- [x] 2026-10-08 Export (4) reviewed: 1,608 records/240 sources; IChemE catalogue has 25 records and 14 verified scoped outlines in actual user output. Added remaining eleven course families after live section checks; 362 tests passed, icheme-outline-4. Existing exports unchanged; new additions pending scan acceptance.
- [ ] Investigate IChemE Knowledge and Competence response-size failure and IMDA GenAI invalid PDF response from export (4); continue content-based checks of A*STAR/NUS/SIT failures without bypassing access controls.

- [x] 2026-10-08 Five further IChemE families reviewed: process safety leadership, process control/instrumentation, human factors module 4, nuclear safety and PEM electrolysers. Scoped extraction preserves delivery attribution and regulatory scope. icheme-outline-3; Cloud acceptance pending.
- [ ] Verify IChemE catalogue and reviewed detail extraction together in a fresh Cloud scan; publishing organisation must not be confused with an explicitly named external course provider.

- [x] 2026-10-08 Four additional IChemE families reviewed live and added to scoped outline extraction: HAZOP, practical distillation, oil/gas production systems and human factors module 3. 345 tests passed; icheme-outline-2. Cloud acceptance pending; remaining families still need individual content review.

- [x] 2026-10-08 IChemE LOPA and Fundamentals of Process Safety detail sections reviewed and scoped to academic outlines, retaining learning outcomes and removing testimonials/booking material. Live checks 335/367 words; 341 tests passed. icheme-outline-1; Cloud acceptance pending.
- [ ] Continue content review of other IChemE course families before extending section-specific extraction; do not equate discovered URL counts with useful evidence quality.

- [x] 2026-10-08 IChemE dynamic catalogue recovered through observed public API; bounded requests and same-site links, 25 URLs locally, first detail page 1,254 words without templates. 339 tests passed. icheme-api-1, Cloud acceptance pending; remaining detail-page quality still to review.

- [x] 2026-10-08 IChemE Courses A-Z unresolved template evidence rejected after live verification; genuine short course-list regression retained. icheme-template-1. Source not removed; dynamic listing recovery remains next, Cloud acceptance pending.

- [x] 2026-10-08 Tsinghua postgraduate duration/admissions overview excluded after live content review; short named-course curriculum explicitly preserved in regression test. tsinghua-overview-1; catalogue unchanged, Cloud acceptance pending.

- [x] 2026-10-05 Harvard pagination hardening: skip page=0 alias, deduplicate fragment links, test partial and total failures, backend warnings for skipped subjects. harvard-pagination-1. Per-subject partial health is not yet exposed in UI; Cloud verification pending.

- [x] 2026-10-05 Harvard /catalog subject-first bounded discovery: five technical subject roots, interleaved course cards, 25 unique URLs locally in five requests. 334 tests passed; harvard-subjects-1. Cross-listed business content still requires relevance assessment; Cloud acceptance pending.

- [x] 2026-10-05 Harvard PLL detail-page extraction expanded after three live STE layout checks: learning outcomes retained alongside descriptions; related cards excluded. 333 tests passed; harvard-outcomes-1, Cloud acceptance pending. Mixed course relevance remains a separate review task.

- [x] 2026-10-05 Harvard AI Strategy reviewed course URL scoped to actual description, excluding suggested courses; navigation-class reuse covered by test. 41 words with note locally, 332 tests passed. harvard-description-1, Cloud acceptance pending. Other Harvard pages remain to review.

- [x] 2026-10-05 SJTU /en/research hub excluded after metrics/navigation review, detailed child pages preserved. Build sjtu-overview-1; Cloud acceptance pending. Next source-content target: Harvard related-course contamination in export (3), not blanket short-text rejection.

- [x] 2026-10-05 SJTU institute directory cleaned with names/descriptions preserved and mixed-discipline scope explicit; 3,953 words locally, 329 tests passed. Build sjtu-directory-1; Cloud acceptance pending. No inferred competency/course claims or catalogue changes.

- [x] 2026-10-05 SJTU summer research internship scoped to training/benefits, 232 words locally without GPA/timeline; 327 tests passed. sjtu-internship-1, Cloud acceptance pending. Research-institutions directory left unchanged pending STE scope review.

- [x] 2026-10-05 SJTU /281 academic accordion extracted (1,542 words locally, restrictions preserved); /282 application-only destination excluded. Mixed-scope/linked-document caveats included. 326 tests passed; sjtu-exchange-1, Cloud acceptance pending. Remaining research institute/summer internship records next.

- [x] 2026-10-05 SJTU /522 summer overview scoped to its actual content block; mixed-discipline/course-example caveat, 196 words locally, 324 tests passed. Build sjtu-summer-1; Cloud acceptance pending. /281 and /282 remain unchanged pending finer section review.

- [x] 2026-10-05 completed /387 admissions wrapper exclusion now that its linked PDF is separately configured. Programme/PDF guards and ArticleExtractor provenance tests pass; 323 total tests. Build sjtu-admissions-2. Next checkpoint: fresh-session SJTU-only Cloud scan; no full-scan requirement yet.

- [x] 2026-10-05 SJTU /387 linked official programme PDF added as separate enabled source: 721 words/five page markers locally, mixed-discipline and table-order caveats, robots and response guards. 321 tests passed; sjtu-catalogue-1. Cloud check pending; existing session catalogues preserved. /387 HTML cleanup remains open.

- [x] 2026-10-05 SJTU /278 and /279 engineering cluster overview extraction: English/French identities and planned-course qualifiers preserved; local output 313/217 words without menu/application sections. 319 tests passed. Build sjtu-cluster-1; Cloud acceptance pending. Next: inspect /387 linked programme list before changing it.

- [x] 2026-10-05 SJTU /778 civil engineering body extraction: verified 509 words locally, curriculum/facilities retained, navigation/admissions omitted; specific title and missing-study guard. 317 tests passed. Build sjtu-civil-1, Cloud acceptance pending. Remaining programme pages still require review.

- [x] 2026-10-05 SJTU /825 placeholder and exact research-news index excluded as evidence destinations after export and official-page review. Programme pages and article child URLs preserved; catalogue unchanged. Build sjtu-index-1; Cloud acceptance pending.

- [x] 2026-10-05 SJTU /794 exact section extraction: 859 words locally; retains both engineering/health programmes and study/industry experience, excludes menus/admission paperwork. Scope disclaimer and missing-body guard; catalogue unchanged. Build sjtu-programme-1; Cloud acceptance pending.

- [x] 2026-10-05 SJTU /267 and /270 reviewed: identical generic graduate-admission instructions, not programme curricula. Exact storage exclusions added; other programme pages and master catalogue unchanged. Build sjtu-admissions-1. Appendix document discovery remains unverified.

- [x] 2026-10-05 resumed Tsinghua exact homepage/index.htm alias guard from export (3): within-scan dedup only with matching text/org/query. Other resources retained; catalogue unchanged. Build tsinghua-alias-1; Cloud acceptance pending. SJTU duplicate programme pair remains next content-review candidate.

- [x] Export (3) short-content audit: exclude ASCE meeting submission form and exact MIT introduction-only extraction; retain short actual course lists. No catalogue changes. Build export3-content-1. IMDA error details still needed; no claimed fix to Cloud adapters.

- [x] Export (3) reviewed: 239 sources / 1,579 evidence reconciled. IMDA overview/GenAI both zero with OTHER_SCAN_ERROR; optional full ICT not scanned. Cloud acceptance remains pending. NP listing and A*STAR body selectors fail in Cloud despite local success.
- [ ] Obtain two IMDA Recorded scan errors to distinguish deployment, browser and PDF response failures before changing extraction. Added safe diagnostic categories; do not claim root cause from generic prior exports.

- [x] Sectioned ICT PDF implemented: exact-asset 600-page allowance, same 8 MB/2M-character bounds; download once, 50-page records, original page links and no silent source-cap truncation. Live 561-page extraction yields 12 records/~138k words. Added optional source disabled by default to protect transfer size; build ict-pdf-sections-1. Supersedes earlier exclusion; Cloud test pending. Not a table reconstruction or process sandbox.

- [x] PDF page provenance added: original page numbers survive text extraction, blank-page gaps preserved. Large ICT document confirmed 561 pages from bounded metadata/sample inspection; remains disabled under 400-page guard. Build pdf-page-references-1. Sectioned retrieval and full document validation remain pending.

- [x] IMDA GenAI PDF text validated and added as direct explicit-competency source: 20 text-bearing pages / 5,620 source words, exact URL/type/content guards and table-reading-order caveat. 296 tests passed; build imda-genai-pdf-1. Cloud acceptance pending; existing sessions unchanged.
- [ ] Larger IMDA ICT PDF exceeds 400-page guard; remains excluded with no partial evidence. Consider bounded document segmentation separately, not a silent limit increase.

- [x] PDF size foundation: exact two reviewed IMDA assets may use 8 MB, all other downloads remain 2 MB; PDF page/text caps reject partial results. This is not a process resource sandbox. Document discovery/content validation still pending; no PDF source enabled yet.

- [x] IMDA linked-document access/size check: HTTP200 PDF responses, 5,223,203 and 2,804,080 bytes advertised; both exceed current 2 MB ceiling. Preserve reviewed links in overview with not-retrieved disclaimer. 291 tests passed; build imda-document-links-1. No PDF parsing or content validation performed.
- [ ] Design separately bounded PDF retrieval if larger framework content is required; do not raise global HTML limits or claim links as extracted evidence.

- [x] Ordinary browser checks: SkillsFuture redirects to an access-restricted Jobs-Skills page; no bypass attempted. IMDA ICT framework candidate renders substantive overview normally. No catalogue change; ICT-only scope, not a whole-SkillsFuture replacement.
- [x] Bounded exact IMDA ICT browser extraction implemented, main-content-only with access/loading rejection and explicit overview provenance. Production local check: 397 words. Added separate supporting overview source; existing SkillsFuture/ISA unchanged. 290 tests passed, build imda-overview-1; Cloud acceptance pending.
- [ ] IMDA linked framework documents require separate retrieval/size/content verification; current overview must not be represented as complete framework extraction.

- [x] SkillsFuture local HTTP/replacement investigation: both configured URLs empty; two official IMDA alternatives return loading-only main content. No validated replacement, no threshold relaxation, catalogue unchanged. Browser viability remains unverified. Last code suite 285 passed.
- [x] User direction recorded: keep ISA unchanged now and defer its permission review. Do not automatically exclude or replace it.

- [ ] ISA permission decision: configured cybersecurity certificate page now returns programme content locally but displays an AI-use restriction notice. Confirm suitable permission/licensing or ask to disable ISA sources before expanding extraction for downstream AI use. Catalogue unchanged; no legal conclusion or Cloud recovery claim. Other tuning work remains independent.

- [x] October 1 MedTech: reproduced Enablers short-page rejection and added exact-route 50-word/all-five-names guard with overview disclaimer. Missing reviewed content fails closed. 285 tests passed; build medtech-overview-1; catalogue unchanged, Cloud verification pending.

- [x] October 1 SIMTech missing-body review: normal robots-aware production extraction succeeds locally for Industrial Automation (239 words) and Sustainability Informatics & Strategy (211 words). Existing selectors retained; Cloud discrepancy unresolved, not marked recovered. Documentation-only; last suite 284 passed. Continue insufficient-content cases without broadening extraction to menus.

- [x] October 1 NP investigation: nine local listing links under normal permission checks; Cloud zero-output cause remains unconfirmed. Expanded safe diagnostic categories and preserved all repeated-source error categories. 284 tests passed; catalogue unchanged. Await fresh diagnostics rather than guessing a selector fix.

- [x] October 1 full export reviewed: 237 sources / 1,591 evidence; counts reconcile. SLA, RICS dedup, Zhejiang and NTU scoped output verified in supplied Cloud results; 48 zero-output sources remain. Separate restrictions/empty responses from parser defects in next tuning round.
- [x] Navigation persistence fixed for omitted sidebar during scan and lock-held operations using non-widget selected_page state. 282 tests passed including both return paths; Cloud scan/preparation UX confirmation pending. No master catalogue changes.

- [x] 2026-10-01 RICS supplied-export review: exact duplicate Real Estate Agency PDF aliases (3,839 words) now deduplicate within scan when text/org/query match. Other pathways and changed versions preserved; no catalogue edits. 280 tests passed; build rics-dedup-1; Cloud verification pending.

- [x] 2026-09-29 NEA exact overview alias pair deduplicated within scan only when organisation/query/full normalised text match (554-word duplicate in supplied export). Useful child resources and changed content retained. 279 tests passed; build nea-dedup-1. No catalogue edits; Cloud acceptance pending.

- [x] 2026-09-29 Peking programme sources scoped to exact graduate introduction/biotechnology pages and main body, excluding scholarship/student-life navigation expansion observed in export. Locally useful213/741-word main bodies; no full-curriculum claim. 278 tests passed; build pku-programmes-1. Catalogue unchanged, Cloud acceptance pending.

- [x] 2026-09-29 duplicate audit: SUTD same-path slash aliases (850 words identical) dedup within scan only when text/org/query match. Different IEEE webinars and NTU programme variants intentionally preserved. 276 tests passed; build sutd-dedup-1. Remaining duplicate candidates require provenance review; no global text dedup.

- [x] 2026-09-29 Zhejiang listing gap: exact span.url discovery returns eight local article candidates; two samples extract733/303 words. Same-host/path/robots/cap guards; not listing snippets or PDF. Historical sustainability signals, not competencies. 275 tests passed; build zju-discovery-1; Cloud acceptance pending.

- [x] 2026-09-29 SLA Master Plan/OneMap exact body routing verified locally (197/169 words), excludes government banner/title-only selection; no full-document claim. 274 tests passed; build sla-content-1. Zhejiang HTML reachable but content review still pending; no catalogue edits or Cloud recovery claim.

- [x] 2026-09-29 newly empty source review: PUB robots explicitly Disallow:/; Cambridge engineering news and later robots endpoint HTTP503. No bypass/replacement/disable performed. Local access findings documented, not asserted as proven prior Cloud causes. Documentation-only; last code suite272 passed. Continue remaining failures/content review.

- [x] 2026-09-29 content audit: retain concise EI course lists and AI privacy research; exact scan-boundary exclusions for ASCE committee application, NEA empty grants listing and Tsinghua recruitment listing. No broad keyword filtering or configured-source deletion. 272 tests passed; build cloud-noise-1. Changes apply next scan, current export remains review baseline.

- [x] Post-Cloud review: public export gains fixed per-source diagnostic categories without raw errors; NTU Robotics exact-page discovery excludes unrelated listings/forms/degrees observed in supplied export. Build cloud-review-1. No master source edits; existing files cannot recover omitted diagnostics. Continue remaining quality review before repeat scan.

- [x] 2026-09-29 Cloud checkpoint reviewed: supplied export 1,580 evidence/237 sources/133 organisations, counts tally. Confirmed AISG, NParks, EI, HKUST education, Polimi, ISA IC32 and IEEE outline content. Partial acceptance only: 47 zero-output (previous44), ICE/SIMTech/NP still zero; new failures and NTU unrelated content recorded in source_tuning_status.md. Generic exported errors prevent exact diagnosis.
- [ ] NEXT after Cloud review: expose safe source-level failure diagnostics in export; scope NTU programme discovery to relevant curriculum material. No immediate repeat full scan needed. Do not classify count decline alone as quality regression or declare all tuned sources recovered.

- [x] 2026-09-29 NUS Civil/Environmental courses, Industry4.0 and MSc Project Management HTTP checks empty. Official Civil build-your-own-degree alternative blocked in HTTP and browser; no URL changes or bypass. Documentation published; last code suite 262 passed.
- [ ] NEXT acceptance checkpoint: request full Cloud scan and public_evidence.txt on build ieee-outline-1, with revised AI Singapore archive configured. Evaluate accumulated NParks/ISA/EI/ICE/HKUST/NP/AISG/Polimi/SIMTech/IEEE fixes using actual content, not count alone. Do not claim Cloud recovery from local probes. Restore defaults optional but discards temporary edits.

- [x] 2026-09-29 IEEE storage tutorial: verified 65-word four-session outline, exact-page routing and guarded short-outline exception; full-resource disclaimer retained. SAE short root and HDB generic services homepage not claimed recovered, unchanged. 262 tests passed; build ieee-outline-1. Cloud acceptance pending.

- [x] 2026-09-29 NUS access review: SCALE BTech Civil, CDE Biomedical undergraduate and FASS PC Applied GIS return six-word Incapsula notices in normal browser; HTTP empty. Current AY2026/27 SCALE bulletin alternative also HTTP empty. No accessible replacement verified, no catalogue/runtime changes or bypass. Recorded unresolved limitations; last code suite 261 passed. Remaining-source review continues.

- [x] 2026-09-29 SIMTech training overview scoped to substantive rich-text block (239 words, four modules); no full-syllabus claim. ICE legacy /attributes mapped to reviewed canonical URL for within-scan dedup, permissions on both checked. EMA media HTML still empty, unchanged. 261 tests passed; build simtech-training-1. No master catalogue edits; Cloud verification pending.

- [x] 2026-09-29 Polimi: exact standalone routing and main-body extraction for both configured programme pages, locally verified 694/611 words. Preserve actual degree levels (Civil page says BSc despite URL). 259 tests passed; build polimi-programmes-1. Tokyo still connection timeout, HKUST general overview only inspected. No catalogue changes; Cloud acceptance pending.

- [x] 2026-09-28 AISG research root replaced by official research category archive; legacy connect host robots401 respected. Scoped card discovery returns 25 candidates, three sampled articles 580/526/673 words. Research/news signals only; not competencies. SkillsFuture framework and FAQ HTTP remain empty, unchanged. Build aisg-research-1; existing sessions require URL edit or reset defaults. Cloud acceptance and remaining failures pending.

- [x] 2026-09-28 NP engineering: exact listing discovery yields nine actual courses; scoped overview/learning extraction yields 123–807 words locally. Eight empty interactive module accordions explicitly flagged in evidence, not claimed as complete syllabuses. SMU sustainability HTTP still empty; unchanged. Build np-curriculum-1. Cloud acceptance and remaining empty-source review pending; no master source edits.

- [x] 2026-09-28 zero-output review: exact-page routing/extraction for official ICE attributes and HKUST sustainability education. Permission-checked local samples 1,641 / 1,374 words; all three ICE grade tabs retained and related events excluded. 254 tests passed; build structured-pages-1. No source catalogue changes. Earlier Cloud failure cause unconfirmed; Cloud acceptance and other empty sources remain pending, including legacy ICE /attributes.

- [x] 2026-09-28 duplicate-description review: three redundant IEEE PES video/slides records identified in supplied export. Within-scan guard keeps first representative URL only for same webinar/organisation/query and identical normalised description; other courses/content remain distinct. Resets every scan. 252 tests passed; build description-dedup-1. No catalogue changes. Next: remaining zero-output sources; full rescan not required yet.

- [x] 2026-09-28 catalogue tuning: scoped EI root to nine public technical categories, excluding staff/test/policy/bespoke sections. No accessible verified alternative academy root due robots403. Added official ISA IC32 public-description source (341 words live, learning outcomes inspected); reject heading-only ISA product bodies. Preserve concise legitimate catalogue lists; no full rescan needed yet. See source_tuning_status.md.

- [x] Current Cloud export reviewed: 1,611 records, 236 sources, 44 zero-output; 63 additional Error sources retain evidence. NParks navigation/anchor noise corrected via scoped research/biodiversity routing and .main-body extraction; research seed classification corrected. Live samples verified (207/584/898/879 words), oversized PDF remains rejected. 245 tests passed. Remaining priority: title-only catalogue records, duplicate descriptions, then zero-output sources; no mass disable based only on status.

- [x] Resumed source tuning after scan stability confirmation: official SIT Solar course and course portal still lack readable HTTP text; normal browser portal/energy-efficiency centre return 403 Incapsula six-word notices. No accessible same-course substitute verified, no URLs/flags changed. Recorded in source_tuning_status.md. Next use current Cloud evidence TXT for content-led remaining-source review; no repeat full scan needed if completed output remains available.

- [x] Repeated stop diagnostic: version session-held workflow/job objects; replace idle outdated runtime without deleting sources/evidence. Do not replace an active worker. Visible build scan-isolation-2 identifies deployed runtime. Unexpected worker failures now emit traceback/source/progress to server logs. Stale session objects are a plausible cause, not confirmed without Cloud traceback.

- [x] Website failure isolation: discovery/browser/parser errors skip affected source/page, preserving earlier evidence and continuing to remaining sources. Up to three detailed page errors per source plus total skipped count appear in final error summary; completion is WITH_ERRORS, not a failed background job. SQLite/resource failures remain fatal. Regression includes blocked NUS, generic and differently defined ScanError, discovery timeout, empty HTML and downloadability.

- [x] Session scan progress: background worker owns the scan DB lock without Streamlit calls; fragment polls an isolated status snapshot each second. Reruns show current source, completed/total, percentage and remaining count instead of the lock-only page. Duplicate starts blocked; errors release lock. Reset/edit disabled during active work. No cancellation on tab close yet; bounded requests continue until completion, server restart interrupts.
- [x] Verification: 236 tests passed in the deployment checkout, including active-lock progress UI, duplicate start and worker failure cleanup. Cloud small-scan acceptance requested next.

- [x] Remove administrator UI/password requirement; app.py exposes the same officer UI to each approved visitor.
- [x] New sessions read master sources only, with no prior evidence. Source edits/uploads live in session memory and cannot save to master YAML or another user's database.
- [x] CSV template/upload validation and manual review/apply; restore default sources. Start fresh clears the whole session and reloads defaults.
- [x] SQLite :memory: per session, no disk evidence database/audit payload logging from active services. New scan clears previous evidence/summary/run; only current round shown/downloadable. Legacy disk history left untouched, never imported.
- [x] TXT preparation explicitly click-only even after scanning. No user-facing batch selector or batch filename. Existing export schema IDs retained as internal identifiers for government assistant compatibility.
- [ ] Validate two browser sessions and government-browser download after deployment. Browser disconnect cleanup is framework-managed; brief reconnects can resume, so Start fresh is the explicit immediate reset. No claim of instant secure memory erasure.
- [x] Verified 233 tests in both main workspace and deployment checkout; published session-only design to GitHub main as ad82466. Master catalogue unchanged. Existing disk history remains untouched and is not read by the new UI.

Earlier shared-admin and five-batch runtime directions below are superseded for the active UI.

- [x] Unified entrypoint: app.py now runs the safeguarded shared collector locally and in cloud; cloud_app.py is only a compatibility alias. Composition moved to collector_services. Admin authorization, lock and existing .cloud_runtime state preserved. Former local root history untouched, not silently imported. Documentation updated to one setup path.

- [x] IT-team handover: replaced chronological README with current collector overview; added architecture/data, operations, security, contribution and tuning-status documentation. Old README preserved locally outside publication allowlist. Deployment guide reconciled with current Scan & Download behavior.
- [x] Publication allowlist now includes regression tests, dev dependencies and required maintenance helpers so the receiving team can validate a clean checkout. No runtime data/secrets included.
- [x] Handover verified/published: 228 tests passed in both working folder and synchronized deployment checkout; reviewed patch published to GitHub main as b935942. No databases, logs, secrets or evidence exports published.
- [ ] Deployment acceptance remains: verify cloud rebuild/download on target browser. Source URLs unchanged during documentation work; SIT alternatives remain the next tuning task.

- [x] NUS Urban Design completeness reviewed: short text includes semesters, named courses, units and degree requirements. Scoped curriculum-body extraction now excludes adjacent menu; tables preserved by regression test.
- [x] All five SIT short-course pages checked with standard browser across this and prior pass: access-block notices, not usable course text. Sources retained unchanged pending verified alternatives. Do not claim browser rendering solved SIT.
- [ ] NEXT: accessible official same-course alternatives for SIT; remaining access-limited source review. No full scan requested solely for this extraction cleanup.

- [x] NUS curriculum browser verification: standard Playwright retrieves Urban Planning (1,119 extracted words, named course codes/units inspected) and Urban Design (256 words, curriculum marker validated). Scoped browser path fetches rendered evidence, not just discovery links; enabled only these two local configured sources. Robots/final URL/status/size/time checks, no login/challenge interaction. SIT Smart Grids remains blocked. 226 tests passed.
- [ ] Cloud acceptance: enable Browser for the existing two NUS curriculum rows, then run a small scan after deployment. Cloud IP/browser behaviour is not proven by local tests. Next examine Urban Design content completeness and remaining SIT alternatives.

- [x] Completed paused validation/publish: 224 tests passed; empty-HTML retrieval diagnostics pushed to GitHub main as a08ceec. NUS/SIT access failures remain unresolved; no source URLs changed this round. Hosted rebuild not independently verified.

- [x] NUS/SIT follow-up: no verified replacement this round. NUS canonical curricula blocked; SIT Smart Grids alternates blank/blocked; SITLEARN catalogue includes real listings but sampled course detail fails. Added explicit empty/script-only HTML retrieval error with regression tests; no access bypass or source removals.
- [ ] NEXT: same-course official alternatives or permitted browser-rendered verification for remaining NUS/SIT sources. Do not present an error-message improvement as recovered course coverage.

- [x] Oxford teaching discovery scoped to actual linked official graduate course pages, not research navigation. Official course-host robots.txt returns 403; retain accessible overview only, no bypass or claim of syllabus coverage. EnterpriseSG root again yielded 695 words but linked career routes still fail; keep intermittent status.
- [ ] NEXT: remaining NUS/SIT access-limited curricula/course sources; next consolidated scan should verify narrowed Oxford/SIMTech output and EnterpriseSG repeatability.

- [x] SIMTech secondary discovery reviewed: 25 generic candidates included navigation and encoded/unencoded duplicate root. Actual research body has no onward links. Scoped standalone-resource route now returns one permission-checked root for both URL encodings, preserving 211-word research extraction. No catalogue/history mutation.
- [ ] NEXT: remaining batch-46 agency/university access-limited sources; SIMTech overview is not a full course catalogue. Existing cloud catalogue must use the reviewed SIMTech URL for this route to apply.

- [x] Download preparation no longer runs on page entry. Existing latest result needs explicit Prepare TXT click; only a scan completed in the current interaction auto-prepares. Browser save still requires Download. Session caching and non-rerunning download preserved.
- [x] A*STAR corporate sustainability replaced locally by verified SIMTech Sustainability Informatics & Strategy research page. Exact-body extraction retains lists/plain text: 211 words; navigation excluded, missing/short content rejected. ID/enabled/caps/history preserved. Cloud seed updated on publish; existing cloud runtime catalogue is deliberately not overwritten.
- [ ] NEXT: inspect SIMTech secondary discovery candidates and remaining empty agency sources; consolidate before full scan. Hosted existing runtime needs the reviewed sustainability URL change through Source Configuration to activate this replacement.

- [x] Published code-only deployment commit 33dc591 to huangchaohung/competency-intelligence-system main after 217 passing tests. No local DB/logs/backups/secrets uploaded. Hosted rebuild/acceptance still unverified; user should check Source Configuration and Scan & Download. Future updates use the isolated checkout, not manual file copies.

- [x] Source schema 20 removes Country, Category and Evidence label from active SQLite sources, YAML and public export fields. Existing IDs/history preserved; local pre-migration backup in backups/source-schema-20260924-133907. Research ARTICLE sources migrate to visible RESEARCH type; compatibility input fields remain in the legacy Python entity only, not persisted. Technical identity/retirement/URL-pattern fields remain backend infrastructure, not officer columns.
- [x] Connected isolated .cloud-deploy checkout to https://github.com/huangchaohung/competency-intelligence-system.git (main). scripts/sync_cloud.py copies only deployment allowlist, without committing/pushing automatically. No manual document copying needed for subsequent code updates. Cloud runtime migration strips removed fields without replacing user-edited URLs.
- [ ] Verify hosted schema migration and Scan & Download after publishing; cloud source URL edits remain separate from version-controlled seed updates. Next source tuning: remaining batch-46 sources after MedTech/Biodesign checkpoint.

- [x] Resumed source tuning: A*STAR MedTech now discovers only its root and actually linked innovation-pillars/enablers pages, respecting robots/caps. Exact-page body extraction removes general navigation. Live root 119 words; pillars 156 words of named technical capabilities; enablers below existing article threshold, not stored. No threshold relaxation or claims of complete coverage.
- [x] Source Configuration hides Country, Evidence label and Category in grouped tables/editor; existing backend values preserved. Current project already directly supports cloud_app.py + requirements.txt + packages.txt.
- [ ] Continuous deployment setup blocked on user's existing GitHub repository URL: working folder is not a Git repository. Do not initialize/push the entire folder, which contains local and legacy data. Connect a clean allowlisted deployment working copy to the existing remote once supplied; no external publishing performed.
- [ ] NEXT source tuning: remaining batch-46 access-limited/empty sources and MedTech short enablers resource if useful. Consolidated scan checkpoint pending further fixes.

- [x] Website tuning paused at user request. Singapore Biodesign completed (four live records, 211 tests at that checkpoint); A*STAR MedTech narrowing is the next tuning task. Preserve the remaining batch_46_review.md worklist.
- [x] New delivery flow: internet-accessible government laptop uses the hosted public collector and downloads one evidence TXT directly. No internal competency framework is uploaded. History removed from navigation, not deleted from storage. Latest shared result, source health and paginated preview appear on Scan & Download.
- [x] Download prepared automatically, session memory limited to one package, download click does not rerun the app. Added small test TXT to diagnose browser/network restrictions without bypassing controls.
- [ ] Cloud/government-browser acceptance: update hosted code, run/download latest result and verify full TXT. Actual reported cloud failure cause is unconfirmed without browser/network evidence. Admin-only scans retained; private app access still required.
- [ ] Resume source tuning only after this delivery checkpoint. Cloud runtime source configuration remains separate from repository defaults.

This pointer supersedes older NEXT/CURRENT NEXT notes below, which are chronological review notes.

- [x] User reports cloud preparation/deployment done; resumed source tuning. This is user confirmation, not an independently verified cloud crawl.
- [x] Singapore Biodesign general MedTech duplicate replaced with official migrated fellowship catalogue; country Singapore, CATALOGUE route. Four live records verified: overview 780 words and programme pages 351/267/262 words. Consent modal and programme alumni directory excluded by observed DOM IDs. 211 tests passed; existing IDs/history/enabled state preserved.
- [ ] NEXT: narrow A*STAR MedTech technical body/discovery, then remaining access-limited sources. Biodesign overview still includes testimonials; do not equate these with curriculum statements. No full scan required for this single change.
- [ ] Cloud deployment uses a separate runtime catalogue: local tuning changes do not automatically update the hosted app. Publish code changes and manually mirror reviewed source edits through its administrator editor before cloud scan validation.

- [x] Cloud trial preparation: separate cloud_app.py, admin-only configuration/scans, single-instance nonblocking lock, isolated runtime, bounded dependency list/Linux Chromium, code-only packaging and deployment instructions. Local data/catalogue unchanged.
- [ ] Immediate checkpoint: private Community Cloud deployment and small Linux/browser scan; verify access controls, export and busy-session behaviour. Cloud compatibility/resource capacity is not yet verified. Durable storage and production authentication remain out of scope.
- [ ] Resume the source-tuning items below after cloud acceptance; no sources are being disabled or replaced as part of deployment preparation.

- [x] A*STAR MedTech source uses research-resource route; root recovered (468 words), Singapore country corrected. 206 tests passed. EMA media releases access-blocked, unchanged.
- [ ] NEXT: verify programme-specific Singapore Biodesign URL; narrow A*STAR MedTech technical content (navigation still present). Remaining access-limited sources are not resolved. Details: batch_46_review.md.
- [ ] Consolidated user scan checkpoint after further verified fixes; do not repeatedly scan the whole catalogue for each individual change.

### Batch 46 review — 2026-09-21

- [x] CUGE exact-root PDF discovery supports actual links to government file-host collection /32/, permission/cap/dedup guarded. 206 tests passed.
- [ ] CUGE PDF retrieval remains blocked: file-host robots.txt returns 403, so no PDF attempted. Index remains available; do not report full-guide coverage. Continue remaining agency roots.

- [x] NParks Nature replaced by verified CUGE publications index (765 words), standards/guidance and Singapore. Preserved identity/history/enabled state. A*STAR alternative NOT applied: initial text included navigation, isolated extraction insufficient. Experimental code reverted.
- [ ] CURRENT NEXT: NParks linked technical resources and substantive A*STAR content; publication index does not imply all PDFs were retrieved.

- [x] 2026-09-22: SAE Mobilus alternative returns bot verification, no replacement. EnterpriseSG Energy & Chemicals corrected to catalogue route/Singapore; 695 words validated but immediate follow-up returned script-only HTML: INTERMITTENT, not healthy. IDs/history/URL/enabled state preserved; 205 tests passed.
- [ ] CURRENT NEXT: specific A*STAR/NParks technical resources; next scan must assess EnterpriseSG repeatability. Keep access failures explicit; no block-page evidence or unverified replacements.

- [x] 2026-09-22: IEEE PES host-specific public-description extraction, explicit description-only disclosure, unchanged 100-word guard. Three of four live samples recovered; short fourth rejected. 205 tests passed. No full-resource access or catalogue/history mutations.
- [ ] CURRENT NEXT: SAE standards and remaining empty agency sources; next consolidated scan to inspect recovered professional-resource descriptions.

- [x] 2026-09-22: IFMA individual-courses parser fix restores 1,615 words including named courses; exact-page scope, navigation still removed, no catalogue mutations. 202 tests passed. Details in batch_46_review.md.
- [ ] CURRENT NEXT: IEEE PES resource descriptions (links exist but sampled extraction fails), then SAE alternatives and remaining agencies. No immediate rescan requested.

- [x] Oxford Energy homepage replaced with its verified Teaching and training page, CATALOGUE label/UK country. 412 programme-overview words extracted; 12 discovery candidates, root only sampled. IDs/history/enabled settings preserved; 201 tests passed. See batch_46_review.md.
- [ ] CURRENT NEXT: remaining empty agency/professional-body sources; next consolidated scan must also inspect secondary Oxford candidates for relevance. No immediate full scan requested.

- [x] ETH/UIUC follow-up: UIUC canonical trailing-slash URL extracts 3,085 programme words; ETH official research page extracts 297 research words (course-page listing not verified). Updated YAML/database preserving IDs/history/enabled flags; 201 tests passed. Details in batch_46_review.md.
- [ ] NEXT: Oxford Energy official teaching/research alternative, then remaining zero/error sources. Validate these replacements in the next consolidated scan, not by rewriting old batches.

- [x] Full-scan checkpoint received: 1,686 unique records/count match; 111 volume-Healthy, 83 Low, 35 No evidence, 7 Error. Verified NASA eight handbook pages, NUS Life Sciences PDF and removed ISEP login contamination. See batch_46_review.md; not all retained text semantically certified.
- [x] Fixed MIT DUSP source 156 route ARTICLE -> CATALOGUE plus country/type metadata; live configured route extracts 2,068 programme words. YAML/database updated preserving ID/history/URL/enabled flag. 201 tests passed.
- [ ] CURRENT NEXT: find substantive ETH ESA / Oxford Energy official roots, investigate newly empty UIUC, continue unresolved access-limited sources. Earlier batch-45 full-scan request fulfilled; no immediate rescan for this one change.

### Batch 45 content tuning — 2026-09-21

- [x] SIT short-course review: five originals and two official alternatives blocked by Incapsula. Corrected five courses' country/training metadata, including energy-storage FRAMEWORK -> CATALOGUE, preserving IDs/history/URLs/enabled flags. 201 tests passed.
- [ ] CURRENT CHECKPOINT (supersedes earlier no-rescan notes): user full evidence-only scan of currently enabled catalogue, then share public evidence TXT. Validate accumulated NASA/NUS fixes and explicit access diagnostics; unresolved sources remain under review, not assumed healthy. Preserve prior exclusions.

- [x] Probed six NUS GIS/Sustainability and SIT undergraduate sources: insufficient content; repeat probes confirmed Incapsula on three. Preserved URLs pending verified alternatives; no old brochures substituted. Added bounded response diagnostics to configured-source probe. See batch_45_review.md.
- [ ] Next tuning group: SIT short courses, then consolidate access-limited sources for user-environment validation and documented exclusion decisions.

- [x] Replaced NUS Life Sciences source 274 with verified official course-list PDF, preserving identity/history and limits; YAML + database updated. Configured route extracts 38,763 words of descriptions/syllabus/outcomes, internal AY2026/27 heading. 201 tests passed. SCALE placeholder-only sample schedule rejected despite accessible download. See batch_45_review.md.

- [x] NUS focused diagnosis: three CDE configured sources return HTTP-200 Incapsula notices; official BME curriculum alternative also blocked in direct probe. Added explicit short-block-page detection rather than weakening extraction. 201 tests passed. SCALE/DBS probes have no visible text, cause still unconfirmed. No catalogue changes or bypass; details in batch_45_review.md.
- [ ] Continue NUS remaining/alternative pages and investigate SCALE/DBS empty responses before moving to SIT. Do not equate search-index availability with successful crawler retrieval.

- [x] Checked supplied export counts/unique IDs/URLs and screened titles/block text; 1,694 records, 236 source-health rows: 111 volume-Healthy, 83 Low evidence, 42 No evidence. Original count matches. This is preliminary screening, not full content certification.
- [x] Fixed NASA handbook navigation contamination with bounded linked-chapter discovery and main-content extraction; reject confirmed login-page shapes including ISEP member-login evidence without rejecting articles about login. 199 tests passed. Details: batch_45_review.md.
- [ ] NEXT: inspect empty NUS course/CET group and skipped-extraction causes; then SIT and remaining zero/low-quality sources. Preserve good concise resources and account for deduplication before exclusions. No full rescan requested yet.

### Persistent scan summaries — 2026-09-21

- [x] User accepted current UI. Added idempotently created scan_summaries table, storing original evidence count and allowlisted source-health rows at completion, before text retention runs. Legacy batches are not backfilled from possibly pruned evidence.
- [x] History uses recorded health for new batches after text pruning; older batches retain unknown-total handling. No raw errors, AI suggestions or internal framework data in stored summary.
- [x] Evidence TXT receives saved original total and count-completeness check; mismatch blocks full export. This checks counts, not byte-for-byte historical content integrity or full website coverage. Existing single-download UX preserved.
- [x] Tests verify retention-independent summaries, repeated initialisation and export mismatch rejection; full suite 196 passed. No real scan or paid AI request performed.
- [ ] NEXT checkpoint: restart app and run an evidence-only scan of currently enabled sources to validate accumulated source tuning and new summaries. Review exported TXT for genuine content quality, not counts alone. Keep documented exclusions disabled. Then continue failed/low-quality-source tuning; collector schema/dependency cleanup remains separate pending work.

### Unified source editor — 2026-09-21

- [x] Unified Add or edit / Delete / Validate and save guidance into one information box with consistent bold labels and paragraph styling.

- [x] Added always-visible instructions inside Edit Sources: far-left row selection -> trash/bin -> validate -> confirm removal -> apply. Explicitly distinguish Enabled from row selection and explain draft-only changes and preserved historical evidence.

- [x] Removed Preview catalogue backup UI/upload renderer and separate Add or remove sources form. One Edit Sources expander supports dynamic row addition, editing and deletion.
- [x] Preserve existing database identity and hidden crawler settings via immutable row keys, not row position. Validate complete draft, show adds/edits/removals, confirm removals and retire missing sources through existing persistence without deleting historical evidence.
- [x] Compare validated baseline with live catalogue to reject stale drafts; intended add/delete/URL changes no longer mistaken for staleness. Reset editor after applying/discarding; empty catalogue can accept a new row.
- [ ] User checkpoint: try adding/editing/deleting a draft row, review validation and discard if only testing. No catalogue mutations were made during development. Once UI accepted, resume source tuning.

### Compact continuous-task prompt — 2026-09-18

- [x] TXT guide replaced with supervisor-review-5-compact: consolidated execution flow, no routine stage approvals, parse/index reuse and one internal report dataset. Preserved six-column evidence tables, full URLs/outlier citations, complete support sentences, Word styles and evidence/deletion/coverage safeguards.
- [ ] Validate whether portal still needs multiple turns/instances on identical inputs. Single-task instruction cannot override context/tool limits; no evidence reduction or guaranteed latency claim. Replace previous instruction block rather than append.

### Evidence table refinement — 2026-09-18

- [x] Guide supervisor-review-4-evidence-tables: complete claim-support sentences rather than character-sliced snippets; auto-height/wrapped rows, first/last-word checks and conditional visual validation. Actual truncation cause unconfirmed without generated DOCX.
- [x] Six-column recommendation/outlier evidence tables now include explicit evidence type and full clickable supplied URL. Unknown/ambiguous labels not upgraded by organisation prestige.
- [x] Remove duplicate Source Register (including 6.6); preserve other audit/coverage information. Source URLs retained directly in every relevant evidence table.
- [ ] Regenerate and inspect portal DOCX to verify unclipped prose, readable six-column widths and outlier links. Prompt-only change; runtime unchanged.

### Prompt efficiency refinement — 2026-09-18

- [x] Replaced TXT guide with supervisor-review-3-efficient: 1,582 whitespace-delimited words versus 3,192 previously (about 50% shorter; not a token/latency measurement). Removed obsolete multipart instructions, duplicate formatting and conflicting staged-chat requirements.
- [x] Retained table layout, paragraph styles, bold counts, citation/coverage safeguards, deletion thresholds, separate outliers, single DOCX and minimal chat response. Explicit BEGIN/END delimiters separate system instructions from officer setup notes.
- [x] Added parse-once/index reuse, internal structured draft before DOCX, shared Word styles and one deliberate validation pass with necessary defect correction. No evidence sampling/truncation added.
- [ ] Compare old/new prompt using same inputs and model in government portal: timing, genuine coverage, support accuracy and layout. Actual performance cause and improvement are unverified; no runtime change or portal test performed here.

### Supervisor report readability v2 — 2026-09-18

- [x] TXT guide updated to supervisor-review-2: one-column executive-summary table with labels above values; one-column multi-row recommendation detail tables; separate claim-linked supporting-evidence tables with proportionate widths and exact URL targets.
- [x] Added selective bold quantities, count-unit checks (current taxonomy has three known source families), consistent section hierarchy, grayscale-friendly styling, pagination guidance and distinct outlier tables. Existing 1.5 spacing/justification/paragraph spacing and single-DOCX/brief-chat delivery retained.
- [ ] Validate actual generated Word report in the approved government portal; no DOCX supplied or rendered in this documentation-only change. Update the assistant instructions using the full current TXT guide, not an additive conflicting old formatting block.

### Supervisor review report / single download refinement

- [x] App exports only `public_evidence_batch_N.txt`; removed assistant-guide download and changed manifest file count to one. Versioned session key prevents old two-file packages appearing after upgrade. Guide remains a maintained developer document for one-time assistant configuration.
- [x] Updated TXT assistant guide to supervisor-review-1: one genuine DOCX only; 1.5 line spacing, justified prose, 6 pt after paragraphs; executive-summary labels bold/underlined on separate paragraphs above values; content-proportional table widths within page margins, narrow numeric columns, repeated headers and layout validation.
- [x] Final successful chat response is only completion sentence plus DOCX link, no report summary or JSON attachments. Coverage/provenance/excluded assessments move to DOCX appendix; blockers and provisional coverage still disclosed honestly.
- [x] Optional knowledge-base policy: narrowly permissioned stable framework/glossary references; batch-specific evidence uploads; explicit version selection, no mixing historical evidence or assuming complete retrieval/memory.
- [x] 189 tests passed. Actual portal-generated DOCX styling must be validated in the government environment; instructions cannot guarantee tool capabilities.
- [ ] Supervisor checkpoint: regenerate a report with updated instructions and inspect paragraph spacing, executive summary, table widths, source citations and downloadable DOCX. No new public scan required.

### Approved-extension export update

- [x] Active downloads now exactly `public_evidence_batch_N.txt` and `government_assistant_guide.txt`. Evidence is unchanged structured JSON encoded as UTF-8 text; guide contains assistant settings, full instructions and starter/user prompts. No HANDOVER_batch file is returned or downloadable. Previous two-file JSON/Markdown delivery is superseded.
- [x] TXT guide explains embedded manifest/index and .txt structured outputs, overriding legacy multipart instructions. Assistant guide can be configured once; only evidence needs transfer on subsequent batches.
- [x] 189 tests passed. Portal file/content/size approval still needs validation; changing extension does not shrink model context. Legacy multipart helper remains internal and is not offered by the active UI.

### Two-file transfer requirement (supersedes multipart delivery)

- [x] Officer requested at most two transfer files. Active export now produces one schema-2.0 JSON containing manifest, all evidence, source snapshot, source health and complete organisation index, plus one Markdown handover guide containing its SHA-256 checksum.
- [x] Removed multipart size selector and ZIP/individual-part UI. No text is dropped to meet the file-count requirement. Legacy multipart builder remains an internal helper only.
- [ ] Validate actual government portal upload/context capacity with this larger single JSON. A two-file transfer does not guarantee all evidence fits the model context. Do not silently truncate if rejected.

### Public handover exporter checkpoint — 2026-09-17

- [x] Added independent `public_handover` service using explicit source/evidence fields, never legacy recommendation/framework/chat tables or raw error text. Batch source snapshot supplies metadata; no live-catalogue substitution.
- [x] History & Export now prepares a ZIP and individually downloadable manifest, complete evidence parts, sources, complete organisation/ID index, sanitised-by-allowlist health summary and HANDOVER instructions. Organisation filters do not restrict exports. No AI calls.
- [x] Evidence-part byte limit configurable from 1–20 MB (default 2 MB), measured as UTF-8 JSON. Full records preserved; an oversized individual record blocks export with an explicit message rather than truncating. Automatic segmentation of a single long document remains pending if needed by portal constraints.
- [x] Manifest records file hashes/sizes, batch/status/timezones, counts and coverage limits. Hashes detect file mismatch, not authorship/security approval. Original scan totals are unavailable in legacy storage, so prior-pruning verification remains false rather than invented.
- [x] Reject running, empty, retention-ineligible, mixed-batch and duplicate-ID exports; obvious credential-bearing/local URLs rejected. Public text and manually entered metadata still need officer review; this is NOT comprehensive secret detection/DLP or a guarantee that all content is public.
- [x] Full suite: 188 passed, including multipart completeness, full text preservation, metadata allowlist, checksum/ZIP integrity, no raw error export, duplicate/cross-batch/pruning rejection and oversized-record refusal.
- [ ] USER CHECKPOINT: in History & Export, select a retained batch, prepare/download files and inspect manifest and evidence text. No new scan or internal framework upload is required for this collector UI check. Pilot portal ingestion only after IT-approved transfer.
- [ ] NEXT: persist original scan totals and per-source health independently of retained evidence; improve completeness reporting for new batches and preserve truthful older-batch reporting. Then controlled legacy schema/dependency cleanup and portal pilot.

### Runtime conversion checkpoint — 2026-09-17

- [x] User confirmed Version 2 is the preserved backup; current repository is the implementation target. Backup untouched.
- [x] Active entry point now composes only source/configuration/scanning/logging services. No AI client, framework service, recommendation workflow or Ask AI is instantiated. Connections close after page execution.
- [x] Collection-only Home, Run Scan and History & Export replace active legacy pages; source editor retained without LLM switches. Manual source-health advice and bounded 10-item/100-word evidence previews retained.
- [x] No legacy export is exposed by the new history page. It explicitly states public-only handover export is pending, rather than presenting the old sensitive-capable export as safe.
- [ ] NEXT: implement and test the versioned public-only handover package. Do not request a government transfer until this exists and IT approves the route.
- [ ] Legacy modules, dependencies and database schema/records still exist, but are not the active UI/services. Collector-only schema, historical health persistence and safe legacy-data cleanup remain pending; no internal records deleted in this step. Earlier tracker items are complete only to this stated scope.

This section supersedes conflicting historical directions below. Earlier checklists remain a development record, NOT authority to retain personal-laptop framework comparison, Ask AI, AI URL suggestions, or LLM fallback. The current turn updates the design and operating prompts; runtime removal/export implementation is still pending.

### Security and operating boundary

1. Personal laptop: configured public STE sources -> deterministic crawler -> extracted JSON -> deterministic organisation map -> source-health review -> public-only downloadable handover package.
2. Transfer only that package through an IT-approved channel. Email is an option only if permitted; do not assume personal-to-government email, attachments, archives or personal devices are approved.
3. Government laptop/approved AI portal: upload public evidence AND the internal competency framework there; normalise evidence, compare, recommend, and create archive files there.
4. Frameworks, recommendations, questions, answers and internal context must not be sent back to the personal laptop or public AI endpoints. No OpenAI key or AI capability required in the collector, including URL remediation.
5. This separation reduces exposure but is not a security certification. IT must approve data classification, portal/model, knowledge-source permissions, retention, file types/limits and transfer route. Public-source documents may still contain personal information or copyright restrictions.

### Personal-laptop scope and user journey

- Keep the configured sources, organisation/family/country tags, crawler strategies, extraction, deduplication within a batch, scan progress, deterministic organisation and content-quality checks.
- Keep scan history by batch. Retain full evidence for the latest five batches as currently requested; retain non-sensitive scan metadata/configuration/health for older batches. Export before pruning; show clearly when text is no longer retained and prohibit a misleading complete export.
- Navigation target: Home (numbered steps), Source Configuration, Run Scan, History & Export. No Current Framework, Recommendations or Ask AI page.
- Step 1: review enabled sources. Step 2: run scan (always evidence-only). Step 3: review unhealthy sources and sample actual text. Step 4: download public evidence package. Step 5: transfer via approved route and use government assistant guide.
- Source health distinguishes request failures, access blocks, empty/noisy content, duplicates and useful evidence. Counts alone are not proof of quality. Keep manual URL changes and non-AI advice such as use an official programme page, inspect access restrictions, or disable with a reason. Never bypass CAPTCHA/login/robots restrictions. Do not invent replacement URLs.

### Handover package contract (planned, not existing export format)

- `manifest.json`: schema_version, batch_id, export timestamp/timezone, scan times/status, file names, byte sizes, SHA-256 digests, total/part evidence counts, excluded/missing counts, text-retention/completeness status, warnings and organisation coverage. A checksum detects mismatch; it is not proof of trustworthy authorship.
- `evidence_part_001.json` etc.: schema_version, batch_id, part index/count, and full evidence records with batch-scoped stable evidence ID, source ID, configured URL, final URL, source name, organisation, country, source family/type/label, title, publication date (or null), fetched time, full extracted text, extraction method and quality warnings. Split on evidence boundaries within tested portal limits. Do not silently truncate or omit long documents; explicitly segment/link them if necessary. Unknown metadata stays unknown.
- `sources.json`: immutable public source configuration used by the batch, explicitly allowlisted fields only (not current mutable source settings).
- `source_health.json`: per-source discovery/extraction counts, failures, quality issues and deterministic manual-review advice. Sanitise errors; never export headers, cookies, tokens, user directories or raw tracebacks.
- `organised_scan.json`: COMPLETE record index by organisation/type and evidence IDs, with counts. Optional short summaries labelled as summaries, not a substitute for full evidence.
- `HANDOVER.md`: simple upload order, batch/part checklist, field definitions and warnings. Officer-friendly public evidence index CSV optional; neutralise spreadsheet formula prefixes.
- Offer individual portal-compatible files; ZIP may be offered for approved transport but must not be assumed readable by the assistant. Package size and split limits must be configurable after testing portal constraints.
- Allowlist export data. Exclude database files, `.env`, keys, operational logs, local paths, framework snapshots/files, recommendations, chats, previous AI raw exchanges and all legacy fallback content. Existing `_serialise_batch` is NOT this safe export and must not be reused wholesale.
- Current `EvidenceOrganiser.build` samples six items per bucket and snippets of 350 characters. Replace/extend its export path to enumerate all IDs and full evidence parts; keep UI sampling only for performance.

### Government assistant scope

Setup, copyable instructions, starter message and staged user prompts are in `government_assistant_guide.md`. Read schema/parts first, normalise all accessible public evidence with citations, map the uploaded framework including Cap Area and Definition, then compare only STE competencies. Distinguish organisation-explicit claims from analytical inference. Report actual coverage; file upload/search does not guarantee full model-context ingestion.

Prioritise new sub-functional areas, new competencies, well-supported obsolete-competency deletion, then amendments; present outlier signals separately. Up to 20 justified actionable recommendations, not a quota. Support breadth target up to 10 distinct relevant evidence items where available, never fabricate or pad. No deletion based only on silence or non-discovery. Deliver human-readable report, structured recommendation JSON and coverage/provenance record inside the government environment. Government assistant does not overwrite the framework.

Default portal setup: Hansard/SingStat connectors off, public web search off, narrowly permissioned knowledge sources only, file creation/data analysis on if approved and available. Closed-evidence analysis avoids mixing untraceable search results or exposing framework context through public search. Test actual file processing, context coverage and file generation; do not assume the supplied Fast model can handle a full batch reliably. Model choice and limits require portal/IT validation.

### Implementation tracker / current pointer

- [x] Record new architecture, security boundary and superseding priority.
- [x] Inspect current entry point/export/organiser and document coupling and sampled-export risks.
- [x] Draft officer workflow and government assistant instructions/prompts.
- [ ] NEXT: confirm the working path of the duplicate repository before destructive runtime/database cleanup. No repository-copy path was supplied; this document change is in the current workspace.
- [ ] Refactor collector service composition and scan workflow to have no framework or LLM dependency; remove recommendation imports from scan/health/export helpers, not only sidebar links.
- [ ] Replace Home/Run Scan/History with the numbered collection-only journey; preserve paginated evidence and health review. Remove current-framework UI, recommendation generation, Ask AI and AI URL-remediation/fallback UI and services.
- [ ] Implement versioned, allowlisted public-only package exporter with complete evidence enumeration, size-aware parts, manifest and integrity/coverage checks.
- [ ] Separate collector SQLite schema and operational logs from legacy internal framework/recommendation/chat data. Inventory legacy data; request explicit confirmation and verify backup/target before purging or rebuilding. Do not copy old sensitive data into supposedly public archives. Keep source identities/configuration and requested scan history where safe.
- [ ] Remove AI dependencies/configuration checks from collector install and system/maintenance reports. Keep public scan operational diagnostics, never internal prompts or credentials.
- [ ] Tests: collector boots/scans/exports without AI key or framework; all expected IDs exported exactly once; counts/hashes agree; no internal fields/secrets/local paths; pruned/partial batches correctly labelled; source snapshots immutable; five-batch retention and URL edits still work; PDF/error regressions preserved.
- [ ] Officer checkpoint: UI collection-only, small public pilot export, IT-approved transfer, government assistant ingestion/coverage and downloadable report test using non-sensitive sample framework.
- [ ] Scale checkpoint: full enabled-source scan, multipart ingestion, citation spot-check, incomplete-context handling and archive reproduction; record portal-tested limits and acceptance results.
- [ ] Update README/maintainer handover to match implemented state; archive contradictory legacy design sections after migration.

The older source-tuning checkpoint is paused, not forgotten: retain the accumulated EMA/IET and other source changes and validate them in the next collector-only scan. Do not mark government-portal integration or runtime removal complete based on documentation alone.

This document captures the architectural direction for the prototype so future development can follow the same plan without re-reading the original prompt.

## Purpose

Build a structured, human-governed competency intelligence system for STE workforce planning. The system should collect multiple kinds of public evidence, preserve provenance, and let an approved LLM reason against the current competency framework.

The system must remain:

- simple
- maintainable
- explainable
- modular
- locally runnable
- auditable
- human-governed
- suitable for a restricted government development environment

## Core principle

This should not become “a scraper that asks an LLM what competencies exist.”

It should become:

“A structured competency intelligence system that collects multiple types of authoritative evidence, preserves their meaning and provenance, and allows an approved LLM to reason against the existing competency taxonomy under human governance.”

## Recommended crawling strategy

The preferred design is a hybrid:

1. deterministic crawler first
2. structured extraction / cleanup second
3. LLM normalization and organisation third

The target pipeline is:

1. crawl each configured source deterministically where possible
2. send the fetched page data to the approved LLM to organise it into a clean structure of competencies, courses, programmes, standards, reports, and related STE evidence
3. if a source is messy but still useful, let the LLM normalise the extracted content into the same structure
4. if the crawler returns nonsensical or low-value text for a source, let the LLM perform a more semantic source-level recovery pass for that organisation and then organise the recovered material into the same structure
5. compare the consolidated structured evidence against the current competency framework
6. generate recommendations from that comparison

In practice:

- use the crawler to retrieve the source pages directly
- preserve URLs, titles, structure, and provenance in Python
- use the LLM to organise messy content into competencies, courses, programmes, and comparable structured ideas
- use the LLM to recover and structure content from sources that do not crawl cleanly but are still worth keeping
- use the LLM again later to compare that structured evidence against the current framework

Why this is preferred:

- better auditability
- better provenance
- lower risk of hallucinated sources
- easier debugging
- easier human review
- more stable over time
- better handling of messy but still valuable institutional pages

Using the LLM as the primary web crawler is possible in some cases, but it is not the preferred default for this prototype because:

- it is more expensive
- it is less deterministic
- it is harder to audit exactly what was discovered
- it can weaken provenance
- it can make troubleshooting difficult when a source changes

That said, the LLM can still help where the page structure is messy or where a source already contains a lot of text but not a clean structure. In those cases, the model may assist with semantic organisation after the page has been fetched and cleaned.

The intended division of labour is:

- crawler: fetch and preserve evidence
- LLM step 1: organise source material into a clean STE evidence structure by organisation
- LLM step 2: compare the consolidated evidence against the current competency framework
- recommendation layer: propose new sub-functional areas first, then new competencies, then removals, then amendments

## Fallback rule when deterministic crawling struggles

If a designed crawler fails or performs poorly for a specific source, the blueprint allows an LLM-assisted fallback for that source.

Examples of crawler failure or poor fit:

- network errors or unstable access
- website structure changes
- cookie walls or repeated consent barriers
- nonsensical or noisy extraction
- sites that hide the useful information behind unpredictable layouts
- sites that are clearly easier to read semantically than to crawl structurally

The intended operating rule is:

1. If the website has a clean, stable structure, use deterministic crawling and extraction.
2. If the website is messy, brittle, or structurally hard to extract, use LLM-assisted crawling / interpretation for that source.
3. If a source starts as a good crawler target but later becomes unstable, downgrade it to the fallback approach rather than forcing a fragile crawler to keep failing.

This lets the system remain practical:

- structured sources stay cheap and reproducible
- messy sources still remain usable
- officers still receive a useful source catalogue

The fallback should still preserve provenance as much as possible:

- source URL
- fetched page URL
- organisation
- source type
- source family
- retrieval timestamp

Even when the LLM helps, the system should still keep the raw source links and extracted outputs auditable.

### LLM fallback governance and verification strategy

LLM-assisted fallback must not be presented as if it were ordinary crawler evidence.

The product should make the provenance difference obvious to officers:

- deterministic crawler evidence = content fetched and extracted by the app from a configured source URL
- LLM-assisted fallback evidence = content interpreted or recovered by an AI call because deterministic crawling was missing, blocked, messy, or low-value

This distinction should appear wherever officers review source material:

- Run Scan fallback panel
- Current Recommendations supporting sources
- History batch evidence / fallback records
- recommendation packs and exports
- Ask AI context and answers

Recommended labels:

- `Crawler extracted`
- `LLM assisted`
- `Needs verification`
- `Verified by URL`
- `Access blocked`
- `Low confidence recovery`

Governance rule:

1. Never silently merge LLM-assisted fallback outputs into normal `evidence` rows.
2. Store LLM fallback outputs separately, e.g. in `fallback_recoveries`, with raw JSON result, source URL, organisation, timestamp, confidence, and recovery notes.
3. Require the model to return exact source URLs for every recovered item.
4. Reject fallback outputs without valid URLs.
5. Treat fallback outputs as lower-assurance until a human officer or deterministic follow-up fetch verifies the cited URL.
6. If the LLM says it recovered something from a source but the system cannot later fetch or display the cited URL, flag it as `Needs verification` or `Access blocked`, not as confirmed evidence.
7. Recommendation generation should prefer deterministic crawler evidence first. LLM-assisted fallback can support recommendations, but the recommendation UI must show that the support includes AI-assisted material.

How to reduce wrong-answer risk:

- Strict fallback schema: require title, organisation, source URL, evidence class, confidence, explicit/inferred status, and recovery notes.
- URL validation: only accept HTTPS URLs and reject malformed or clearly invented URLs.
- Domain guardrails: compare returned URLs with the intended organisation/source domain where possible.
- Confidence threshold: flag low-confidence recovered items and avoid using them as primary support.
- Human review: give officers a visible badge and direct link so they can inspect the cited page.
- Operational logs: record fallback prompt, raw response, parsed result, validation errors, and token usage for backend audit.
- Source-health linkage: retain the reason fallback was used, e.g. 403, Cloudflare, cookie wall, timeout, no article links, or nonsensical extraction.

Future verification enhancement:

- Add an optional deterministic post-fallback URL verification step.
- For each LLM-recovered URL, the app attempts a lightweight fetch of the cited URL.
- If fetch succeeds and enough text is extracted, mark the item `Verified by URL`.
- If fetch fails due to 403, robots, Cloudflare, timeout, or cookie wall, mark `Access blocked`.
- If the URL is reachable but does not contain text matching the recovered claim, mark `Needs manual review`.
- Store this verification result alongside the fallback recovery record and display it in Recommendations and History.

Recommended officer-facing explanation:

> Some sources could not be crawled directly, so the system used an AI-assisted recovery pass. These items are clearly labelled as LLM assisted. Please treat them as lower-assurance until the cited source URL is reviewed or verified.

This keeps the fallback useful without pretending that AI-recovered material has the same audit strength as deterministic crawler-extracted evidence.

### Source-maintenance recommendations during fallback

The LLM fallback stage should eventually do two jobs, not just one:

1. recover useful STE competency/course material where deterministic crawling failed; and
2. assess whether the configured source URL itself still looks healthy, current, and suitable.

For failed, blocked, obsolete, nonsensical, or low-yield sources, the fallback output should be allowed to produce a separate source-maintenance recommendation. This is not a competency recommendation. It is a catalogue-quality recommendation for officers or backend maintainers.

Possible source-maintenance recommendation types:

- keep current source
- replace current URL with one or more better candidate URLs
- disable or remove source from the prototype
- needs IT access review
- use browser rendering
- use PDF/resource-hub extraction
- use deterministic crawler only
- use governed LLM fallback only

Each source-maintenance recommendation should include:

- current configured URL
- organisation
- source family, source type, source role, and country
- crawler failure reason, e.g. 403, timeout, cookie barrier, noisy text, no article links, or obsolete listing
- recommended replacement URL(s), if any
- reason the replacement URL is likely better
- confidence
- whether the recommendation came from deterministic source-health rules or LLM-assisted fallback
- timestamp and operational-log reference where available

The Recommendation page can show these as a separate "Source health / link improvement" panel so officers can see whether a source is still valid. However, source-maintenance recommendations must not silently edit `config/sources.yaml`. Officers should explicitly review and apply changes through Source Configuration.

### Anti-crawler, cookie, Cloudflare, and access-limit strategy

The deterministic crawler should use reasonable, IT-explainable methods before falling back to AI recovery:

- respectful request headers and a clear user agent
- robots.txt checks where applicable
- bounded retries and timeouts
- source-specific listing URLs rather than broad home pages
- RSS feeds, sitemaps, public APIs, or structured index pages where available
- optional Playwright browser rendering for JavaScript loading, scrolling, and ordinary cookie-consent handling where permitted
- PDF discovery and PDF text extraction for official reports, standards, guidelines, and catalogues
- IT-approved proxy, TLS certificate, and Zscaler configuration when deployed on managed government laptops

Hard limits should be documented rather than hidden:

- do not bypass Cloudflare/security challenges, CAPTCHAs, paywalls, login walls, or robots restrictions
- do not scrape authenticated pages unless the agency explicitly approves the credentialed access pattern
- do not pretend blocked deterministic access was successful
- if the source remains blocked, mark it as `Access blocked`, explain the likely reason, and route it to source-health review or governed LLM fallback if appropriate

When anti-crawler or cookie restrictions prevent reliable extraction, the app should record the reason in source health, fallback candidates, operational logs, and IT documentation. This gives future maintainers a defensible explanation for why a source is deterministic, browser-rendered, LLM-assisted, or removed.

## Current evidence acquisition emphasis

The most useful public evidence for this prototype is usually not general news.

The crawler should preferentially seek pages that explicitly describe:

- competencies
- skills frameworks
- course catalogues
- training catalogues
- certification programmes
- research programmes
- technology/resource hubs
- structured topic directories
- standards or guidance documents

These sources are more directly useful than casual articles or job listings because officers can clearly see what an organisation explicitly offers, defines, or recognises.

In practical terms, the crawler should be biased toward:

- FRAMEWORK pages for direct competency definitions
- CATALOGUE pages for courses, programmes, and training offers
- INDEX pages for capability or research hubs that link to richer child pages
- TREND pages only when they materially validate a future capability direction
- ARTICLE pages only as a fallback or supporting source family

The default strategic order should therefore be:

1. framework / standards pages
2. course / programme catalogues
3. resource / research indexes
4. trend validation pages
5. general articles as supporting evidence

## Business objective

The application should help identify:

- emerging competencies not currently represented
- new competencies under existing sub-functional areas
- candidate new sub-functional areas
- competencies whose scope needs expansion
- overlaps / merge opportunities
- long-term trends that may indicate future needs

The AI only recommends. Humans decide.

## Scope of sources

This prototype should focus on Science, Technology, and Engineering (STE) sources only.

The main source families are:

1. professional bodies
2. institutes of higher learning
3. government agencies

The crawler should prefer explicit competency, framework, course, programme, standards, and research-hub pages within those families.

## Source types

The blueprint defines explicit source types:

- FRAMEWORK
- CATALOGUE
- INDEX
- TREND
- ARTICLE

### FRAMEWORK

Explicit competency frameworks, skills frameworks, or professional capability taxonomies.

### CATALOGUE

Repeated structured records such as courses, certificates, microcredentials, programmes, workshops, or training pathways.

### INDEX

Hub pages that link to child pages containing useful capability information. These require bounded traversal.

### TREND

Technology outlooks, foresight reports, and trend material used mainly to validate emerging signals.

News and publication pages can also contribute here as supporting signal evidence. They should not be the primary source class, but they can:

- reinforce an emerging pattern already seen in stronger sources
- highlight outlier topics that appear repeatedly across several reputable organisations
- support the LLM when it needs to understand what is getting attention across the STE landscape

In other words, news/publication content is useful as signal evidence, not as the main source of competency truth.

### ARTICLE

Traditional article / publication pages using main-text extraction.

## Core source families

### 1) Professional bodies

These are the highest-value sources when they publish explicit skills frameworks, standards, competency models, surveys, or course catalogues.

Representative organisations:

- IEEE
- IET
- NSPE
- Royal Academy of Engineering
- Engineering Council UK
- Engineers Australia
- Engineers Canada
- Institution of Engineers Singapore (IES)
- ASME
- ASCE
- SWE
- ISA
- INCOSE
- PMI
- ISACA
- (ISC)²
- ACM
- BCS
- AAAI
- SPE
- ACS
- RSC
- AIAA
- Optica
- SPIE
- BMES

### 2) Institutes of higher learning

These are useful when they publish explicit course catalogues, continuing education catalogues, research capability pages, research institutes, technology programmes, or skills-related initiatives.

Representative organisations:

- National University of Singapore (NUS)
- Nanyang Technological University (NTU Singapore)
- Singapore Management University (SMU)
- Singapore University of Technology and Design (SUTD)
- Singapore Institute of Technology (SIT)
- Singapore University of Social Sciences (SUSS)
- University of Oxford
- University of Cambridge
- Harvard University
- Massachusetts Institute of Technology (MIT)
- Stanford University
- University of California, Berkeley
- relevant NUS schools, centres, and institutes
- relevant NTU centres, institutes, and PACE / professional education pages

### 3) Government agencies

These are important when they publish technology programmes, capability roadmaps, research initiatives, standards guidance, outlooks, or training / workforce material.

Representative Singapore agencies:

- GovTech
- DSTA
- DSO National Laboratories
- A*STAR
- IMDA
- SkillsFuture Singapore
- Workforce Singapore
- PUB
- NParks
- National Research Foundation (NRF)
- Enterprise Singapore

Representative overseas agencies:

- NIST
- NASA
- NSF
- DARPA
- DOE
- UK DSIT
- UKRI
- Innovate UK
- DSTL
- CSIRO
- OECD
- World Bank
- European Commission / JRC

## Source role

Source type and source role are different.

Suggested roles:

- PRIMARY_DISCOVERY
- SUPPORTING_DISCOVERY
- TREND_VALIDATION

## Evidence model

Evidence should preserve what kind of information it is, not just where it came from.

Useful evidence categories include:

- EXPLICIT_COMPETENCY
- COURSE
- CERTIFICATION
- RESEARCH_CAPABILITY
- TECHNOLOGY_TOPIC
- TREND_SIGNAL
- ARTICLE_TEXT
- PROFESSIONAL_RESOURCE

The explicit vs inferred distinction matters:

- explicit = the source literally identifies a competency/skill
- inferred = the source implies a competency indirectly

## Architecture direction

The architecture should be layered:

- Streamlit UI
- workflows
- repositories
- domain models
- scanner / discovery
- extractor
- LLM prompt + response validation
- SQLite persistence

## Discovery and extraction

The blueprint recommends a source-type router:

- FRAMEWORK → hierarchy extraction
- CATALOGUE → repeated record extraction
- INDEX → bounded traversal
- TREND → trend-friendly discovery / validation
- ARTICLE → article text extraction

Principles:

- preserve structure where possible
- keep provenance
- avoid universal one-size-fits-all scraping
- use deterministic Python for structure
- let the LLM reason semantically later

### Discovery bias

When discovering candidate URLs, the crawler should prefer links whose text or path suggests:

- competency
- skill
- framework
- course
- programme
- training
- certificate
- curriculum
- standard
- guidance
- resource
- research
- initiative
- hub
- library

This bias is especially important for FRAMEWORK, CATALOGUE, and INDEX source types.

### Source family prioritisation

When choosing root URLs or discovery targets, prefer pages that make the evidence type obvious:

- competency frameworks
- skills surveys
- standards pages
- course catalogues
- professional education pages
- research programmes
- technical resource libraries
- topic directories
- initiative / hub pages

General news pages should only be used when they are the best available supporting source or when a site offers no clearer competency-oriented page.

## Geography and relevance

Preserve:

- country
- region
- whether the source is Singapore-based
- source role
- source type

Singapore evidence should be weighted more strongly than global evidence, but global evidence still matters for corroboration and trend validation.

## Recommendation logic

The LLM should support:

- NEW_COMPETENCY
- NEW_SUB_FUNCTIONAL_AREA
- EXPAND_COMPETENCY
- MERGE_RECOMMENDATION
- DEPRECATION_CANDIDATE
- ALREADY_COVERED
- INSUFFICIENT_EVIDENCE

The model should:

- analyze the full framework
- analyze the full evidence corpus
- prefer multi-source corroboration
- avoid restating already covered competencies
- propose new STE areas and not just edits to what already exists
- support suggestions with multiple evidence IDs where possible

## LLM prompt and reasoning policy

The LLM should be used in a way that helps organise and compare STE competency information, not merely summarise text.

The prompt should instruct the model to:

1. Prefer explicit competency/course information when the source already provides a clean list.
2. If the source is not already structured, infer and organise the content into competency and course concepts tied to the organisation.
3. Once the source content is cleanly structured, compare it against the current competency framework.
4. Generate recommendations in the following priority order:
   - new sub-functional area
   - new competency
   - obsolete competency candidate for deletion or deprecation
   - amendment to an existing competency, such as a name change or definition change
5. Consider only STE competencies and STE-related source content.

The model should not wander outside the STE domain.

The model should preserve provenance:

- what the source said
- how the content was structured
- whether the result was explicit or inferred
- which organisation the evidence belongs to

## LLM-assisted source interpretation

The LLM should not replace the crawler.

Instead, it should help in two stages:

### Stage 1: structure messy content

If a source page is not already a clean framework or catalogue, the LLM may help interpret the cleaned text into:

- competency-like concepts
- course-like concepts
- programme-like concepts
- research capability concepts
- trend themes

This is a semantic structuring step, not a web crawling step.

### Stage 1b: LLM-assisted fallback crawling / interpretation

For sources that are too messy or brittle for deterministic crawling, the LLM may be used to help:

- identify which page sections matter
- extract likely competency or course entries
- reorganise unstructured text into a useful competency/course form
- explain whether the source looks like a framework, catalogue, index, or trend source

This is a fallback mode for hard sources, not the default for all sources.

### Stage 2: compare against the framework

Once the source content is structured, the LLM compares it against the current competency framework and recommends:

- new sub-functional areas
- new competencies
- outlier signals worth monitoring
- obsolete candidates
- amendments to existing competencies

Recommendation priority should remain:

1. new STE sub-functional area;
2. new STE competency within an existing or proposed area;
3. outlier STE signal worth monitoring;
4. obsolete competency candidate;
5. amendment to existing competency name or definition.

Outlier signal recommendations should be treated differently from direct framework-change recommendations. They are useful when a credible organisation, institute of higher learning, or government agency starts showing a new combination of courses, capabilities, or research themes that is not yet common across the wider source pool. These should be labelled as signals or monitoring items, especially when they appear repeatedly across a small number of reputable sources, e.g. 3 to 5 times, but are not yet broad enough to justify immediate framework change.

Obsolete competency deletion should be conservative. Absence of recent evidence is not enough. A deletion/deprecation recommendation should only appear when there is sufficient positive evidence, such as official replacement by a newer standard, explicit discontinuation of a course/certification, repeated removal from authoritative competency frameworks, or strong evidence that the competency has been superseded by another competency. The system should never automatically delete framework rows; it should only surface a human-review recommendation with supporting URLs.

## Dedicated recommendation and question interface

The product should include a dedicated recommendation page for the current scan before the long-term history page.

That page should let officers:

- review the current scan recommendations first
- inspect the evidence and framework snapshot that produced them
- ask follow-up questions about the scan
- request more evidence
- challenge or disagree with recommendations
- explore outlier signals further

The question interface should submit the relevant batch context together with the user query, including:

- the scanned evidence from the current run
- the current competency framework used for comparison
- the organised structured scan results
- the AI recommendations already generated
- the saved Ask AI question-and-answer history for that recommendation batch
- the provenance for the evidence referenced in the answer

This keeps the assistant grounded in the exact batch being reviewed and avoids context drift across scans.

### Ask AI context-memory strategy

The Ask AI function should be designed as a batch-grounded assistant, not as an uncontrolled general chatbot.

Current technical behaviour:

- Each Ask AI submission is a fresh OpenAI API request.
- The model does not automatically remember prior questions unless the application sends those prior questions again.
- The prototype stores Ask AI questions and answers in `batch_questions`, linked to the recommendation batch.
- Saved Q&A is displayed and exported for audit, but the application must deliberately decide how much of that prior transcript to send into future Ask AI requests.

Officer-facing product expectation:

- Users may naturally treat Ask AI like a normal chatbot and expect it to remember earlier follow-up questions.
- The UI should therefore make the scope clear: Ask AI remembers the selected/current recommendation batch, not the user's entire app history.
- The answer should stay grounded in the scan batch, framework snapshot, organised scan, recommendations, supporting evidence, source-health diagnostics, fallback records, and prior Q&A for that same batch.

Recommended implementation direction:

1. Short-term: include recent saved Q&A turns for the same recommendation batch in every new Ask AI context.
   - Include question, answer, timestamp, and batch ID.
   - Keep this bounded, e.g. latest 5 to 10 Q&A turns, to avoid uncontrolled context growth.
   - Tell the model to use prior Q&A only as conversation context and not as new evidence.
2. Medium-term: add a per-batch conversation summary.
   - After several Q&A turns, summarise the discussion into a compact batch conversation memory.
   - Store that summary separately from the raw transcript.
   - Send the summary plus the latest raw turns in future requests.
3. Long-term: add explicit UI wording and controls.
   - Show a small note such as “Ask AI uses this recommendation batch plus saved questions from this batch.”
   - Add a “Clear conversation context for this batch” option if users want future answers to ignore previous Q&A while keeping the audit transcript.
   - Consider showing “Context sent: batch evidence preview, recommendations, framework snapshot, source health, fallback records, recent Q&A” for transparency.

Context-window and cost guidance:

- Do not send unlimited full evidence text or unlimited chat history.
- Continue sending compact evidence previews and support summaries.
- Prefer structured summaries over raw long transcripts once the Q&A history grows.
- Keep provenance separate from conversation memory: prior Q&A may clarify the discussion, but recommendations must still cite original evidence IDs, URLs, organisations, source family/type/role, and framework snapshot.
- Log the final prompt/context and raw response in backend operational logs with secret redaction so IT can diagnose context-size, cost, or answer-quality issues.

This keeps the crawler simple while still allowing the model to add value where the source is not already neatly structured.

## Database philosophy

Keep SQLite as the local store.

Store:

- source configuration
- scan runs
- evidence
- framework versions
- competencies
- recommendation batches
- recommendations
- audit / provenance information

Do not turn SQLite into a raw webpage archive.

## Backend operational logging and IT maintainability

The system should include a backend-only operational logging layer so future IT specialists can maintain, troubleshoot, and tune the prototype after handover.

These logs are different from officer-facing History pages. Officers should see clean scan batches, recommendations, source health, and supporting URLs. Backend engineers should additionally be able to inspect the technical exchange of information that happened inside the system.

The logging layer should capture timestamped, structured records for:

- application startup, database migration, and configuration loading events
- scan start time, end time, status, duration, and selected scan options
- the full source configuration snapshot used for a scan
- how many sources / websites were enabled and scanned
- per-source crawler results, including:
  - source name, organisation, source URL, source family, source type, source role, country, crawler strategy, and whether browser rendering was used
  - listing pages attempted
  - URLs discovered
  - URLs skipped and why, such as duplicate within scan, utility URL, low word count, disallowed by robots.txt, timeout, HTTP error, PDF extraction failure, or unsupported content
  - evidence items stored for that source
  - source-level errors and warnings
  - source-level duration
- total evidence scanned and retained for each batch
- organised scan summary inputs and outputs, including organisation-level competency / course / research / signal groupings
- LLM recommendation requests, including:
  - timestamp
  - model name
  - endpoint or API method used
  - prompt / request payload sent to the AI
  - raw response received from the AI
  - parsed recommendations
  - validation or parsing errors
  - token usage and estimated cost where available from the API
- Ask AI batch-question requests, including:
  - timestamp
  - batch ID
  - user question
  - compact context sent to the AI
  - raw response
  - displayed answer
- future LLM fallback recovery requests and responses when live fallback calls are implemented

Security and governance guardrails:

- Logs are for backend engineers and should not be shown in normal officer UI by default.
- Logs may contain prompts, AI responses, framework snapshots, evidence excerpts, and troubleshooting metadata, so they should be stored in a backend-only location with appropriate filesystem or deployment access controls.
- Never log API keys, proxy credentials, authentication tokens, or other secrets.
- Add secret-redaction before writing any request headers, environment variables, or connection details.
- Prefer structured JSONL logs or dedicated SQLite audit tables so IT staff can filter by timestamp, batch ID, source, status, or request type.
- Add log rotation / retention rules so troubleshooting records do not grow indefinitely.
- UI timestamps can remain officer-friendly (`YYYY-MM-DD HH:MM`), but backend logs should use an explicit timezone-aware timestamp standard for traceability.

This logging workstream should make it possible for a future maintainer to reconstruct:

- what a scan attempted
- why a source produced weak or no evidence
- what exact prompt was sent to the LLM
- what raw response came back
- how the raw response became officer-facing recommendations
- whether a bug came from crawling, extraction, organisation, prompting, response parsing, persistence, or UI display

## UI direction

The UI should eventually show:

- source type
- source role
- source family
- country
- evidence type
- explicit / inferred state
- batch history
- framework snapshot download
- evidence filters

The source configuration page should stay officer-friendly and simple, with advanced options tucked away.

The History page should mirror the same source-family tagging used in Source Configuration so officers can immediately see whether evidence came from:

- professional bodies
- higher learning
- government agencies

Because the crawler is now more explicitly oriented toward competencies, courses, programmes, standards, and research hubs, the older evidence-type labels should remain visible but should be treated as secondary detail. They are still useful for audit and filtering, but the primary visual emphasis should be on:

- source family
- source type
- source role
- organisation
- evidence provenance

## Testing direction

Phased tests should cover:

- source routing
- article extraction
- catalogue extraction
- framework extraction
- index traversal
- persistence
- failure isolation
- LLM prompt / schema validation

## Delivery progress tracker

Use this as the live checklist for the prototype.

- [x] Core Streamlit app and batch history model
- [x] Source routing by source type
- [x] Framework extraction with hierarchy preservation
- [x] Catalogue extraction for repeated record-style content
- [x] Index discovery with bounded traversal
- [x] Trend discovery path
- [x] Evidence typing and explicit / inferred tracking
- [x] LLM prompt and schema for structured recommendations
- [x] Batch history page with downloadable evidence and framework snapshots
- [x] Source family model for professional bodies / higher learning / government agencies
- [x] Finalise source family assignment for all configured sources
- [x] Tune source roots toward explicit competency, course, programme, standards, and research-hub pages
- [x] Add per-source crawler strategy status in Run Scan
- [x] Add evidence-type and source-family filters across the app
- [x] Add more source-specific adapters only where needed
- [x] Add configuration-driven source strategy inference for sources without explicit type or role
- [x] Update recommendation prompt to use the richer structured source-family and evidence-type signals even more strongly
- [x] Add dedicated current-scan recommendation page before History
- [x] Add user question interface with batch-grounded LLM context
- [x] Add saved question history for the current recommendation batch
- [x] Include bounded prior Ask AI Q&A context in future Ask AI requests for the same recommendation batch
- [x] Add per-batch Ask AI conversation summary once Q&A history becomes long
- [x] Add officer-facing Ask AI memory/scope note explaining that context is limited to the current recommendation batch
- [x] Treat news/publication pages as supporting outlier signals rather than primary sources
- [x] Add deterministic organised scan context before recommendation generation
- [x] Show the deterministic organised scan map in History for officer inspection
- [x] Add organised scan JSON download for historical batches
- [x] Enrich organised scan export with source family, source type, source role, and country metadata
- [x] Add collapsed representative-item review panel for each organisation in the organised scan
- [x] Add officer-facing recommendation support summary tables
- [x] Add fallback provenance counts for retained/pruned evidence batches
- [x] Add source-family/source-type/source-role badges to fallback supporting URLs
- [x] Add recommendation summary and support-profile metadata to the current-batch Ask AI context
- [x] Make the current-batch Ask AI context JSON-safe, including framework metadata and saved framework snapshot
- [x] Smoke-test the live Ask AI flow in Streamlit with the configured OpenAI API key
- [x] Add visible waiting feedback while Ask AI is processing a batch question
- [x] Add compact current-batch recommendation pack export for supervisor review
- [x] Add human-readable Markdown recommendation pack export for supervisor review
- [x] Add JSON and Markdown recommendation pack exports to historical batches
- [x] Add CSV recommendation summary exports for spreadsheet review
- [x] Harden Markdown recommendation exports against table-breaking characters
- [x] Add source provenance metadata to recommendation-pack supporting-source bullets
- [x] Use human-readable recommendation type labels in officer-facing UI and Markdown exports
- [x] Standardise source type and source role badges as human-readable labels in recommendation evidence displays
- [x] Add evidence IDs and titles to recommendation-pack supporting-source entries
- [x] Show evidence IDs in recommendation supporting-source and raw evidence UI expanders
- [x] Add recommendation support coverage tables by source family and organisation
- [x] Add CSV exports for recommendation support coverage tables
- [x] Include support coverage tables in recommendation pack JSON and Markdown exports
- [x] Include support coverage in Ask AI batch context
- [x] Bound Ask AI evidence context using compact article previews instead of full article text
- [x] Add Ask AI preview transparency metadata for truncated evidence text
- [x] Add officer-friendly Ask AI question starters for common batch review tasks
- [x] Add focused Ask AI Q&A history exports in CSV and Markdown for current and historical batches
- [x] Store and display Ask AI chat history for each recommendation batch on the History page
- [x] Add historical source-health table to identify healthy, low-output, no-evidence, and error sources
- [x] Add CSV export for historical source-health reviews
- [x] Add compact source-health status metrics in History
- [x] Add source-health suggested actions for crawler tuning and LLM fallback triage
- [x] Add status filtering for historical source-health review
- [x] Show immediate source-health summary on Run Scan after a scan completes
- [x] Include source-health diagnostics in batch evidence JSON exports
- [x] Include source-health diagnostics in current and historical recommendation pack exports
- [x] Show source-health diagnostics on the Current Recommendations page
- [x] Centralise source-health rules into a shared service used by Run Scan, Current Recommendations, and History
- [x] Include source-health diagnostics in Ask AI batch context
- [x] Show latest-scan source-health attention summary on Home
- [x] Add CSV export for latest-scan Home source-attention list
- [x] Add Home validation-checkpoint guidance for UIUX review, full scan, source tuning, and recommendation review
- [x] Refresh README with officer-facing and IT-facing explanation of source health, organised scan, Ask AI context, and fallback-triage design
- [x] Add no-cost LLM fallback candidate planning/export for failed or empty sources where fallback is allowed
- [x] Add no-cost LLM fallback request/prompt preview exports before enabling any live fallback calls
- [x] Include fallback candidates and request previews in Current Recommendations Ask AI context and recommendation packs
- [x] Add deterministic fallback recovery-readiness labels to candidate plans and prompt previews
- [x] Add fallback readiness counts to Run Scan, Current Recommendations, History, exports, and Ask AI context
- [x] Add fallback-readiness filters to Run Scan, Current Recommendations, and History candidate tables
- [x] Add deterministic recommended-next-step guidance to fallback candidate plans and prompt previews
- [x] Centralise fallback-readiness filter options so Run Scan, Current Recommendations, and History stay aligned
- [x] Add organised scan quality summary for structured-heavy / mixed / signal-heavy batches
- [x] Include organised scan quality in Ask AI context and recommendation packs
- [x] Add backend-only operational logging and audit trail for scans, crawler outcomes, source diagnostics, LLM prompts, raw LLM responses, parsing, token usage, and troubleshooting metadata
- [x] Add size-based rotation for backend operational logs so JSONL audit files do not grow indefinitely
- [x] Add read-only IT handover diagnostics for dependency, configuration, database, OpenAI-key-presence, and operational-log readiness checks
- [x] Add backend operational-log summary command for event counts, source scan totals, recent attention events, and LLM usage review
- [x] Add Markdown maintenance report command combining readiness diagnostics and operational-log summary for IT handover
- [x] Add per-source crawler outcomes to backend log summary and Markdown maintenance report for IT source troubleshooting
- [x] Add governed backend LLM fallback recovery adapter with strict JSON schema, provenance checks, response parsing, and operational logging
- [x] Add explicit officer-controlled UI action for selected LLM fallback recovery candidates
- [x] Store recovered fallback items as separate recovery records rather than deterministic crawler evidence
- [x] Add historical display/export of saved fallback recovery records
- [x] Add explicit officer-facing `Crawler extracted` vs `LLM assisted` provenance badges everywhere fallback material can support review
- [x] Add fallback verification status labels such as `Needs verification`, `Verified by URL`, `Access blocked`, and `Low confidence recovery`
- [x] Add optional deterministic post-fallback URL verification service for LLM-recovered source URLs
- [x] Wire deterministic post-fallback URL verification into officer-controlled UI action and persistence
- [x] Add deterministic source-maintenance recommendations for failed, blocked, obsolete, nonsensical, or low-yield source URLs
- [x] Extend source-maintenance recommendations with governed LLM-assisted replacement-URL suggestions during fallback recovery
- [x] Show source-health/link-improvement recommendations on the Recommendation page without automatically changing the configured source catalogue
- [x] Add advisory recommended replacement URLs for failed or obsolete sources, with officer approval/application still handled manually through Source Configuration
- [x] Add High/Medium/Low source-maintenance priority counts to Current Recommendations, History, Ask AI context, and batch exports
- [x] Document anti-crawler, cookie, Cloudflare, robot, proxy, and Zscaler handling limits in source-health UI, README, and IT maintenance notes
- [x] Add an `OUTLIER_SIGNAL_DETECTED` recommendation category/section for repeated but still-emerging STE signals
- [x] Add conservative obsolete-competency deletion/deprecation recommendation logic with a high evidence threshold and human-review wording
- [x] Add Source Configuration catalogue exports for enabled-source review, full IT CSV backup, and YAML source-catalogue backup
- [x] Harden Source Configuration removal so selected sources are removed by URL as well as database ID, and align listing-page UI controls with the 25-page backend limit
- [x] Clear stale pending source-edit drafts after catalogue removal so Streamlit does not compare different-length source lists
- [x] Add safe Source Configuration YAML-backup preview and validation without applying/overwriting the active catalogue

Implementation update:

- Current Recommendations now includes deterministic source-maintenance recommendations derived from source-health rows. These highlight failed, blocked, empty, or low-yield source URLs and suggest review actions such as access review, replacement URL review, fallback review, or article-limit/source-relevance tuning. They are deliberately catalogue-quality recommendations only: they do not modify `config/sources.yaml`, and any source change still requires officer action through Source Configuration.
- History batch review and batch JSON exports now include the same deterministic source-maintenance recommendations, so future reviewers can see which configured links were weak, blocked, empty, or candidates for tuning at the time that historical batch was generated.
- Governed LLM fallback recovery now returns a separate `source_maintenance_advice` object as part of its strict JSON output. This can advise officers to keep the current source, replace the URL, disable the source, request IT access review, enable browser rendering, or use a PDF/resource hub. Any recommended replacement URLs must be exact HTTP(S) URLs and remain advisory only: they are displayed/exported for officer review, but the app does not silently update `config/sources.yaml`.
- Run Scan, Current Recommendations, History, and recommendation-pack exports now surface fallback source-maintenance advice where available, including recommendation type, confidence, reason, and suggested replacement URL(s), so failed or messy crawler sources can produce both recovered STE evidence and a governed suggestion about whether the configured URL itself should be improved.
- Current Recommendations, History, Ask AI context, and batch/recommendation-pack exports now consolidate deterministic source-health recommendations and actionable LLM-assisted fallback source advice into one source-maintenance view. This lets officers review broken, weak, or obsolete source URLs in one place while still seeing whether each suggestion came from deterministic crawler health rules or LLM-assisted fallback advice.
- Source-maintenance sections now show High/Medium/Low priority counts before the detailed table. These counts are also included in Ask AI context and batch/recommendation-pack exports so officers, supervisors, and IT maintainers can quickly see whether a batch has urgent source-catalogue issues.
- Backend log summary and the Markdown maintenance report now include per-source crawler outcomes. IT maintainers can see each source's completed count, failed count, discovered URL count, stored evidence count, and latest error without opening Streamlit or manually scanning the raw JSONL log first.
- Current Recommendations and History now include officer-triggered deterministic URL verification for saved LLM fallback recovery records. The app only fetches recovered URLs when an officer clicks the verification button, then stores verification results back into the recovery JSON payload so future views and exports can show `Verified by URL`, `Access blocked`, `Invalid URL`, or `Needs manual review` evidence status without re-running the check automatically.
- The recommendation schema and prompt now support `OUTLIER_SIGNAL_DETECTED` as a visible monitoring recommendation. The prompt tells the model to use this when a credible organisation shows an unusual or repeated STE course/capability/research/standards signal that is worth monitoring but not yet broad enough to become an immediate framework update. README now explains this distinction for officers and IT reviewers.
- Deprecation/deletion recommendations now have a local guardrail as well as prompt guidance. `DEPRECATION_CANDIDATE` is only kept visible when it cites at least four supporting evidence IDs; weaker deprecation outputs are downgraded to hidden `INSUFFICIENT_EVIDENCE`. The prompt explicitly says not to rely on absence of evidence and to phrase deprecation as human-review only, never automatic deletion.
- Run Scan, Current Recommendations, and History now show a shared access-limit note beside source-health review. The note explains that the crawler may use ordinary requests, source-specific URLs, bounded retries, browser rendering, and PDF extraction where permitted, but does not bypass robots restrictions, Cloudflare/security challenges, cookie walls, logins/paywalls, or managed-network proxy/TLS restrictions. README now carries the same IT-facing boundary.
- Current Recommendations, History, Ask AI context, standalone Q&A Markdown, and recommendation pack exports now include a deterministic per-batch Ask AI conversation summary. The summary records question count, first/latest question time, common review themes, and recent questions without making an additional LLM call.

## Suggested implementation sequence

1. Domain model + enums + database migration
2. Source configuration UI updates
3. Source-type router
4. Article extraction integration
5. Catalogue extraction
6. Framework extraction
7. Index bounded traversal
8. Trend extraction
9. Evidence normalization
10. Integration testing
11. LLM prompt / recommendation pipeline updates
12. Structured source normalisation pass for messy pages
13. LLM-assisted source recovery fallback for crawler failures
14. Source family and evidence type filters / badges across the history UI
15. Evidence-to-recommendation traceability and batch export hardening
16. Dedicated current-scan recommendation page and query interface
17. Backend-only operational logging and IT handover audit trail
18. Optional governed live LLM fallback execution for failed or messy sources
19. Officer-controlled fallback recovery UI and persistence model
20. IT handover diagnostics and maintainability checks

## Notes for future development

Important guardrails:

- do not rebuild the app from scratch
- do not replace working architecture unnecessarily
- prefer the smallest clean extension
- do not hard-code URLs into scanner logic
- keep provenance intact
- one source failure must not stop the whole scan
- continue iterating in phases and run tests after each phase

## Evidence Review Notes

Batch 7 evidence review led to these source-quality fixes:

- Engineering Council UK-SPEC moved from the retired `ukspec.aspx` URL to the current professional engineering competence and commitment page.
- NParks moved from a broken parks activity page to the official Research Programmes page.
- University of Cambridge Research News moved to Cambridge Department of Engineering News to avoid broad animal-research governance pages overwhelming the STE evidence pool.
- Discovery now blocks common utility and placeholder links such as Cloudflare email-protection URLs, social links, contact pages, careers pages, newsletter pages, and generated `[resource:...]` placeholders.

Batch 8 evidence review showed the crawler is now completing cleanly and storing a much larger evidence pool, but some listing and utility pages were still being accepted as evidence:

- Treat pagination URLs such as `?page=2` and Drupal-style filter URLs as navigation only, not evidence records.
- Continue using pagination URLs for discovery queues so multi-page sources still produce deep results.
- Block JavaScript placeholders, taxonomy pages, legal/privacy/contact forms, newsletter pages, and social redirect paths before they reach article extraction.
- Keep the current 25-article / 5-listing-page testing cap while tuning source quality.
- Replace deprecated Streamlit `use_container_width` calls with `width="stretch"` to reduce noisy runtime warnings.

Batch 9 evidence review confirmed that pagination-listing pages were no longer being stored as evidence. Remaining low-value items were narrower utility URLs, so discovery filtering was tightened again:

- Block newsletter pages even when `newsletter` appears inside a longer path such as `department-newsletter`.
- Block legal/privacy pages, social redirect paths including TikTok, IEEE ad privacy pages, and known typo/placeholder URLs.
- Keep skipped-candidate log lines as diagnostic information; they are acceptable when the final batch stores enough useful evidence and completes without an error summary.

Batch 10 evidence review confirmed the scan remains stable at 600+ evidence records with no fatal error summary. A small number of low-value URLs can still slip through when browser/source-specific discovery returns utility links, so scan orchestration now includes a final pre-storage URL hygiene guard for pagination, legal/privacy, newsletter, social, and known placeholder URLs.

Batch 11 evidence review confirmed retention and scan stability remain healthy. Further tuning found nested utility paths and query-filter listing pages:

- Block utility segments anywhere in the path, e.g. `/home/careers/`, `/legal/privacy-statement`, and nested about/contact/privacy pages.
- Block query-filter evidence records such as `?year=2026`, `?category=...`, and `?ucam-ref=...`; these can help navigation but should not be stored as individual evidence items.
- Apply the utility URL guard before fetch, after fetch redirect resolution, and after extraction so redirected privacy/legal/utility pages cannot be stored as evidence.
- Keep the next tuning focus on source roots that produce mostly navigation/corporate pages, especially DSTA/DSO/ASCE pockets, while preserving their genuinely useful STE capability pages.
- Source-specific narrowing added for DSTA and DSO:
  - DSTA Technology Spotlight should keep `/whats-on/spotlight/...` article pages only.
  - DSO Media Centre should keep `/media-article/...` pages only.
  - Browser-rendered discovery now respects configured `article_url_pattern`, not only plain HTML discovery.

Batch 13 evidence review confirmed redirect/utility filtering is active, but broad discovery paths still bypassed URL patterns. Discovery pattern handling was normalised:

- `article_url_pattern` is now applied consistently across generic, paginated, browser-rendered, IEEE, NUS browser, broad news, and resource-hub discovery.
- The workflow no longer treats `career-growth` as utility, preserving NSPE ethics pages while still blocking true `/careers/` pages.
- Next DSTA/DSO check should show mostly `/whats-on/spotlight/...` and `/media-article/...` evidence respectively.

Batch 14 evidence review confirmed DSTA and NSPE are behaving as intended. DSO still allowed two `/assets/docs/...pdf` records because PDF candidates were accepted before `article_url_pattern` was checked. The pattern check now happens before PDF acceptance, and scan snapshots now store backend discovery constraints such as `article_url_pattern` and `use_browser_rendering` for audit.

Batch 15 evidence review confirmed the DSO PDF bypass was removed, but DSO failed because its raw listing page exceeded the response-size limit after browser discovery had already found usable links. Discovery now preserves browser-rendered URLs when the subsequent raw listing fallback fails, protecting messy or oversized sites without weakening source constraints.

Batch 16 evidence review confirmed DSO recovered cleanly with only `/media-article/...` records and no scan error. Next source-quality cleanup narrowed:

- IET Skills Surveys and Reports to the UK skills-survey report path only, removing broad publishing/media hub records.
- ASME Codes and Standards to `/codes-standards/...` only, removing broad topics/resources and unrelated programme pages from that source.

Batch 17 evidence review confirmed scan stability at 641 evidence records with no scan-level error summary. The remaining issue was configuration drift: the IET and ASME path restrictions had been added to earlier duplicate catalogue entries, while the active entries still had blank `article_url_pattern` values. Cleanup applied the restrictions to the active entries and added path restrictions for GovTech:

- GovTech Media and Announcements should keep `/media/...` records only.
- GovTech TechNews and Insights should keep `/technews/...` records only.
- IET Skills Surveys and Reports should keep the UK skills-survey report hub and child report pages only.
- ASME Codes and Standards should keep `/codes-standards` and child standards pages only.

Next scan should check that:

- GovTech no longer stores product/service landing pages under the media or technews sources.
- IET primarily stores skills-survey/report evidence, not publishing/media hub pages.
- ASME primarily stores codes/standards evidence, not broad topic/resource/certification pages.

Batch 18 evidence review showed the scan remained large and mostly stable at 640 evidence records, but the batch completed with one GovTech Media discovery error and still contained older broad GovTech/IET/ASME records. Root cause: `config/sources.yaml` had accumulated repeated source blocks, so some stale definitions could remain active or confusing even after individual patches. Cleanup actions:

- Deduplicated `config/sources.yaml` from 74 source blocks to 44 unique source URLs.
- Fixed accidental pattern drift on AI Singapore and SkillsFuture entries.
- Added code-level default URL scopes for brittle high-value hubs so stale database rows with blank patterns are still constrained:
  - GovTech Media: `/media/...`
  - GovTech TechNews: `/technews/...`
  - IET UK Skills Surveys: the UK skills-survey report path only
  - ASME Codes and Standards: `/codes-standards` and child paths only
- Added a final scan-workflow guard so out-of-scope redirected/extracted evidence is skipped before storage.

Next scan should check whether the SQLite synchronisation retires the old GovTech root-style source row and whether GovTech/IET/ASME no longer store product pages, broad publishing hubs, or broad ASME topic/resource pages.

Batch 19 evidence review confirmed the source-scope guard is working:

- IET now stores 8 UK skills-survey/report records only.
- ASME now stores 8 `/codes-standards...` records only.
- GovTech TechNews now stores 13 `/technews...` records only.
- Broad product/service, publishing, and ASME topic/resource records are skipped as out-of-scope rather than stored.

The only remaining scan-level error was GovTech Media and Announcements, which no longer discovers permitted `/media/...` links reliably. Since GovTech TechNews remains useful and GovTech Media adds an avoidable error, GovTech Media was removed from `config/sources.yaml`. The catalogue now has 43 unique source URLs and no duplicate URL blocks.

Next scan should confirm a clean `COMPLETED` status with no GovTech Media error and roughly 605 evidence records, minus any source volatility.

Batch 20 evidence review confirmed the crawler tuning checkpoint is stable:

- Scan status is `COMPLETED` with no error summary.
- Evidence count is 605.
- GovTech now stores 13 TechNews records only.
- IET remains clean with 8 UK skills-survey/report records only.
- ASME remains clean with 8 codes/standards records only.
- DSTA and DSO remain scoped to their intended article paths.
- Remaining low-priority review items are content-quality judgments rather than crawler failures, e.g. Cambridge career stories and Engineering Council whistleblowing guidance.

This is the current stable baseline for the source crawler. Future source tuning can continue source-by-source, but the general discovery, URL scoping, duplicate-catalogue cleanup, and scan completion behaviour are now acceptable for prototype use.

Recommendation-pipeline update after the stable crawler checkpoint:

- Recommendation generation now builds an `ORGANISED_SCAN` context before calling the LLM.
- The organised scan groups the full evidence batch by organisation into:
  - competencies or standards
  - courses, programmes, or resources
  - research reports or capability evidence
  - supporting signals and topics
- The LLM prompt receives both:
  - `ORGANISED_SCAN`, which gives full-batch coverage across all evidence
  - `SELECTED_EVIDENCE`, which gives a larger balanced citation-ready evidence pack
- This addresses the previous weakness where only the first 20 evidence items were sent to the model. The detailed citation pack is now balanced across organisations and expanded, while the model still sees a compact map of the full scan.
- This is a deterministic intermediate step, not a second paid LLM call yet. It prepares the architecture for the future two-pass flow where the first LLM pass can explicitly organise/recover source material and the second pass can compare it against the framework.

Recommendation-output review after the first organised-scan run:

- Recommendation quality improved: the model produced more substantive gap recommendations with multiple evidence sources.
- The important defect was provenance pairing: some model-generated `supporting_urls` and `supporting_organisations` were valid individually but mismatched as pairs.
- Provenance is now canonicalised from `supporting_evidence_ids`. The application treats evidence IDs as the single source of truth and stores URLs/organisations from the retained evidence records rather than trusting model-paired arrays.
- Recommendations without evidence IDs are rejected because they cannot be audited safely.
- The prompt now asks for 12 to 20 visible actionable recommendations when supported, with more diversity across cap areas and sub-functional areas.

Batch 22 recommendation review:

- The organised-scan approach produced a stronger recommendation set, including more visible recommendations and more new sub-functional area proposals.
- Officer review needs more supporting evidence per recommendation. The system should not stop at 2–3 sources when more relevant evidence exists.
- Supporting source policy:
  - ask the LLM to cite 4 to 10 supporting evidence IDs for each recommendation where available
  - allow fewer than 4 only when fewer genuinely relevant sources exist
  - cap each recommendation at 10 supporting evidence items so the officer review panel remains usable
  - store support using canonical evidence IDs so URLs and organisations remain correctly paired

Batch 23 recommendation review:

- The 4-to-10 evidence-source instruction improved recommendation support without obvious evidence padding.
- Most recommendations now cite around 4 sources where available.
- The recommendation set remains useful and officer-facing, with a strong mix of new competencies, expansions, and new sub-functional area proposals.
- To make the larger support set reviewable, Recommendation and History pages now show support strength in the recommendation expander label:
  - number of cited evidence sources
  - number of supporting organisations
  - number of source family types represented
- Recommendation and History pages also include an officer-facing recommendation summary table above the detailed expanders. The table shows recommendation type, confidence, sub-functional area, competency, supporting source count, supporting organisation count, and source-family count so users can triage quickly.
- If full evidence rows are unavailable because evidence has been pruned or not loaded, the summary table must fall back to the recommendation's stored supporting URLs and organisations. This avoids misleading zero-count support columns while still marking source-family counts as unavailable when the full source metadata cannot be reconstructed.
- The fallback citation display should also match stored supporting organisations back to the configured source catalogue. Where a match exists, older or pruned batches still show source-family, source-type, and source-role badges beside each supporting URL.
- The current-batch question interface now supplies the LLM with the same recommendation summary and support-profile metadata shown to officers. Follow-up answers should use this compact support map first, then cite detailed evidence where needed.
- Live Ask AI smoke testing found that the context originally passed a `FrameworkVersion` object directly, which is not JSON serialisable. The context builder now converts framework metadata into a plain dict and includes the saved framework snapshot from the recommendation batch where available.
- Live Ask AI smoke testing then succeeded: the answer used recommendation support breadth, organisations, source-family diversity, and cited evidence IDs. The UI now shows a spinner while the model is reviewing the batch context so users are not left wondering whether the button worked.
- Test checkpoint after this traceability update: `python -m pytest` collected 44 items and all 44 passed. Live Streamlit validation also confirmed the Ask AI path can call the configured OpenAI API, return a grounded answer, and log the question against the batch.

Recommendation pack export update:

- Current Recommendations now includes compact JSON and Markdown downloads for supervisor review.
- History also exposes the same JSON and Markdown recommendation pack downloads for older recommendation batches.
- Current Recommendations and History include CSV downloads of the recommendation summary table for officers who want to sort/filter in Excel.
- Historical CSV exports use batch-specific filenames so officers can compare multiple batches without overwriting files.
- The pack includes scan and recommendation batch metadata, framework metadata/snapshot, recommendation summary rows, support profiles, cited evidence URLs/organisations, source metadata, and saved Ask AI questions.
- The JSON pack is system-friendly; the Markdown pack is human-readable and can be opened directly or pasted into a note/email.
- Markdown export values are escaped and normalised so pipes and line breaks in competency names, reasons, or source names do not break the summary table.
- Recommendation pack supporting-source entries include organisation, URL, source family, source type, source role, and country where the source can be matched to the catalogue.
- Markdown recommendation packs display recommendation types and source provenance as human-readable labels, while JSON keeps machine-readable enum values.
- Current Recommendations and History display recommendation type labels in human-readable form while preserving backend enum values in JSON exports.
- Source type and source role badges in recommendation evidence displays use readable labels such as "framework" and "primary" instead of exposing raw enum text.
- Recommendation pack supporting-source entries include evidence IDs and titles so officers can cross-reference exported recommendations against History evidence records.
- Current Recommendations and History show evidence IDs in supporting-source and raw evidence expanders, matching the exported recommendation pack cross-reference format.
- Current Recommendations and History show support coverage tables so officers can see whether visible recommendations are supported by a broad spread of organisations and source families or concentrated in a narrow evidence base.
- Support coverage tables are labelled as "Cited evidence by source family" and "Top cited organisations" for clarity.
- Support coverage tables can be downloaded as CSV for spreadsheet review.
- Recommendation pack exports include support coverage tables so supervisor review packs remain self-contained.
- Ask AI receives support coverage tables so follow-up answers about breadth, concentration, or source diversity can rely on precomputed audit counts.
- Ask AI receives compact evidence previews instead of full retained article text, keeping follow-up question payloads bounded while preserving evidence IDs, titles, URLs, organisations, and source metadata for traceability.
- Ask AI evidence previews include preview length, original compacted text length, and a truncation flag so the model can avoid over-claiming details when it only received a preview.
- Current Recommendations includes one-click Ask AI starter questions for common officer review tasks: broadest-supported recommendations, trend/news-heavy recommendations, and genuinely new STE sub-functional area proposals. Starters prefill the question box for editing rather than immediately sending the query.
- Saved Ask AI questions can be downloaded separately as CSV or Markdown from Current Recommendations and History, so officers can share the discussion trail without exporting the full recommendation pack.
- The pack intentionally excludes full article text so it is portable and focused; raw/full evidence remains available through the History evidence export where retained.

Organised scan visibility update:

- History now includes an "Organised scan" section after recommendations and batch configuration.
- It shows each organisation's evidence split into competencies/standards, courses/resources, research/capability, and signals/topics.
- A collapsed review panel lets officers inspect representative retained items for each organisation and bucket without rendering every evidence record by default.
- Evidence count, retention note, and evidence filters are colocated with the Organised scan section so users understand and adjust the organised view without scanning back up the page.
- The Organised scan filters also drive the raw Scan report shown below it, while recommendations remain full-batch to avoid controls below changing recommendation content above.
- Officer-facing explanatory captions in the History page were trimmed once the organised scan layout became self-explanatory; retention policy remains documented in the blueprint rather than repeated in the main UI.
- Officers can download the same organised scan map as JSON for audit or manual review.
- The organised scan JSON export is enriched with organisation-level and item-level source metadata, including country, source family, source type, and source role.
- This makes the intermediate source-understanding layer visible instead of hiding it inside the LLM recommendation prompt.
- History includes a source-health table for each selected batch. It compares every configured source in the batch snapshot against retained evidence counts and scan errors, so officers can see healthy sources, low-output sources, sources with no evidence, and sources that errored. New scan snapshots preserve source IDs and the LLM fallback flag so this table can accurately count evidence and explain whether future fallback recovery is permitted. The section also shows compact status metrics, status filtering, suggested actions, and can be downloaded as CSV for source-tuning review. This is a practical bridge toward future LLM-assisted fallback routing because it exposes which sources need recovery rather than hiding them when they store no evidence.
- Run Scan also shows the same source-health summary immediately after a scan completes, so officers can see crawler quality before navigating to History.
- Batch evidence JSON exports include source-health rows and status counts, making shared scan-output files more useful for source tuning and fallback triage.
- Current and historical recommendation pack exports include source-health rows and status counts, so supervisor review packs can assess recommendation quality alongside crawler/source quality.
- Current Recommendations shows source-health metrics, filtering, table review, and CSV export for the latest linked scan batch, matching the Run Scan and History review experience.
- Source-health classification, action suggestions, status counts, and filters are centralised in `src/services/source_health_service.py`; dashboard pages only add display-specific badges.
- Ask AI receives source-health rows and status counts in the current-batch context. Follow-up answers can therefore consider scan reliability, weak/no-output sources, crawler quality, and whether LLM fallback may be appropriate.
- Home shows latest-scan source-health metrics and a compact "Sources needing attention" table so officers can see crawler/source issues before entering detailed review pages.
- The Home attention list can be exported as CSV for quick follow-up with source owners or IT support.
- README now explains the updated end-to-end pipeline in both officer-friendly and IT-friendly terms, including source-health statuses, source-health exports, organised scan context, Ask AI batch context, five-batch evidence retention, and the current boundary between deterministic crawling and future LLM-assisted fallback.
- Run Scan and History now show an LLM fallback candidate plan for sources with `Error` or `No evidence` status where fallback is allowed. The plan includes source URL, organisation, source family/type/role, country, evidence count, scan reason, and intended recovery focus. This is a no-cost planning/export layer only; it does not call the LLM yet.
- The fallback candidate panel now includes JSON request previews and Markdown prompt previews. These define the intended future recovery objective, constraints, and expected output shape before any paid LLM-assisted fallback call is implemented.
- Current Recommendations now includes fallback candidates and request previews in Ask AI context and recommendation packs, so officers can ask which sources may need recovery and supervisor exports preserve the planned fallback contract.
- Fallback candidate rows now include recovery-readiness labels such as `Ready for prompt review`, `Needs access review`, `Optional signal recovery`, and `Review manually first`, helping officers decide which failed/empty sources are worth future LLM recovery before spending tokens.
- Run Scan, Current Recommendations, and History now show compact fallback-readiness metrics. JSON exports, recommendation packs, and Ask AI context include `llm_fallback_readiness_counts` so officers and the model can distinguish strong future fallback candidates from access problems or optional signal recovery.
- LLM fallback candidate tables can now be filtered by readiness level across Run Scan, Current Recommendations, and History. Filtered CSV/JSON/Markdown downloads match the visible readiness selection, while full batch JSON/recommendation-pack exports still preserve the complete candidate set.
- Fallback candidate rows now include a `Recommended next step` field derived from recovery readiness, so officers can distinguish prompt-review candidates from access-review, optional-signal, source-URL, or manual-review cases without interpreting the labels themselves.
- Fallback-readiness filter labels and ordering are centralised in the shared source-health service to prevent dashboard pages from drifting apart.
- Organised scans now include a `quality_summary` with primary evidence count, signal evidence count, primary share, signal share, and a plain-language evidence-mix label. History displays these metrics, and the recommendation prompt tells the LLM to use them before relying heavily on trend/news evidence.
- Current recommendation packs and Ask AI context now include the compact `organised_scan_quality` summary, so officers and the model can discuss whether a batch is structured-heavy, mixed, or signal-heavy without loading the full organised scan JSON.
- Backend operational logging now writes structured JSONL events to `logs/operational_audit.jsonl`. The first implementation records app service initialisation, scan/source lifecycle events, crawler counts and skip reasons, scan completion and pruning, recommendation generation lifecycle, LLM prompts, raw LLM responses, parse errors, token usage when exposed by the SDK, and Ask AI question exchanges. The logger redacts likely API keys, tokens, credentials, and authorization values before writing. These files are excluded from source control and are intended for backend engineers, not normal officer UI.
- A governed backend LLM fallback recovery adapter exists for explicit fallback calls. It builds on the no-cost fallback preview payload, sends a strict schema request only when explicitly called by application code, validates recovered URLs and evidence classes, rejects invalid responses, logs prompts/raw responses/parse errors to the backend operational log, and returns structured recovered items.
- Run Scan includes an explicit fallback recovery control inside the LLM fallback candidate panel. Officers can filter candidates, select one source, review the generated prompt preview, and click a dedicated button to spend OpenAI tokens on that single selected fallback recovery. Results are displayed, downloadable as JSON, and saved as separate fallback recovery records. They are deliberately not merged into deterministic crawler evidence or automatically fed into recommendation generation.
- Fallback recovery persistence now uses a separate `fallback_recoveries` table. Successful officer-triggered fallback recovery outputs are saved with scan run ID, source name, organisation, source URL, recovery status, recovered item count, raw JSON result, and timestamp. These records deliberately remain separate from deterministic crawler evidence so future audit can distinguish crawler-extracted evidence from AI-recovered source interpretation.
- History now displays saved LLM fallback recovery records for the selected batch when they exist. Officers can see recovery status, source, organisation, recovered item count, recovered item summaries, confidence, explicit/inferred state, and source URLs. The saved fallback recoveries can also be downloaded as JSON for audit and IT review.
- README has been refreshed after the fallback recovery and operational logging work. It now explains explicit one-source-at-a-time fallback recovery, separate `fallback_recoveries` persistence, History fallback recovery display/export, backend `logs/operational_audit.jsonl`, and the key implementation files for IT handover.
- Saved fallback recovery records are now included in Current Recommendations Ask AI context, current/historical recommendation pack JSON, recommendation pack Markdown, and History batch evidence JSON exports. This lets officers and supervisors distinguish candidate sources that still need fallback from sources where explicit AI-assisted recovery has already been run.
- Current Recommendations now also displays saved LLM fallback recovery records for the latest batch when they exist, with a compact table and JSON download. This mirrors the History audit view while keeping Run Scan as the only page that can execute a paid fallback recovery call.
- Home now includes a suggested validation checkpoint. Depending on latest scan state, it tells officers whether the next useful check is basic Streamlit UIUX review, running a full source scan, reviewing source-health/fallback candidates, checking scan errors, or inspecting Recommendations/History for recommendation quality and responsiveness.
- Full Streamlit validation checkpoint passed: Home, Source Configuration, Current Framework, Run Scan, Recommendations, and History were reviewed in the app and the UI/UX was confirmed to look good. History is required to preserve and display the Ask AI chat history belonging to each recommendation batch so future officers can understand both the original recommendations and the follow-up reasoning/questions asked about that batch.
- Backend operational logging now has size-based rotation. The default active log is `logs/operational_audit.jsonl`, rotating at about 5 MB and keeping three backup files. Token usage metadata remains visible for IT/cost review, while API keys, access tokens, credentials, passwords, and authorisation values are redacted.
- A read-only IT handover diagnostic command is available at `python scripts\system_check.py`. It reports required Python import availability, source catalogue and framework-template presence, SQLite table/migration readiness, OpenAI API-key presence without exposing the key, and operational-log file status. It does not crawl websites or call OpenAI, making it safe for maintainers to run before troubleshooting.
- A backend operational-log summary command is available at `python scripts\log_summary.py`. It reads `logs/operational_audit.jsonl` and reports event counts, scan/source totals, recent failed/error/empty-response events, invalid JSONL line counts, and aggregate LLM token usage when available. This gives IT staff a first-pass troubleshooting view without manually reading the full audit log.
- A Markdown maintenance report command is available at `python scripts\maintenance_report.py`. It combines readiness diagnostics and operational-log summary into a pasteable handover report covering overall status, dependency availability, configuration/database readiness, recent scan activity, recent attention events, and LLM token usage. It does not print API keys, crawl websites, or call OpenAI.
- Source Configuration now includes three catalogue export controls: an officer-friendly enabled-source CSV, a full IT CSV with backend tuning fields such as article URL pattern, and a YAML backup matching the source configuration format. This supports source-tuning reviews and safer handover before officers or IT staff make catalogue changes.
- Source Configuration source removal now uses the selected URL as the durable catalogue key, not only the database ID. This matters because YAML-loaded source definitions do not carry SQLite IDs. The visible listing-page controls now allow up to 25 pages, matching backend validation and the crawler-tuning limit.
- Source Configuration now clears any validated-but-unapplied edit draft after a source is removed. Pending drafts are also checked against the live source URL list before rendering proposed changes. This prevents stale Streamlit session state from comparing an old draft against a shorter catalogue and crashing with a strict zip length error.
- Source Configuration now includes a YAML-backup preview panel. Officers or IT staff can upload a `sources_backup.yaml`, validate it using the same source safety rules as the real catalogue, see source counts and URL-level add/remove/update differences, and inspect preview rows. The preview deliberately does not apply or overwrite the active catalogue.
- Ask AI now behaves more clearly as a batch review assistant rather than a general chatbot. The UI tells officers that questions are scoped to the current recommendation batch, evidence previews, framework snapshot, source diagnostics, fallback records, and only the latest bounded same-batch Q&A turns. The question examples nudge users toward focused review questions, and the LLM context includes a `question_history_policy` plus up to five recent same-batch Q&A turns. Prior Q&A is conversation context only, not new evidence.
- README has been expanded for IT presentation use. It now explains deterministic crawler components, optional browser rendering, PDF extraction, proxy/Zscaler considerations, OpenAI Responses API usage, Ask AI stateless-request behaviour, application-managed memory, context-window controls, audit logging, source/provenance controls, and export/security considerations.
- Saved LLM fallback recovery records now carry explicit officer-facing provenance and verification labels in Current Recommendations, History, and JSON exports. Existing fallback outputs are labelled `🤖 LLM assisted` and `🟡 Needs verification`; low-confidence recovered items are labelled `🔴 Low confidence recovery`. This makes AI-assisted recovery visibly different from deterministic crawler-extracted evidence while leaving deterministic post-fallback URL verification as a future enhancement.
- A deterministic fallback URL verification service now exists in `src/services/fallback_verification.py`. It can attempt to fetch LLM-recovered URLs without making another LLM call, then label results as `✅ Verified by URL`, `🟠 Access blocked`, `🔴 Invalid URL`, or `🟡 Needs manual review` based on URL validity, fetch outcome, readable text length, and lightweight title/summary term matching. Current Recommendations and History expose explicit verify buttons, persist the results on the fallback record, and log the verification summary; ordinary page rendering never triggers network verification.

## Source-health remediation phase

- [x] Keep deterministic crawling as the normal evidence path. Do not automatically invoke LLM web search or automatically replace configured URLs.
- [x] Flag unhealthy, inaccessible, obsolete, empty, or low-quality configured sources and tell the officer to review and replace the source link through Source Configuration.
- [x] Keep any fallback recovery action explicit and officer-triggered; recovered evidence remains visibly labelled as LLM-assisted and separate from crawler evidence.
- [ ] Add a dedicated source-remediation section showing all unhealthy/unuseful sources with organisation, current URL, failure reason, evidence count, source family/type, and a plain-language instruction to replace or review the link.
- [x] Source-maintenance rows now carry explicit officer instructions, approval requirements, provenance, and an `AI URL recommendation` state so the future remediation section can distinguish deterministic warnings from LLM-assisted advice.
- [x] Run Scan, Recommendations, and History now present source-maintenance output as `Unhealthy or unuseful sources — review and replace`, with officer-facing guidance that configured URLs are never changed automatically.
- [x] Added a JSON-safe fixed prompt contract for future URL-recommendation calls. It locks the organisation, carries the current URL and crawler issue, restricts suggestions to official same-organisation STE pages, and forbids invented URLs or automatic catalogue updates.
- [x] Added strict parsing for future URL-recommendation responses. Responses must preserve the exact organisation and contain only valid HTTPS URL/reason pairs; malformed, cross-organisation, or non-HTTPS suggestions are rejected before officer display.
- [x] Added the governed OpenAI source-URL recommender request layer with one fixed batch prompt, strict JSON schema, operational request/response/error logging, and API-key/configuration guards. UI invocation and persisted result validation remain the next slice.
- [x] Application services now expose the governed source-URL recommender and its one-result-per-batch repository; no request is made until an officer presses the future remediation button.
- [x] Recommendations now provides one batch-level `Generate AI replacement URLs` action. It submits all flagged sources in one request, persists the result, displays it, and locks the action after completion; officers must apply accepted URLs manually.
- [x] History now displays saved batch URL-replacement recommendations with an explicit `AI suggested URL — human review required` label and no automatic catalogue update.
- [x] Recommendations and History flatten nested per-source URL suggestions into readable rows showing organisation, source name, current URL, recommended URL, reason, and human-review status.
- [x] The OpenAI URL-recommendation service now validates every returned source against the submitted organisation/source/current-URL snapshot and validates every proposed URL before persistence.
- [x] URL-recommendation response audit events now include SDK usage metadata when available, allowing IT staff to measure the cost of the single batch request without exposing secrets.
- [x] Updated the read-only IT system-check expected-table list to include `source_url_recommendations`, so maintenance reports explicitly verify the URL-remediation persistence table.
- [x] Officer-facing guidance now directs users to manual URL remediation rather than presenting LLM fallback crawling as an available workflow; legacy fallback records remain backend-compatible for historical audit only.
- [x] History no longer renders legacy fallback-recovery panels; user-facing review is consolidated around source health and AI-suggested URL replacement tables.
- [x] Recommendations no longer renders legacy fallback-recovery panels; the records remain available to backend exports and historical audit only.
- [x] Recommendations no longer presents an officer-facing `LLM fallback candidates` section; the active user workflow remains source-health review plus AI-suggested URL replacement.
- [x] Removed the per-source fixed URL-prompt preview selector from Recommendations; officers now use the single batch-level AI replacement action directly.
- [x] Ask AI starter questions now focus on source-family credibility, cautious signal interpretation, recommendation rationale, new STE sub-functional areas, and strongest outlier signals; the bounded same-batch Q&A context increased from 5 to 10 saved turns.
- [x] Updated Ask AI regression expectations to reflect the revised starter set and bounded semantics: the context holds up to 10 real saved turns and does not pad shorter histories with artificial entries.
- [x] Removed the obsolete regression expectation for an `evidence IDs` starter phrase after the officer-facing question was intentionally simplified.
- [x] Added a human-readable fixed-prompt preview so officers and IT staff can inspect the exact organisation-preserving URL-recommendation instructions before any future paid call.
- [x] Current Recommendations now lets officers select an unhealthy source and download its fixed URL-recommendation prompt preview; this remains review-only and does not call the LLM or change the catalogue.
- [x] Current Recommendations always shows the source-remediation section, including a clear healthy-batch message when no configured links are flagged.
- [x] Current Recommendations identifies the selected scan batch in the remediation caption and distinguishes a healthy batch from a missing scan-run link, preventing confusion with source-health results from another run.
- [x] Run Scan no longer exposes LLM fallback recovery controls. It only reports crawler/source-health outcomes and directs officers to manual URL remediation through Recommendations, History, and Source Configuration.
- [x] Recommendation generation now links an unqualified/current recommendation request to the latest scan run when one exists, ensuring Recommendations and source-health remediation inherit the same batch context instead of creating an unlinked recommendation batch.
- [x] Recommendations now recover source-health context for legacy batches with a null scan link by using the latest scan as an explicitly labelled fallback; truly unavailable links show the recommendation batch ID in the warning.
- [ ] Add a controlled `Generate recommended replacement URL` button for each flagged source. The button must use a fixed application-owned prompt (no free-form user prompt) asking only for relevant public URLs belonging to the same organisation and STE purpose. The organisation must never change; only the proposed URL may change.
- [ ] Replace the per-source preview action with one one-time-per-batch `Generate AI replacement URLs for all flagged sources` action. The request must contain all currently flagged sources in one fixed application-owned prompt and must not be callable a second or third time for the same recommendation/scan batch once a result is saved.
- [ ] Persist the batch URL-remediation request and response in a dedicated database record linked to the scan run and recommendation batch, including requested-at time, flagged-source snapshot, raw response, parsed suggestions, token usage, and completion/error status.
- [x] Added the dedicated `source_url_recommendations` persistence table/repository with a one-result-per-recommendation-batch guard. OpenAI response parsing and UI display remain the next slices.
- [ ] Display saved URL-remediation results in both Current Recommendations and History, with each result labelled `AI suggested URL — human review required`, original organisation/current URL, proposed same-organisation URL, reason, and validation outcome. Never apply a suggestion automatically.
- [ ] Validate the model response as exact HTTP(S) URLs, preserve the original source and organisation for comparison, label the result as `AI suggested URL — human review required`, and never write it directly to `config/sources.yaml`.
- [ ] Allow officers to review/download the recommendation and manually apply an accepted URL through Source Configuration. Log the request, original URL, proposed URL(s), validation outcome, and officer decision without storing secrets.
- [ ] Remove the automatic-fallback queue execution concept from the product roadmap. A bounded queue preview may remain as diagnostic information, but it must not trigger LLM retrieval automatically.
- [ ] Persist recovered items with unmistakable provenance such as `LLM_SEARCH_ASSISTED` / `🤖 LLM search assisted`, separate from deterministic crawler evidence. Every recovered item must retain the original failed source URL, the LLM-retrieved URL, recovery timestamp, confidence, recovery reason, and verification status.
- [ ] Feed verified/high-confidence recovered items into the organised-scan and recommendation pipeline only when the provenance is preserved and the recommendation context identifies them as LLM-assisted. Unverified or low-confidence items remain visible for review but must not silently become ordinary crawler evidence.
- [ ] Ask the fallback model to return source-maintenance advice when the configured URL is weak, blocked, obsolete, or nonsensical. Show officers that the configured link produced poor crawler evidence, explain the reason, and display any exact replacement URL recommendation as advisory only until a human accepts and updates the catalogue.
- [ ] Add operational-log events for automatic fallback queueing, recovery outcomes, replacement-link suggestions, and any human acceptance/rejection decision. Include counts and provenance, never secrets or unbounded page text.

Evidence retention policy update:

- Retain full evidence text for the latest 5 scan batches instead of only the latest batch.
- Prune evidence rows outside the latest 5 scan runs after a new scan completes.
- Keep scan-run records, source snapshots, framework snapshots, recommendation batches, recommendations, supporting evidence IDs, supporting URLs, and supporting organisations for audit continuity.
- History should clearly note when older batches may no longer contain full stored evidence text.

## Blueprint maintenance rule

- Operational-log summaries tolerate legacy field aliases (`source`, `evidence`, `urls_discovered`, and older token names) and malformed optional counts. This keeps IT diagnostics usable when reviewing logs written by an earlier application version or a partially completed scan.
- Fallback URL verification is now included in the operational audit trail. Each explicit officer-triggered verification records the recovery ID, scan/source provenance, number of recovered URLs checked, and the verified/blocked/manual-review counts without recording secrets. This closes the traceability gap between the saved fallback result and its deterministic verification action.
- History now passes the selected batch's saved fallback-recovery records into the scan-report maintenance view, preventing the LLM fallback section from raising an undefined-variable error when source-maintenance recommendations are rendered.

Update this blueprint whenever a major implementation phase is completed.

Keep the progress tracker current so the blueprint can be used as the authoritative memory of:

- what has been completed
- what is in progress
- what remains to be done

Current URL-remediation checkpoint:

- Completed: source-health flagging, fixed prompt contract, strict response validation, one-time batch persistence, Recommendations display, History display, audit logging, and IT schema diagnostics.
- Intentionally not supported: automatic fallback crawling, automatic URL replacement, repeated URL-recommendation requests for the same batch, or changing an organisation identity.
- Remaining polish: include saved URL-remediation results in every JSON/Markdown/CSV export and add a dedicated end-to-end UI smoke test for the one-time button lock.

## UI improvement backlog

UI improvements are intentionally managed separately from crawler, AI, and database changes. Before implementing each item, ask the officer to describe the desired layout, wording, interaction, colour, or visibility change; then implement and validate it in Streamlit.

- [ ] UI improvement 1 — officer to specify desired change.
- [ ] UI improvement 2 — officer to specify desired change.
- [ ] UI improvement 3 — officer to specify desired change.

Process for each UI item:

1. Confirm the intended page and desired user experience with the officer.
2. Implement the smallest isolated UI change without altering backend semantics.
3. Add or update UI/helper tests where practical.
4. Ask the officer to open Streamlit for a visual checkpoint.
5. Mark the item complete here after the officer confirms the result.

## New source catalogue refresh (planned)

### Internet replacement review following batch 41

- [x] 2026-09-15 follow-up: EMA roadmap official PDF works through configured discovery/extraction (one document, 2,153 words). Replaced HTML URL and re-enabled same source with official-guidance label. Storage handbook exceeds existing size cap; other three EMA overview roots remain disabled. This supersedes the four-source temporary exclusion below.
- [x] IET sustainability root and official survey alternatives checked: empty original, blocked survey HTML, non-PDF response at PDF URL. Disabled only this source, recorded URLs/reasons and retained history.
- [x] PDF reliability: stream-enforce existing byte limit, close response, reject HTML masquerading as PDF and convert parser failures into per-source ScanError; regression tests cover these cases.
- [x] Verification after EMA/IET changes: full pytest suite 182 passed. Existing PDF extraction test double updated to model streamed responses; configured EMA PDF probe succeeded. No paid AI calls or historical evidence rewrites.
- [ ] Next checkpoint: run a consolidated evidence-only scan of the currently enabled catalogue and inspect source-health plus evidence/organised-scan exports. This validates accumulated changes; it does not certify every enabled source as healthy. Keep documented exclusions disabled during this scan.

- [x] 2026-09-15: Reviewed four failed EMA energy-grid/roadmap/storage/solar HTML roots and two official HTML alternatives; all yielded zero readable words locally. Temporarily disable the four roots in YAML and SQLite, preserving identity/history, and correct country to Singapore. Separate EMA media index unchanged. See source replacement register for exact URLs and evidence.
- [ ] EMA follow-up: locally validate official roadmap PDF/storage handbook candidates before considering reinstatement; empty HTML does not establish that PDF/browser retrieval also fails.
- [ ] Consolidated scan checkpoint: reconcile remaining batch-42 failures (including IET sustainability) and report any outstanding limitations; accumulated replacements require end-to-end validation, not just sample probes.

- [x] 2026-09-15 HDB career/tech-career sources reviewed: 8/34 words of headings/navigation, linked internship/scholarship alternatives 1/3 words. Both disabled reversibly with exact findings documented, IDs/history preserved and country Singapore. HDB root unchanged.
- [ ] EMA failures remain under review before consolidated scan checkpoint; HDB career exclusions can be revisited if usable official retrieval becomes available.

- [x] 2026-09-15: SERIS original and flagship page empty; two official research alternatives return Incapsula block text. Recorded exact URLs and reversibly disabled the source in YAML/SQLite, preserving history and correcting Singapore/research classification. Search indexing is not proof of crawler access.
- [ ] EMA and HDB failures remain under review; consolidated scan checkpoint follows remaining access decisions. SERIS can be reconsidered if an accessible equivalent is verified.

- [x] 2026-09-15 IFMA empty credential overview replaced with official CFM pathway. Actual extraction 615 words, one substantive candidate. Explicitly renamed to reflect narrower CFM scope; country USA; YAML/SQLite updated, individual-courses source untouched. Configuration/routing tests: 17 passed.
- [ ] Validate IFMA alongside accumulated replacements in consolidated scan; remaining sources (including EMA, HDB and NUS SERIS) still require review. Do not equate readable landing page with complete credential coverage.

- [x] 2026-09-15 OCW extraction cleanup: HTML decoding now honours declared charset/meta rather than Requests' implicit Latin-1 default. Catalogue extraction preserves course-info values (including teaching term) and keeps expanded descriptions instead of duplicate collapsed teasers. Regression coverage added for UTF-8, explicitly declared legacy charset and course metadata. Applies to future retrieval, not stored evidence rewrites.
- [ ] Consolidated source scan and broader OCW sample validation remain pending; historical teaching dates must not be represented as current course availability.

- [x] 2026-09-15 OCW empty search replaced by explicitly named Featured STE Courses source. Narrow course-card discovery, 15 live candidates, two substantive extraction samples. No homepage evidence stored; YAML/SQLite updated.
- [ ] OCW full-catalogue coverage and extraction polishing (historical dates, encoding/teaser noise) remain pending. Featured coverage is not full coverage. Remaining failed-source review continues before consolidated scan.

- [x] 2026-09-15: KAIST companion curriculum table discovery completed through a narrow observed-link rule. Both live extraction samples succeed (526 / 1,241 words); robots, cap and deduplication regression added. No additional configured source or history mutation.
- [ ] Validate KAIST in consolidated scan alongside other replacements; remaining source review continues.

- [x] 2026-09-15 resumed source tuning after Ask AI user verification: KAIST robotics requirements retained, corrected ARTICLE to CATALOGUE, renamed and labelled South Korea in YAML/SQLite. Actual landing-page extraction 526 words, one useful evidence candidate. Count alone is not the quality criterion.
- [ ] KAIST separate Fall 2026 curriculum table is not yet covered by this discovery result; remaining failures and consolidated full-scan validation are pending.

- [x] 2026-09-15 Ask AI follow-up: measured actual existing batch fields; source-health/maintenance tables added approximately 259 KB. Remove their detailed rows from live Q&A only, retaining summary counts and unchanged UI/export diagnostics. Existing batch context now 188,163 UTF-8 bytes before question/instructions, below 300,000-byte guard. No new scan required. Added read-only field-size diagnostic and regression test.

- [x] 2026-09-15 urgent Ask AI size fix: recommendation-cited evidence only by ID/exact URL, compact batch metadata, source lookup limited to cited evidence, no live legacy fallback payload. Preserve framework and ten recent Q&A. Explicit missing-evidence/scope metadata; 300,000-byte preflight guard and 4,096 output-token cap. No scan/history deletion. Resume failed-source tuning after user verifies Ask AI on existing batch.

- [x] 2026-09-15: fixed catalogue omission of definition-list syllabus details (dt/dd) and legacy centered availability notices. Oxford live root extraction increased from 207 to 402 words. Regression test covers ordering, nested-content deduplication and navigation exclusion. Full suite: 171 passed.
- [ ] Oxford child-candidate relevance and remaining failed sources still need review; root extraction fix does not certify all 16 candidates or complete source coverage.

- [x] 2026-09-15: Oxford failed systems-engineering source replaced with accessible Secure Systems Engineering module and explicitly renamed. Applied YAML/SQLite, CATALOGUE, UK. Actual root extraction 207 words; 16 discovery candidates. Configuration tests: 10 passed.
- [ ] Oxford syllabus preservation (404 readable versus 207 extracted words) and child relevance need follow-up. Security course is narrower than original scope and has unscheduled future dates. KAIST and other remaining failures still pending; full-scan checkpoint not yet reached.

- [x] 2026-09-15: Melbourne Civil Engineering Systems replaced with its accessible official BDes handbook entry; actual extraction yields 394 words of skills/learning outcomes, two discovery candidates. YAML/SQLite updated, country Australia. Narrower pathway and academic-year caveats recorded in replacement register.
- [ ] Validate Melbourne replacement in the next consolidated scan; remaining failed-source review continues.

- [x] 2026-09-15: RTPI and INCOSE framework sources excluded reversibly after documented original/official alternative access failures. Apply to YAML and SQLite, preserving source records and historical citations. Accessible INCOSE vision content is not an equivalent framework replacement.
- [ ] Melbourne handbook alternative and other remaining failures still require review. Full-scan validation remains pending; do not infer healthy status from search indexing.

- [x] 2026-09-15: Michigan BME original plus official bulletin programme/course alternatives return 403; documented and disabled the source. Both configured UCL sources disabled because robots retrieval returns 403 (permissions unavailable, not confirmed disallow). Official environmental-design alternatives checked for eligibility; no bypass. Preserve records/history. See replacement register for exact URLs and scope limitations.
- [ ] Remaining sources are still under review; next full-scan checkpoint will follow further tuning, not each exclusion.

- [x] 2026-09-15: Princeton replacement applied to YAML/SQLite after original and undergraduate-announcement alternatives returned 403. Engineering majors/minors page discovers four candidates and yields 159 words of actual programme overview. Undergraduate-only coverage caveat recorded.
- [x] Michigan Sustainable Systems disabled after original requirements page and same-programme overview both returned 403. Recorded reversible access exclusion; no changes to other Michigan sources or history. Configuration/routing tests: 11 passed.
- [ ] Continue remaining university and professional-body failures before next full-scan checkpoint; current review is not complete.

- [x] 2026-09-15: retain ETH EPSE research overview with research/resource-first routing; live discovery returns seven candidates and the sampled landing page extracts 112 words. Some navigation labels remain; complete child-page quality not certified.
- [x] Replace empty Georgia Tech EnergyWatch with official Strategic Energy Institute energy-research overview; applied to YAML and SQLite preserving identity. Live extraction returns 1,167 words. Document broader research coverage versus original monitoring portal in the replacement register.
- [ ] Validate these changes together in a future full scan; remaining failed-source reviews continue. No full scan needed for this two-source pass alone.

- [x] 2026-09-15: reject short student-chat pages and the confirmed SUTD navigation-only catalogue shape. Do not impose a blanket 100-word minimum on structured course/competency lists. Regression coverage preserves actual short course lists and mixed navigation/course content. Full suite: 170 passed.
- [ ] Other short items (including recruitment placeholders) remain to review; this targeted filter is not a general semantic quality classifier. Remaining failed-source URL research is still outstanding. Hold the next full scan until further source changes are ready.

- [x] 2026-09-15: retain IStructE `div.card__body` course descriptions in document order, without duplicating nested paragraphs or including navigation cards. Actual probe increased from 147 to 399 words. This is listing-level extraction, not all individual course pages.
- [ ] Next source-quality pass: short navigation-only catalogue entries and remaining genuine failures. No new full scan requested for the course-description change alone.

- [x] Batch-42 follow-up: IStructE extraction lost its main content inside an ASP.NET form; preserve main-containing form wrappers and remove controls. Allow only the reviewed IStructE training landing path through the utility guard, not other About pages.
- [x] SUSS curriculum PDF text now becomes escaped paragraph blocks readable by structured catalogue extraction. Local probe recovered 1,992 words of curriculum; IStructE recovered 147 words including course titles. Full next-scan validation remains pending; IStructE card descriptions still need improvement.
- [ ] Continue short navigation-only catalogue cleanup without deleting legitimate concise competency/course lists. No need for another full scan yet.

- [x] Batch 42 interim scan received and reconciled: 249 sources, 1,547 evidence records. Content sample and limitations recorded in `docs/batch_42_review.md`.
- [x] Fix false source-health errors caused by organisation substrings in unrelated URLs (PUB versus publish-with-incose). Recomputed actual error sources: 22, versus 36 exported flags. Reporting correction only.
- [x] Fix redirect duplicates within each scan; retain cross-scan repeats. Batch 42 had 1,505 distinct final URLs among 1,547 records. Do not rewrite historical evidence.
- [x] Full regression suite after these fixes: 163 passed.
- [ ] NEXT: diagnose IStructE/SUSS workflow zero-output results and short catalogue/navigation evidence, then continue official alternatives for remaining failures. Hold next full scan until this additional tuning pass is ready.

- [x] 2026-09-14: verified PUB (four pages), MPA (two sources plus alternative), and NIST using actual discovery/extraction. Correct research-page routing and labels; preserve working URLs. Disable only the low-content MPA general hub after comparing the official alternative; retain MPA research centres.
- [x] Add a bounded read-only configured-source probe and research-routing regression tests. No paid AI requests during tuning.
- [x] Regression checkpoint: full local suite passed, 156 tests (2026-09-14). Ready for interim full evidence-only scan; no full scan has been run by the agent.
- [x] Interim full evidence-only scan completed as batch 42; exports reviewed. This does not complete all batch-41 failed-source reviews.

- [x] 2026-09-14: content-check five BCA pages; retain official URLs, correct resource-first routing for three article-classified guidance hubs, and set Singapore/official-guidance metadata. Details in `docs/source_replacement_review.md`.
- [ ] Validate BCA changes in the next full scan, including child-document failures and incomplete oversized-PDF coverage; successful landing-page probes are not full-scan certification.
- [x] Reject EMA educational-materials candidate after actual Incapsula block text; record failure without substituting irrelevant or blocked content. Remaining failed-source reviews are still pending.

- [x] IStructE official events/training alternative retrieved relevant engineering course descriptions and replaced the unproductive training URL; CATALOGUE retained. Full scan validation pending.
- [ ] IFMA credential alternative returned title only; member resource hub is readable but not equivalent. Continue investigating before replacement/exclusion.

- [x] PMI thought-leadership original and two official alternatives returned 403; recorded and disabled. Three configured PMI source entries now have documented access exclusions.
- [ ] EMA solar statistics alternative also returns empty readable content; no equivalent working replacement confirmed. MIT OCW catalogue discovery remains pending; archived single courses are not equivalent to its broad search index.

- [x] Applied Cornell certificate redirect to Duffield domain and CATALOGUE classification after inspecting curriculum text. Applied Cambridge Energy Technologies postgraduate directory as a focused replacement for energy hub (nuclear coverage still pending).
- [x] Disabled PMI programme-standard source after original and standards index repeatedly returned 403; documented before applying. MIT OCW and PMI thought-leadership review still pending.

- [x] Replaced SUSS BSc Facilities Management marketing page with official public curriculum service (sims1.suss.edu.sg, progcd=fmt-maj1). Local scanner retrieved course names/codes and credit units; full scan validation pending.
- [x] Disabled PMI PgMP certification source after original plus two official alternatives returned 403. Original/replacement attempts and reversible access-exclusion reason recorded in `docs/source_replacement_review.md` before applying to YAML/SQLite. Other PMI functions remain under review.

- [x] NUS brochure preference recorded: use the official HTML MSc Project Management page already in the catalogue; the PDF was never configured. HTTP probe returned no readable text, so HTML retrieval remains unresolved.
- [x] Probed INCOSE Vision 2035 (readable but not equivalent to full framework), SUSS alternative module (robots retrieval 403), and EMA roadmap (no readable HTTP text). Decisions and URLs recorded in the replacement register; no unsupported swaps or exclusions.

- [x] Started `docs/source_replacement_review.md`, recording official alternatives, crawler probe results and exclusion reasons before any disabling.
- [x] Applied two locally retrievable official training alternatives for AEE CEM and Energy Institute Academy in YAML/SQLite, preserving database identities.
- [ ] Complete research for the remaining error/zero-output sources (96 rows initially). First four candidate probes are not completion of this task.
- [ ] Validate replacement extraction in a scan. INCOSE PDF is 403; its Vision site remains to test. NUS brochure exceeds the current 2 MB limit and requires a crawler-capacity decision, not automatic exclusion.
- Exclude only after documenting attempts and the specific reason; preserve past evidence citations. No exclusions in the first internet-review pass.

### Internal content review requirement — batch 40 onward

#### Shared crawler fixes after batch 40

- Batch 41: 253 source rows; 93 count-healthy, 64 low-output, 42 zero-output, 54 errors; 1,506 retained records. Counts do not establish quality. NParks source 151 still produced 13 visitor-activity records and source 95 still produced 21 largely visitor/navigation records.
- [x] Fixed NIST feedback-form misclassification as pagination: `page=https://...` is not a numeric page selector. Discovery now requires numeric pagination or explicit next-page controls and excludes form endpoints. Seven targeted tests passed.
- [ ] Verify NIST next run; continue NParks scope tuning. All 253 remain enabled. This is an initial batch-41 inspection, not a completed content audit.

- [x] Following officer request, re-enabled all 253 configured sources in YAML and SQLite for the next full evidence-only scan; zero sources disabled. Review the resulting exports together for actual content quality before further catalogue tuning. Full scan and post-scan validation remain pending.

- [x] Catalogue extraction reads headings, paragraphs, learning-outcome lists and course-table rows in document order, retaining linked course names rather than substituting raw href values. Removes navigation/print controls in the selected content region.
- [x] Link discovery excludes semantic navigation/header/footer menus before selecting article links, preventing these menus from consuming the source quota.
- [x] Fourteen targeted extraction/discovery tests passed, including curriculum-table and learning-outcome preservation and menu exclusion.
- [ ] Live output validation remains required: these fixes do not establish health for all 253 sources. Enabled/disabled choices remain as before while shared extraction changes are tested.
- [ ] Revisit the disabled sources using access diagnostics and content-level inspection; distinguish blocked access from broken discovery and incomplete extraction. Do not repeatedly request unchanged scans as a substitute for diagnosis.

- [x] Officer requirement recorded: source tuning must assess extracted content, not simply record count. This is an internal development review and does not require a new officer-facing UI or an automatic change to the visible health score.
- A count-based Healthy result only confirms volume. Review actual text and organisation/source provenance for STE relevance, explicit competencies, courses, learning outcomes, standards, and useful supporting signals.
- Check for access challenges, cookie-only pages, advertising, navigation/footer clutter, off-topic visitor pages, repeated boilerplate, encoding damage, and missing table/list content. Search markers are triage aids, not sufficient grounds to reject a source (e.g. legitimate documents may discuss advertising or CAPTCHA).
- Record inspected evidence IDs and limitations. A useful single framework may outweigh 25 irrelevant pages. Do not mark a whole source content-validated from a small sample or infer absence of content from cross-source deduplication alone.
- Batch 40 baseline: 1,857 evidence records; 108 count-healthy, 28 low-output, six zero-output sources. Organised classification reports 873 primary and 984 signal records; these classifications do not establish content quality.
- [x] Initial content inspection documented in `docs/batch_40_content_review.md`.
- [ ] Tighten NParks resource discovery to prevent visitor activity/navigation links filling the article quota; preserve the separate research-programmes source.
- [ ] Repair UIUC extraction of course tables and learning-outcome lists and exclude print controls from extracted text.
- [ ] Verify HSA PDF discovery/extraction beyond its useful guidance-title index.
- [ ] Continue source-by-source text sampling across all enabled sources; this first inspection is not a full content audit.

### 2026-09-14 corrective tuning checkpoint

- Batch 39: 107 healthy, 28 low-output, six no-evidence and one UIUC connection error. All six metadata retests still produced zero records.
- [x] Resource discovery now includes the configured page itself as an extraction candidate, checks robots permission, and respects the listing-page limit. Previously a standalone course/framework page with no matching child links was omitted. Twelve targeted crawler tests passed.
- [ ] Confirm extracted content from the six retest sources after this discovery fix. This is a diagnosed candidate-discovery defect, not proof that it explains every failed source. Keep UIUC enabled for retry after its single disconnection.

- [x] Fixed health-stage URL matching to preserve case-sensitive paths. Previous full-URL case folding could overwrite A*STAR `/Research/` and `/research/` outcomes, so previous staged counts were not identical to health-report counts.
- [x] Corrected five NUS programme/specialisation pages from ARTICLE to CATALOGUE and HSA medical-device guidance from ARTICLE to FRAMEWORK; assigned Singapore and enabled these six existing URLs for retesting. Applied to YAML and SQLite: 253 total, 142 enabled.
- [ ] Verify these six destinations in the next scan. Metadata corrections route them through resource discovery; successful extraction is not yet established.
- Remaining disabled sources still require content/access investigation. Earlier removal of them from scans was staging, not completed crawler tuning.

- [x] Receive the officer’s newly compiled source list covering STE government agencies, institutes of higher learning, and professional bodies across systems engineering, sustainability, infrastructure, energy, biomedical science, geospatial, project management, and related domains.
- [ ] Validate each URL, organisation, country, source family, source type, source role, evidence label, and STE relevance.
- [ ] Detect duplicate URLs, overlapping sources, obsolete entries, and sources that conflict with the current catalogue.
- [ ] Stage additions and updates as a reviewable diff; do not overwrite the approved catalogue automatically.
- [ ] Preserve existing configured sources unless the officer explicitly requests removal or replacement.
- [ ] Add accepted sources through the existing Source Configuration workflow and update crawler limits/strategies only where justified.
- [ ] Run a controlled scan and review source-health outcomes before marking the refreshed catalogue stable.

Source-list follow-up priority:

- [ ] Stage the supplied list as a reviewable import rather than overwriting the active catalogue.
- [ ] Infer source type from the destination path (framework/standards, catalogue/course, official guidance, research/resource, or news/commentary) and preserve the supplied source family and role.
- [x] Added deterministic URL-path source-type inference for staged imports, covering framework/standards, catalogue/course, research/resource, trend/news, and generic article paths.
- [x] Added staged-import URL normalization and duplicate filtering for escaped spreadsheet URLs, host casing, and trailing slashes while preserving distinct URLs from the same organisation.
- [x] Added a review-only staging transform that preserves supplied source family/role, infers backend source type, and marks rows as `Staged for review` without changing the active catalogue.
- [ ] Add Source Configuration staging-import preview: show staged row count, duplicate removals, inferred source types, and URL-level add/update/remove differences before an officer explicitly applies the catalogue changes.
- [x] Added deterministic URL-level staging diff logic for additions, removals, and changed metadata; the Source Configuration preview can now build on this without mutating active sources.
- [x] Added CSV/TSV text parsing for staged source lists, allowing government-laptop users to provide an export or pasted table even when Excel automation is unavailable.
- [x] The officer does not need a new source-list upload function. The supplied source list will be integrated directly into the existing catalogue through a controlled configuration update, preserving the current Source Configuration editing workflow.
- [ ] Direct integration is now the active next phase. Add the supplied sources in domain groups (for example systems engineering, sustainability/infrastructure, project management, energy, biomedical, geospatial, and automation), deduplicate against the current catalogue, and run a source-health checkpoint after each group.
- [x] Source-health review established the staged testing policy: newly added groups are disabled by default after import, only the current tuning group is enabled for a scan, and previously tuned groups remain disabled or enabled according to the active test plan.
- [ ] Before each tuning scan, explicitly record which source group is enabled and disable all other newly added/unready sources; enable the full refreshed catalogue only after group-level health checks are complete.
- [x] Added controlled test-set staging: `SourceConfigurationWorkflow.stage_test_set()` and `scripts/stage_source_test.py` enable only explicitly named, organisation-matched, or distinctive partial-name/URL sources, disable the rest without deleting them, and fail fast on unknown identifiers. This removes the need for the officer to toggle sources one by one during tuning.
- [x] Added broad baseline mode: `python scripts/stage_source_test.py --all` enables every active configured source for a full health scan. This is reversible through the same staging command and supports the officer's initial whole-catalogue quality review.
- [x] Added `scripts/integrate_source_list.py` to merge the latest pasted TSV source list into the existing catalogue, normalise escaped URLs, deduplicate against current entries, infer source metadata, preserve existing entries, and optionally enable the complete merged catalogue with `--enable-all`.
- [x] Integrated the latest supplied source list: 48 existing entries preserved, 205 new URLs added, 253 total configured sources, and all 253 enabled for the requested baseline scan. Health results will determine the next tuning groups.
- [x] Applied batch-37 health staging: 138 healthy/low-output sources remain enabled; 115 error/no-evidence sources are disabled for the next scan but retained in the catalogue for URL remediation or an explicit removal decision. No catalogue rows were deleted from a single health batch.
- [x] Batch 38 improved the staged set: 108 healthy, 28 low-output, 1 no-evidence, and 1 timeout/error result. The next stage keeps the productive set enabled and disables the newly confirmed no-evidence/timeout entry; the remaining 115 disabled catalogue rows stay unchanged for later remediation.
- [x] Batch-37 remediation priority established from disabled high-value STE pages: NIST CPS/IoT, ISA standards/training, Georgia Tech ISTD, PUB research/code-of-practice, Cornell Systems Engineering, MIT professional learning, BCA built-environment competency, INCOSE competency framework, Engineers Canada guidance, and CAAS aviation systems. These should be reviewed before lower-value home pages, news-only pages, or duplicate course listings.
- [x] Next isolated tuning target selected from batch 33 health results: CAAS Air Traffic Management Systems and Technology is enabled alone from the new group; NASA, NASA APPEL, Carnegie Mellon, Cornell, and Georgia Tech remain disabled.
- [x] Batch 35 confirmed CAAS still produces no retained evidence. CAAS is disabled for the next test, and NASA Systems Engineering Handbook is now the next isolated tuning target.
- [x] First systems-engineering group integrated: CAAS, NASA Systems Engineering, NASA APPEL, Carnegie Mellon Engineering, Cornell Systems Engineering, and Georgia Tech ISTD. Existing catalogue entries were preserved.
- [ ] Normalise escaped URLs such as `https\://`, deduplicate repeated organisation/URL pairs, and retain distinct URLs from the same organisation when they serve different STE purposes.
- [ ] Tune and validate sources one organisation/domain at a time. A source is not considered complete merely because its URL is reachable; it must produce useful STE evidence and have a healthy source-health status.
- [ ] After each tuning group, record evidence count, errors, low-value output, blocked access, and recommended URL changes before enabling the next group.

### Source catalogue completion register

The latest pasted source list is the authoritative intake list for this refresh. Each organisation/URL pair must be tracked through these states:

`Not staged` → `Staged` → `Enabled for test` → `Healthy`  
or `Needs tuning` / `Blocked` / `Remove from candidate list`.

The register must preserve distinct URLs from the same organisation and record the final health state, evidence count, source family, inferred source type, and last test batch. A source is counted as completed only when it has been added to the configured catalogue and has a healthy or explicitly accepted low-output status after review.

Current tracking checkpoint:

- Completed and healthy existing catalogue: continue to preserve and monitor.
- New systems-engineering group: NASA Systems Engineering is currently enabled for isolated testing; CAAS produced no evidence and is disabled; NASA APPEL, Carnegie Mellon, Cornell, and Georgia Tech remain staged/disabled.
- Remaining supplied list: not yet staged or health-tested.
- [ ] Maintain this register after every source-health batch until the full supplied list is either healthy, explicitly accepted, or removed from the candidate list.
# Current checkpoint — card provenance and excerpt repair

- [x] Verified the user's latest three TXT attachments: 206 cards, 75 represented organisations, 106 status rows; status and URL-log totals both equal 206. The quoted 24-card pilot diagnosis does not describe these attachments.
- [x] Native Cloud exports carry a shared unique scan identifier in filenames, cards and CSV logs. Export rejects inconsistent organisation/log card counts.
- [x] New Cloud scans allow 3,000 serialized characters/card and 15,000/organisation. Whole blocks or sentences are selected, rather than cutting arbitrary prefixes.
- [x] Cards include explicit schema, original text size, source family, evidence type and priority. Unknown dates/countries remain unknown, never guessed. Priority is resource-type ordering, not credibility.
- [x] Reject narrow product-certification-only cases; suppress identical excerpts within an organisation.
- [ ] Review a fresh Cloud scan for semantic usefulness, PDF boilerplate and partial duplicates. Exact duplicate suppression is not a complete document-family independence check.
- [ ] Government assistant review of matching newly named files. Previously shortened cards cannot be expanded without a new scan.

# Current checkpoint — ranked discovery

- [x] Bounded sitemap discovery for native Cloud rows, once per origin/run; ranked frontier capped at 100 candidates with explicit pruning logs.
- [x] Search/faceted URL exclusion; body-level learning-outcome signals and definition-list extraction.
- [x] Optional browser escalation restricted to sparse JS shells. Explicit Required remains supported; images/fonts/media blocked, scripts and styles preserved for functionality.
- [x] Up to 200 characters of extracted public text logged for qualification rejection diagnostics.
- Redirects already follow up to six attempts. Browser assets never consumed the content-candidate budget. Robots policies remain cached per origin, not merged across hosts with potentially different rules.
- [ ] Validate yield on next Cloud export. Scoring is a hypothesis, not proof of representative coverage.
- [ ] Consider larger framework excerpts/PDF limits and authorised manual-file ingestion separately; existing bounds remain to protect Cloud resources.
- [ ] Further canonical redirect deduplication, boilerplate and document-family review remain pending. Do not bypass robots or WAF restrictions.

# Current checkpoint — redirect export repair

- [x] Preserve requested and resolved URLs in scan logs; compare card provenance with resolved URL when present.
- [x] Keep strict organisation, source ID and count checks. No guessed URL reconciliation for earlier in-memory results.
- [ ] Verify fresh Cloud scan/export on build `redirect-provenance-1`. Old browser-redirect scans without recorded final URLs may still require rescanning.

