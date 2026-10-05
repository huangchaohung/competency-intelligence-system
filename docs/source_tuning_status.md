# Source tuning checkpoint — 2026-09-24

## SJTU summer research internship — 2026-10-05

- Reviewed /en/summer-program/: preserve the About Summer Program and participant-benefit text blocks, excluding menu, eligibility and timeline. Label as research-training overview, not a complete project list or syllabus. Exact URL profile; missing or duplicate academic sections fail closed.
- Live permitted extraction: 232 words including scope note; research-skills text retained, GPA instructions absent. 327 tests passed; build sjtu-internship-1. Catalogue unchanged, Cloud acceptance pending.
- Research institutions directory inspected: predominantly policy/social-science think-tank descriptions with some interdisciplinary content. Left unchanged pending closer STE scope review rather than blanket exclusion.

## SJTU exchange and visiting pages — 2026-10-05

- /281 has a reviewed accordion block headed 3. PROGRAMS & COURSES. Keep that block, including access restrictions and school descriptions; omit nomination, visa, accommodation, transcript and scholarship blocks. Mixed disciplines and unvisited linked-document scope are explicit. Live permitted extraction: 1,542 words including note; mechanical engineering and restrictions retained, visa section absent.
- /282 reviewed introduction and registration content offer visiting-student application procedures, not named subject programmes or competencies. Exclude only that exact destination from storage; exchange and summer-school pages remain eligible. No catalogue removal.
- 326 tests passed; sjtu-exchange-1. Cloud acceptance pending; existing exports unchanged. Next: review remaining research institute and summer internship records; SJTU-only Cloud check is still suitable.

## SJTU summer-school overview — 2026-10-05

- Reviewed non-degree /522: export had 424 words including extensive global navigation. Exact-page extraction retains the single unheaded overview and named course examples, with mixed-discipline/partial-catalogue scope explicit. No claim of full syllabi. Other non-degree pages remain unchanged.
- Permitted live result: 196 words including scope note, surgical robotics retained, Work@SJTU absent. Missing/ambiguous body fails closed. 324 tests passed; sjtu-summer-1. Catalogue unchanged; Cloud acceptance pending.
- /281 exchange fact sheet and /282 visiting-student page inspected: useful fragments are intermixed with substantial administrative material. Leave unchanged until section-level review; do not blanket-exclude non-degree programmes.

## SJTU admissions wrapper cleanup — 2026-10-05

- Completed the /387 follow-up: exclude its exact HTML destination from stored evidence. Prior permitted content review found a programme-list link followed by application eligibility, deadlines, scholarships, fees and contacts; the actual PDF now has its own enabled source. Other programme pages and the PDF remain eligible.
- Added ArticleExtractor integration checks for PDF organisation/source/scan provenance, mixed-scope disclaimer, page markers, and empty/redirected responses. 323 tests passed; build sjtu-admissions-2. No further catalogue changes or retrospective edits. Cloud acceptance pending.
- Suitable next checkpoint: a fresh-session SJTU-only scan covering the GIFT source and new Chinese-taught PDF source; inspect programme text and PDF output before the next broad scan. Existing session source copies are not overwritten.

## SJTU linked programme PDF — 2026-10-05

- /387 links directly to the official isc.sjtu.edu.cn 2026 Chinese-taught undergraduate programme PDF. Added that reviewed document as a separate enabled catalogue source; original GIFT source unchanged. Direct robots-checked PDF routing avoids treating admissions HTML as the programme list.
- Production text extraction returns 721 words with five PDF page markers. Mixed STE/non-STE scope is explicit; no table-row relationship or complete-syllabus claim. No visual table fidelity certification. URL/type/content guards reject redirected or invalid responses. 321 tests passed; build sjtu-catalogue-1. Cloud acceptance pending.
- New sessions receive the new default source. Existing session source copies are intentionally preserved: restore defaults only if temporary edits may be discarded, or add the PDF URL manually. /387 admissions HTML cleanup remains pending; no historical exports modified.

## SJTU engineering cluster programmes — 2026-10-05

- Reviewed /278 English and /279 French pages using permitted live retrieval. Their substantive introductions are unheaded .page-item blocks; named sections contain admissions, fees and application paperwork. Exact-page profiles retain the introductions with distinct language-specific titles and a selected-overview disclaimer. Planned-offering qualifiers are preserved verbatim.
- Live extraction: English 313 words, French 217 words; navigation and application-material sections absent. Missing or ambiguous introduction fails closed. 319 tests passed; build sjtu-cluster-1. Catalogue unchanged; Cloud acceptance pending.
- /387 Chinese-taught page remains unchanged pending linked programme-list review: its visible Program List section is a link and administrative note, not the actual programme list. Do not claim that linked content was extracted.

## SJTU civil engineering programme — 2026-10-05

- Reviewed official degree-programs/778 HTML. Exact-page extraction retains Programme Introduction, What You’ll Study, career prospects, facilities and global mobilities, excluding navigation, fees and application paperwork. Programme-specific title prevents confusion with the configured GIFT discovery source.
- Permitted live extraction: 509 words including selected-overview disclaimer; Digital Twin Technology retained, Work@SJTU and application-material instructions absent. Missing study section fails closed rather than falling back to navigation. Other programme pages unchanged.
- 317 tests passed. Build sjtu-civil-1; catalogue unchanged. Cloud acceptance pending; changes apply to subsequent scans. Continue reviewing remaining programme pages; IMDA error details still outstanding.

## SJTU index and placeholder review — 2026-10-05

- Export (3) stored degree-programs/825 as 257 words of navigation plus a link-out instruction, and /en/news-events/meet-sjtu/research as 249 words of navigation. Official-page review confirms the first is a School of Medicine link placeholder and the second a research-news index, not an article body.
- Exclude these two exact destinations from evidence storage. Research article child URLs and programme pages remain eligible; no catalogue deletion or broad research exclusion. The index may still serve discovery, but its menu must not count as substantive evidence.
- Build sjtu-index-1. Applies on a new scan; existing downloads unchanged. Cloud verification pending. Remaining programme-body cleanup and IMDA raw-error diagnosis remain open.

## SJTU GIFT section extraction — 2026-10-05

- The configured /794 programme page mixed global navigation and lengthy admission paperwork into evidence. Exact-page extraction now retains reviewed programme-introduction, Sustainable Energy/Health Science, international opportunities and industrial experience sections, including nested headings. Other SJTU pages are unchanged.
- Live permitted extraction yields 859 words including scope disclaimer; both programmes remain and Work@SJTU menu text is absent. Admission, scholarship, fee and contact sections are omitted. Missing reviewed content fails closed. This is a selected programme overview, not a complete syllabus.
- Build sjtu-programme-1; no catalogue edits. Cloud acceptance pending. IMDA recorded errors remain outstanding independently.

## SJTU duplicate admissions review — 2026-10-05

- Export (3) records 1301/1302 have identical 1,976-word text at degree-programs/267 and /270. Permitted local retrieval confirms shared graduate-admission content: general introduction, eligibility, deadlines, documents, fees, scholarships, contacts and appendix links; not actual curriculum or competency descriptions.
- Exclude these two exact host/path destinations from stored evidence instead of treating them as two programmes or retaining one as primary evidence. Other SJTU pages (including configured /794 with substantive Sustainable Energy/Health Science programme descriptions) remain unchanged. No blanket admissions keyword exclusion or catalogue removal.
- Build sjtu-admissions-1. Applies next scan; original exports are untouched. Appendix links may be useful future discovery candidates but their document content has not been validated. IMDA Cloud failure still awaits recorded errors.

## Tsinghua alias guard — 2026-10-05

- Resumed the interrupted change from the export (3) audit. Tsinghua School of Environment /enven/ and /enven/index.htm contain identical 515-word text in the supplied export. Deduplicate only this exact pair within a scan when organisation, query and whitespace-normalised full text match.
- Different content, organisations and other department pages stay separate. Distinct IEEE webinars and NTU programme variants with shared descriptions are intentionally preserved. Shanghai Jiao Tong's identical programme-page pair remains pending content/provenance review.
- No catalogue edits or retrospective export changes. Build tsinghua-alias-1; Cloud acceptance pending. IMDA failures still require Recorded scan errors; this change does not resolve them.

## Export (3) content-quality review

- Reviewed the shortest 16 records and searched retained text for several common access/challenge phrases; none of those markers matched. This is a limited audit, not certification of all 1,579 records.
- Exclude the exact ASCE committee meeting information form (35 words, administrative submission instructions). Reject MIT professional course-catalog only when extracted text is a short browse-the-catalogue introduction without course records (observed 47 words). Discovery remains enabled; substantive future catalogue content and short named-course lists are not blanket-rejected.
- Preserve concise Energy Institute and Tsinghua course lists. No source removal or master URL changes. IMDA Cloud cause remains unresolved pending recorded errors. Build export3-content-1; new guards apply to subsequent scans, not the supplied export.

## October 1 export (3) Cloud review

- Latest supplied export: 239 scanned sources, 1,579 retained records across 133 organisations. Source totals equal the manifest count. Health: 111 Error, 65 Low evidence, 62 Healthy, 1 No evidence. These counts do not imply all partial-error sources are unusable.
- IMDA overview and GenAI PDF each have zero records and OTHER_SCAN_ERROR. Optional full ICT PDF is absent from the scanned source snapshot, so sectioned retrieval was not tested. Do not mark either IMDA adapter Cloud-verified or infer a particular failure cause.
- NP now reports LISTING_MISSING; MedTech and both SIMTech pages report CONTENT_BODY_MISSING. These remain differences from locally successful responses, not grounds to accept navigation text.
- Requested the two IMDA messages from Recorded scan errors. Added fixed browser/PDF/dependency/code diagnostic categories for future exports while retaining the no-raw-error rule. This does not recover omitted details from an old export or fix the unconfirmed Cloud failure. Catalogue unchanged; no additional full scan requested yet.

## Optional sectioned ICT framework — 2026-10-01

- Supersedes the earlier large-document exclusion: the exact reviewed ICT asset now permits up to 600 pages, retaining its 8 MB and 2 million extracted-character bounds. Other PDFs remain at 400 pages and their existing byte limits. This is not a hard CPU/memory sandbox.
- Live full text extraction succeeds: 12 records covering pages 1–561, approximately 138,000 words including page labels/caveats. One download per scan, sections of up to 50 original page numbers, page-fragment URLs and range titles. These are retrieval boundaries, not semantic categories; table alignment/OCR completeness are not claimed.
- Added IMDA ICT Full Framework (large PDF - optional), disabled by default to avoid unexpectedly swelling government-assistant uploads. Existing sources unchanged. If enabled, the configured evidence cap must accommodate all sections or the source fails without silently returning a partial document.
- Regression tests cover page numbering, invalid markers, cap rejection and a single-download/multi-record workflow. Build ict-pdf-sections-1; Cloud verification pending. Use an isolated optional-source test before a full scan; existing sessions must add the source or deliberately reload defaults (discarding temporary edits).

## PDF page provenance — 2026-10-01

- Read-only bounded inspection confirms the large ICT framework is 561 pages / 5,223,203 bytes. Eight sampled pages show introductory navigation, tracks and a job-role table; this is not full content validation or visual table verification. It remains excluded by the 400-page production limit.
- PDF text now retains [PDF page N] markers using original document numbering, including gaps for pages without extractable text. This supports officer cross-checking and future explicit section ranges; it does not reconstruct table columns or add OCR.
- Existing PDF catalogue regression updated for the intentional page marker. No new sources or scan limits changed. Sectioned retrieval is still pending, not silently enabled. Build pdf-page-references-1.

## IMDA GenAI PDF enabled — 2026-10-01

- Bounded production retrieval/extraction of the GenAI asset succeeds locally: 20 text-bearing pages, 5,620 document words. It includes named technical skills, descriptions, knowledge, abilities and proficiency descriptors. Added a separate enabled government FRAMEWORK / PRIMARY_DISCOVERY source with direct PDF discovery and robots checks; browser rendering is unnecessary.
- Extraction requires the exact final PDF URL, PDF content type and substantive competency markers. Stored evidence is explicit competency text with a warning that multi-column reading order/table alignment may differ. This is text-level validation, not visual verification of proficiency-column relationships; no claim of perfectly reconstructed tables.
- The larger ICT framework is rejected by the 400-page limit. No partial document is stored and no source for it was added. Existing overview references remain references, not proof of PDF coverage.
- Live end-to-end GenAI evidence: 5,642 words including warning; 296 tests passed; build imda-genai-pdf-1. Cloud acceptance pending. Fresh sessions receive the new source; existing session source edits remain untouched.

## PDF retrieval limits foundation — 2026-10-01

- Added an 8,000,000-byte allowance only for the two reviewed exact IMDA PDF asset URLs when the final URL matches and robots permission succeeds. Other PDF/HTML downloads retain the 2,000,000-byte limit. PDF extraction rejects over 400 pages or 2,000,000 extracted characters, with no partial evidence returned.
- These are byte/page/output safeguards, not a hard CPU-time or decompression-memory sandbox. Document text quality remains unverified. Automatic IMDA document discovery and catalogue entries are deliberately not added yet; the overview still reports linked documents as not retrieved.
- Regression coverage checks exact URL allowance, ordinary/redirected defaults, byte/page/text rejection and response cleanup. Next verify actual document parsing/content before enabling them in scans.

## IMDA document references — 2026-10-01

- Two actual rendered overview links were checked with normal robots permission and bounded HTTP reads. Both returned HTTP200 application/pdf: Navigate SFw for ICT (Content-Length 5,223,203 bytes) and New skills in GenAI (2,804,080 bytes). Both exceed the global 2,000,000-byte ceiling; reads stopped at its first exceeding chunk. PDF content was not parsed or validated.
- Preserve the two reviewed same-host /assets/ PDF link titles and URLs in overview text, explicitly marked not retrieved or analysed. Reject external/query/fragment links and deduplicate references. No PDF-content claim, global limit increase or catalogue change.
- 291 tests passed; build imda-document-links-1. Larger-document retrieval remains pending a bounded PDF-specific design. Cloud acceptance pending; no full scan needed solely for these references.

## IMDA scoped browser adapter implemented — 2026-10-01

- Added the separate enabled IMDA ICT Skills Framework Overview source (government agency, supporting discovery, ARTICLE). SkillsFuture and ISA are unchanged. This adds ICT coverage; it does not replace the general sector framework sources.
- Exact-page discovery and browser retrieval preserve robots checks, response status/scope checks, bounded navigation/content waits, rendered-size limits and browser cleanup. Reviewed main article selector excludes site navigation and Contact. Access notices, loading-only or short bodies fail closed; exceptions remain source-level failures, not whole-scan termination.
- Initial live test exposed the container mounting before text; bounded text readiness fixed it. Production adapter then returned 397 overview words locally. Evidence explicitly says linked framework documents were not retrieved and remains inferred professional-resource evidence, not an explicit competency list.
- 290 tests passed; build imda-overview-1. Cloud acceptance pending. Fresh sessions receive the added master source; existing session catalogues are intentionally preserved. Add the exact URL manually with browser rendering, or restore defaults only if willing to discard temporary source edits. Linked PDF retrieval remains separate future work.

## Framework browser checks — 2026-10-01

- Ordinary headless Chromium, after robots permission checks on the configured URLs, was tested without challenge solving or login. SkillsFuture skills-framework redirects to jobsandskills.skillsfuture.gov.sg/frameworks/sector-information and displays an explicit access-restricted message. No further access attempted; not evidence of an empty framework.
- IMDA's https://www.imda.gov.sg/how-we-can-help/techskills-accelerator-tesa/skills-framework-for-infocomm-technology-sfw-for-ict renders substantive public overview content normally after JavaScript. It describes ICT skill areas and links to the framework and GenAI materials. HTTP-only main content had been loading-only. Browser rendering therefore helps this exact candidate, but does not resolve SkillsFuture access.
- Candidate scope is ICT, not all STE sectors. Do not silently replace the general SkillsFuture source or attribute IMDA content solely to SSG. No catalogue edits yet. Next implement a bounded exact-page browser body extraction with provenance and loading/access checks, then test linked document handling separately. The overview is not the full framework or linked PDF content.
- Documentation-only; last suite 285 passed. ISA remains unchanged per user direction.

## SkillsFuture replacement review — 2026-10-01

- Both configured skills-framework and skills-framework/skills-frameworks-faq URLs pass local robots checks but the normal HTTP scanner reports no readable HTML. This differs from the export's insufficient-text category; neither establishes that the underlying organisation lacks useful frameworks.
- Search identified official IMDA alternatives: https://www.imda.gov.sg/how-we-can-help/skills-framework and its directly linked https://www.imda.gov.sg/how-we-can-help/techskills-accelerator-tesa/skills-framework-for-infocomm-technology-sfw-for-ict . Normal permitted retrieval returns only Loading in main on both, not usable framework content. Search snippets are not substituted for extracted evidence; no replacement made.
- These responses may need rendering, but browser success is not yet verified. Do not lower thresholds or treat navigation/loading text as competencies. Catalogue unchanged; no new test run for this documentation-only review (last suite 285 passed).
- User decision: leave all ISA sources unchanged for now; retain permission review as a later task, not an automatic exclusion.

## ISA programme review — 2026-10-01

- Configured ISA/IEC 62443 Cybersecurity Certificate Program URL is robots-permitted and returns substantive programme content locally, including certificate levels, prerequisites and linked training formats. This differs from the supplied Cloud insufficient-text outcome; Cloud cause remains unconfirmed.
- The same response displays a publisher notice restricting entry of ISA intellectual property into AI tools without express permission. Because the intended downstream workflow uploads collected evidence to a government AI assistant, seek organisational permission/licensing review before expanding extraction or transferring ISA material. Robots permission and public accessibility do not resolve that question. This is an observed notice, not a legal determination.
- No parser expansion, replacement URL, disabling or deletion performed. Existing ISA sources remain unchanged pending user direction on permission or exclusion. Documentation-only; last code suite 285 passed. Other organisations can continue to be tuned independently.

## MedTech short overview — 2026-10-01

- Normal permitted local retrieval finds 129/176/78 visible body words on the root/pillars/enablers pages. Production extraction retains 119/156 words on the first two but rejected Enablers under the general 100-word minimum.
- Exact Enablers route now accepts at least 50 words only with all five reviewed names present, preserves its body and labels it as a public overview, not a detailed competency framework. Missing reviewed sections now fail closed rather than falling back to page navigation. General thresholds unchanged.
- 285 tests passed; build medtech-overview-1. No catalogue edits. This fixes a reproduced short-page rejection, not the unconfirmed reason for all Cloud MedTech output being empty. Cloud verification pending.

## SIMTech missing-body review — 2026-10-01

- Investigated the two CONTENT_BODY_MISSING zero-output rows in the October 1 export: Sustainability Informatics & Strategy and Industrial Automation. Both URLs pass current local robots checks, retain their configured URL and expose the expected rich-text body.
- End-to-end production extraction succeeds locally: 211 words of sustainability research capabilities (performance quantification, decarbonisation, resource circularity and digital platforms), and 239 words of industrial automation programme overview. These are overview records, not complete module syllabi.
- The existing selectors match both local responses; no broader selector, URL replacement or source disablement is justified. Cloud response differences remain unresolved. This is a local check, not a Cloud recovery claim. Future investigation should use the Recorded scan errors section and richer diagnostics; never relax missing-body guards to admit navigation content.
- Documentation-only checkpoint; no code changes or new test run. Last full regression suite: 284 passed. Continue remaining insufficient-content cases; no full rescan requested solely for these checks.

## NP Cloud discrepancy diagnostics — 2026-10-01

- Normal robots-aware local discovery still returns nine NP engineering course links. This does not reproduce the Cloud zero-output result and is not proof of recovered Cloud extraction. No speculative catalogue or selector changes made.
- Diagnostic export now distinguishes missing course listings, unexpected redirects, network failures and common HTTP failures. Repeated source errors retain the union of their categories rather than overwriting earlier errors. Only fixed categories are exported, never raw exception details or secret URLs.
- 284 tests passed. Prior OTHER_SCAN_ERROR cannot be retroactively resolved from the supplied export. Next relevant scan can carry the richer categories; no full scan needed solely for this diagnostic change.

## October 1 full-scan acceptance and navigation fix

- Reviewed public_evidence (2).txt: 237 sources, 1,591 records across 132 organisations; per-source counts sum to 1,591 and match the manifest. Health: 109 Error, 64 Low evidence, 63 Healthy, 1 No evidence. Errors can include partial success; 48 sources actually have zero records.
- Zero-output diagnostic occurrences: 21 EMPTY_HTML, 11 ROBOTS_RESTRICTED, 7 ACCESS_BLOCKED, 4 INSUFFICIENT_TEXT, 2 CONTENT_BODY_MISSING, 1 NO_LINKS, 1 OTHER_SCAN_ERROR. Categories are recorded hints, not definitive causes; the remaining zero-output row has no category.
- SLA reviewed pages retain 197/169 words; RICS reviewed duplicate pair appears once; Zhejiang yields seven items (with a partial insufficient-text error); NTU Robotics has one scoped programme. Peking graduate/degree pages remain zero under robots restrictions. Ngee Ann engineering remains zero with OTHER_SCAN_ERROR and needs more specific diagnostics before a parser change.
- Fixed page reset after operations: persist navigation in a separate non-widget session key, restored when the sidebar returns after scan/lock early exits. Regression tests cover both hidden-sidebar paths. Existing download tests verify explicit preparation and reuse without regeneration. 282 tests passed. No source catalogue edits this round; user should verify scan and TXT preparation stay on Scan & Download after deployment.

## RICS PDF alias review — 2026-10-01

- Supplied September 29 export records 1233 and 1240 contain the same 3,839-word Real Estate Agency Associate Assessment guide at two PDF URLs. Added an exact-pair within-scan identity requiring matching organisation, query and whitespace-normalised full text. Other pathway guides and changed versions remain separate.
- No catalogue changes, archived-export rewrites or broad PDF deduplication. Review uses supplied content, not a new live-site availability check. Older document dates remain in their text; retrieval does not establish current applicability.
- 280 tests passed; build rics-dedup-1. Cloud verification pending. Next consolidated scan should verify the accumulated scoped extraction and diagnostic changes; no scan required solely for this duplicate pair.

## NEA overview duplicate — 2026-09-29

- Supplied export has identical 554-word Waste Minimisation and Recycling text at the 3R root and its waste-minimisation-and-recycling child. A narrow within-scan guard now keeps the first only when organisation, query and normalised full text match.
- Other child pages (including at-work, food waste, EPR and the Zero Waste Manager Course) remain separate. Different overview content is retained; no global text deduplication or catalogue change. Existing exports are unchanged.
- 279 tests passed; build nea-dedup-1. Cloud acceptance pending. Continue remaining content review before requesting the next consolidated scan.

## Peking programme scope — 2026-09-29

- Latest export includes homepage text and scholarship navigation attributed to the graduate-programme source. Local configured graduate introduction and biotechnology degree pages both return substantive programme bodies (213 and 741 visible main-body words before cleanup), including research-training skills and degree outcomes.
- Added exact standalone routes and main.pad80 extraction for those two configured pages. No scholarship/admissions/student-life expansion; a homepage redirect lacks the reviewed route and is rejected. This is programme-page coverage, not all linked curricula. No URLs or enabled flags changed.
- 278 tests passed; build pku-programmes-1. Cloud acceptance pending. Continue remaining evidence-content review before the next consolidated scan.

## Duplicate-content review — 2026-09-29

- Supplied export includes identical 850-word SUTD ESD course lists under the same path with and without a trailing slash. Narrow within-scan dedup now retains the first only when organisation, query and whitespace-normalised text also match. Changed content remains distinct; other sites unaffected.
- Other exact-text pairs include distinct IEEE webinar IDs and NTU programme variants. These are deliberately not globally merged: identical text does not prove identical resources. NEA parent/child, Peking scholarship/homepage and RICS duplicate-document pairs remain candidates for provenance/content review, not silently removed.
- 276 tests passed. Build sutd-dedup-1; no catalogue edits. Existing exported file unchanged; next scan applies the guard. No full rescan needed solely for this duplicate.

## Zhejiang structured listing — 2026-09-29

- Sustainability root embeds article destinations in span.url fields rather than normal anchors. Exact-page discovery now reads those fields and admits only same-host dated English article paths, with robots checks, deduplication and article caps. Listing snippets, assets and external URLs are not returned as evidence.
- Local check: eight candidates; first two extracted 733 and 303 words. These are campus sustainability/news signals, not competency lists. Dates include older material; no freshness or comprehensive-coverage claim. Linked report PDF is not included in this article-only route.
- 275 tests passed. Build zju-discovery-1; no catalogue changes. Cloud acceptance pending.

## SLA content scoping — 2026-09-29

- Both configured SLA Master Plan and OneMap pages are readable locally. Exact standalone routing and the main content-column selector now retain the actual policy/platform descriptions rather than government-banner articles or navigation. Verified 197 and 169 words respectively. These are overviews, not full competency lists or the linked master-plan document.
- Selector regression includes a similarly classed heading to ensure the body, not just the title, is selected. Robots/missing-body/short-text guards remain. No URL or catalogue edits.
- Zhejiang sustainability root returns HTML (1,138 total visible words) locally, but content quality and discovery are not yet verified; no recovery claim or code change there.
- 274 tests passed. Build sla-content-1. Prior Cloud failure causes remain unconfirmed; these are local extraction checks. No new full scan required yet.

## Newly empty PUB / Cambridge access checks — 2026-09-29

- PUB robots.txt returned HTTP200 with `User-agent: *` and `Disallow: /`. Permission checks deny the configured R&D and Code of Practices URLs. This explains current local inability to crawl; it does not prove the exact cause of the earlier Cloud failure. No alternate path on the same host can bypass this rule. Keep catalogue unchanged pending an authorised accessible equivalent; do not fetch disallowed pages.
- Cambridge engineering news returned HTTP503. A subsequent official homepage alternative check stopped because robots.txt itself returned HTTP503. This is current unavailability, not evidence that the engineering news has permanently moved. The general Cambridge news source still has 21 records in the supplied Cloud export.
- No parser, URL or enablement change is justified by these checks. Documentation-only round; last code verification 272 tests passed. Next review other newly empty sources and continue using the supplied export; no full rescan requested solely for these access checks.

## Reviewed administrative noise — 2026-09-29

- Reviewed the seven records under 30 words and administrative-title candidates in the latest export. Four short EI records are legitimate named-course lists and remain accepted. AI Singapore's privacy research article is useful, not a privacy-policy page.
- Added exact host/path exclusions at the scan boundary for ASCE committee-application-form, NEA grants-and-awards listing (12 words), and Tsinghua research-recruit-ra-en listing (17 words). These records contain administrative/navigation content rather than technical competencies or courses. No blanket keyword rejection; technical child pages and other domains remain unaffected. Configured sources stay enabled.
- The NTU generic listing was already addressed by programme-scoped discovery in the preceding update. Build cloud-noise-1; 272 tests passed. Existing exports unchanged; these exclusions apply on the next scan. Continue reviewing current evidence before another full scan.

## Post-export corrections — 2026-09-29

- NTU MSc Robotics supplied export has a substantive 2,323-word programme record plus a scholarship form, generic programme listing and unrelated undergraduate degrees. Exact programme discovery now returns only its configured page, retaining existing extraction. This deliberately does not claim retrieval of every linked syllabus. No global NTU restriction or catalogue edit.
- New TXT exports include source-specific fixed Diagnostic categories derived from recorded errors (timeouts, access restrictions, missing bodies, insufficient text, etc.). Raw exceptions, URLs embedded in errors, local paths and secrets are not copied. Categories are hints, not proof of root cause; empty categories do not certify health. Existing exported files cannot be retroactively diagnosed.
- Build cloud-review-1. Tests cover source-name separation, safe category output, and scoped NTU routing. Next examine remaining content quality before requesting another full scan.

## Cloud acceptance export — 2026-09-29

- User confirmed deployment/URL/scan/download checkpoint and supplied public_evidence (1).txt. Scan 02:37–03:09 UTC: 237 sources, 1,580 evidence, 133 organisations, COMPLETED_WITH_ERRORS. Actual evidence count and summed health counts both equal 1,580. Previous export: 236 sources, 1,611 evidence, 131 organisations. These different catalogues are not a controlled benchmark.
- Health: 106 Error, 66 Low evidence, 64 Healthy, one No evidence. Zero-output sources rose from 44 to 47. Partial Error sources can still retain useful evidence. No sampled access-challenge marker matches found in stored text; not a comprehensive quality guarantee.
- Confirmed useful Cloud output: AISG 25 substantial research articles; NParks research six records with programme content; EI nine course lists (not syllabuses); HKUST education 1,374 words; Polimi 694/611 words; ISA IC32 341 words; IEEE storage outline 73 words including disclaimer. NUS Urban Design also now has one record. General HKUST root recovered 17 records but still needs content review.
- ICE both rows zero, SIMTech industrial automation zero, NP engineering zero: local fixes not accepted as Cloud recovery. ICE canonical row can be skipped after the alias attempted the same URL, since dedup tracks attempted URLs. Export has generic reasons only, so exact Cloud exception cannot be established here. Need source-level error diagnostics before prescribing an access/parser fix.
- Newly zero compared with previous export include ISA certificate programme, four PUB sources, two SLA sources, Tokyo graduate engineering, Cambridge news and Zhejiang. Do not infer permanent removal from one failed run.
- Content issue remains: NTU robotics source includes application-form material and an unrelated cultural-leadership item; seven total records have fewer than 30 words (some are legitimate course lists). Next priority: narrow NTU programme discovery and improve exported failure diagnostics. Do not ask for another full scan solely to repeat these observations.

## NUS curricula follow-up / next Cloud checkpoint — 2026-09-29

- Configured Civil Engineering courses, Environmental Engineering courses, Industry 4.0 specialisation and MSc Project Management pages all returned no readable HTML through permission-checked HTTP. This check does not establish that the underlying programmes lack content.
- Official Civil Engineering `https://cde.nus.edu.sg/cee/undergraduate/beng-civil/build-your-own-degree-civil-engineering/` is indexed with relevant curriculum information, but HTTP and normal Chromium both returned an Incapsula access notice (browser HTTP200, six words). No replacement made; no bypass attempted. The other three pages were HTTP-tested only this round.
- Documentation-only update; no catalogue or runtime changes, last full code suite 262 passed.
- NEXT CHECKPOINT: run a full Streamlit Cloud scan on the deployed updates, then export public_evidence.txt. Existing sessions must use the revised AI Singapore research archive URL to exercise that change; Restore defaults also loads other master additions but discards temporary source edits. Build ieee-outline-1 identifies the latest runtime. Compare extracted content and failures against the September24 export, not just evidence counts. Cloud recovery is still unverified until this scan.

## IEEE short outline / SAE / HDB — 2026-09-29

- Reviewed IEEE PES Grid Energy Storage tutorial: public body contains a useful 65-word four-session outline, rejected by the 100-word minimum. Exact standalone routing now targets the resource itself. A narrow 50-word minimum applies only to this exact page when all four session markers and energy-storage content remain present; other descriptions retain the existing threshold. Evidence still explicitly states full resource not retrieved. Slides were not downloaded.
- SAE standards root returns only 26 words locally, insufficient to verify standards content. HDB homepage redirects to a general housing-services homepage, not a useful competency/course source. No replacement verified in this round; both remain unchanged and unresolved for tuning.
- 262 tests passed. Build ieee-outline-1. No master catalogue changes; Cloud acceptance pending.

## NUS access-limited programmes — 2026-09-29

- Reviewed configured SCALE BTech Civil Engineering, CDE Biomedical Engineering undergraduate, and FASS Professional Certificate in Applied GIS pages. Robots permitted requests; HTTP returned no readable HTML. Normal Chromium returned HTTP 200 with only six-word `Request unsuccessful / Incapsula incident ID` notices on all three, not programme evidence. No challenge interaction or bypass attempted.
- Official search results confirm the BTech and PC GIS pages contain relevant programme information, but search indexing is not evidence of collector access. Tested the current AY2026/27 NUS Bulletin undergraduate SCALE page as a same-programme alternative: HTTP also returned no readable HTML. Historical 2019/20 bulletins were not substituted for current curricula.
- Decision: keep existing URLs and enablement unchanged; no accessible same-programme replacement verified in this round. Do not turn Browser on globally or accept blocked text. A source-specific access failure must continue to be skipped and reported while other sources scan.
- This round changes documentation only; last code verification remains 261 passing tests. Cloud behaviour may differ and has not been retested. These sources remain unresolved, not marked healthy or deleted.

## SIMTech training / ICE alias / EMA — 2026-09-29

- SIMTech Industrial Automation is locally readable. Exact standalone routing and the main rich-text block preserve a 239-word overview with four named 42-hour modules, excluding global navigation and fee/funding blocks. This is a programme overview, not retrieval of every module syllabus.
- Legacy ICE /attributes locally reproduces the reviewed attributes page. Discovery now maps it to the existing canonical membership-attributes URL, respecting permission on both URLs. Existing within-scan URL deduplication prevents duplicate storage when both sources are enabled; the first source owns the retained evidence. No catalogue rows deleted.
- EMA media releases still returns no readable HTML through permission-checked HTTP. Remains unresolved and unchanged; no bypass attempted.
- 261 tests passed. Build simtech-training-1; no master catalogue changes or reset needed. Local success does not prove Cloud recovery. Consolidated Cloud acceptance remains pending.

## Polimi / Tokyo follow-up — 2026-09-29

- Both configured Polimi programme pages return useful local HTML. Exact-page standalone routing now avoids unrelated secondary discovery; extraction preserves main programme content, degree level, subjects and career information, excluding global navigation. Building Engineering for Sustainability yielded 694 words; Civil Engineering yielded 611.
- The Civil Engineering page explicitly says Bachelor of Science despite the configured URL containing laurea-magistrale. Preserve the publisher's actual text; do not infer degree level from URL. Building Engineering for Sustainability explicitly says Master of Science. No URLs or source types changed.
- University of Tokyo's configured engineering page still times out during connection; unresolved, not disabled or replaced. HKUST general sustainability root is readable (about 1,003 main-body words), but mostly institutional overview; no additional tuning or recovery claim in this round.
- 259 tests passed. Build polimi-programmes-1. These are local checks, not confirmation of earlier Cloud failure causes or Cloud recovery. Continue empty-source review; consolidated scan acceptance remains pending.

## AI Singapore / SkillsFuture follow-up — 2026-09-28

- The old AISG research/features page links mostly to connect.aisingapore.org, whose robots endpoint returned 401; no bypass attempted. The publisher-linked research category archive on aisingapore.org is accessible. Master AI Singapore URL replaced with https://aisingapore.org/category/ai-research/ (same organisation and INDEX classification).
- Scoped article-card discovery with bounded listing pagination, robots checks, same-domain links and tracking-query removal yielded 25 candidates. Three sampled full article extractions returned 580, 526 and 673 words with substantive research descriptions. This is research/news signal evidence, not a competency framework or a full-scan validation of every candidate.
- Both configured SkillsFuture framework/FAQ URLs still yield no readable HTML through permission-checked HTTP; indexed search content does not establish crawler access. URLs unchanged, unresolved.
- Build aisg-research-1. Existing sessions retain their source copy: edit the AI Singapore URL manually or Restore default sources (which discards temporary source edits). Cloud acceptance pending.

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
