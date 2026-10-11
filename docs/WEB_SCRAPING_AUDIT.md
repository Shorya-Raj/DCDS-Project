# Web scraping and tender-data collection audit

**Audit date:** 11 October 2026  
**Coverage:** Maharashtra tender records, with a 2026 publication-date filter where the source supplied a publication date  
**Status:** Historical work documented; the available 2026 collection is not a complete calendar-year archive.

### Follow-up review of the tender records (11 October 2026)

The earlier sections below describe the merged baseline workbook before the record-level follow-up. The reviewed working copy preserves the three original sheets and adds a `Record Review` tab. That workbook is retained outside this Git repository because its official detail URLs can contain browser-session query values.

- The copy retains **1,619 unique Tender IDs**, including 1,574 included official records and 45 excluded third-party details. The six repeated organisation/reference/title groups (14 records) remain separate; Tender ID remains the key. No rows were deleted or merged.
- A retained 10 October official capture for `2026_NMC_1342575_23` supplied its exact detail URL and the later schedule: submission closes **13 October 2026, 3:00 PM**; opening is **14 October 2026, 3:00 PM**. The original 3 October collection date is retained and the earlier `Open` status is labeled as a screenshot snapshot. SQL readiness is now **1,572**; Mongo detail readiness remains **1,573**. Two rows still lack exact detail-page evidence and are held out of the first import, but remain in the master workbook.
- Correcting that schedule changes the number of included rows with closing dates before 10 October from 22 to **21**. Portal status remains a dated snapshot, not a current-status check.
- Record #1356 (`2026_NMC_1342575_11`) has a captured portal title naming Satpur/P.No.09, while its own location and work description name Nashik East/P.No.14. The title is retained verbatim and flagged for notice-document review.
- The `DCDS-Project` loader now maps `.xlsx` Tender Log rows by Tender ID. Its dry run on the reviewed copy reports **1,572 ready**, **2 held**, and **45 `Include? = No` rows excluded**. This validates field mapping only; MySQL/MongoDB import has not been run.
- The 9 October `NEW ↓` manifest's 129 pending URLs remain a historical count and still need link-by-link reconciliation. Third-party leads remain separate; the 108 undated Tender247 leads and 45 unverified TenderShark details were not promoted.

The reviewed workbook fingerprint is SHA-256 `FAA13CA941E03F94621D1D27B85E9911036CBB6D9A20C00AE89885B0DDEF593A`.

### Import preparation checkpoint (11 October 2026)

The reviewed workbook was checked again while preparing the next import step. Tender Log rows 9 and 10 remain held because they lack exact detail-page evidence; row 11 (`2026_NMC_1342575_23`) retains its verified URL and corrected schedule. Record #1356's title/location conflict still requires checking the official notice document. No rows were deleted or merged.

The loader now has a `--sample-size` option that selects a deterministic, evenly spread sample from the import-ready records. This prepares the planned 25-record first database test and repeat-import check. Official MongoDB documents now also include the `categories` array used by the project's category aggregation, and optional date fields are emitted as ISO dates. These are code changes only; no database import has been performed.

Verification on the bundled Python 3.12.14 runtime with `openpyxl` 3.1.5:

| Check | Result |
|---|---|
| Unit tests | 7 passed |
| Workbook dry run | 1,572 ready; rows 9 and 10 held; 45 `Include? = No` rows excluded |
| Spread-sample dry run | 25 selected from the 1,572 ready rows; no database connection opened |
| Python compilation | Normalizer, loader and test module compiled successfully |
| MySQL / MongoDB ports | `127.0.0.1:3306` and `127.0.0.1:27017` refused connections |

The documented virtual-environment interpreter still points to the unavailable Windows Store Python. Its existing `Lib/site-packages` contains Streamlit 1.65.0, MySQL Connector 9.7.0, PyMongo 4.18.2, `python-dotenv` 1.2.4 and `openpyxl` 3.1.5. Using the bundled Python 3.12.14 runtime with that directory on `PYTHONPATH`, the sample-mode dashboard rendered in a browser: 129 sample listings appeared, and the `Nashik` search returned two records. The local server health endpoint and page both returned HTTP 200; the server and test tab were closed afterward. This verifies the sample mode only. The `AppTest` harness did not complete within about 35 seconds and was stopped; the browser smoke test supplied the UI check instead.

Docker and Podman commands are unavailable, WSL is not installed, and ports 3306 and 27017 refuse connections. No database sample import, repeat pass, cross-store reconciliation or full 1,572-record load has been performed. The project dependencies can be used through the current host workaround, but the saved virtual-environment interpreter itself remains broken. See [the chronological work log](WORK_LOG.md) for the exact checks and remaining sequence.

This report records the tender collection and merge work that can be substantiated from the saved workbooks, JSONL captures, manifests, validation scripts, and prior task history. It does not claim that every Maharashtra tender published in 2026 was found. No new web scraping was performed to prepare this report.

## Executive summary

The current workbook contains **1,619 unique Tender Log IDs**. It consists of 1,574 records already in the Maharashtra collection plus 45 new, dated third-party detail records. Sixteen external-source rows were linked to existing Maharashtra tender records and were not added as duplicate log rows. Another 108 external leads without a captured 2026 publication date remain on the `External Sources` audit sheet.

The largest saved official-site capture occurred on 10 October 2026. Two raw capture files contain 1,348 page captures in total: 107 in the first batch and 1,241 in the second. The first batch added 107 records. In the second batch, 5 Tender IDs were already represented in the workbook, so 1,236 were added. The official log therefore grew from 231 existing IDs to 1,574 IDs before the third-party merge.

The secondary-source workbook contains 169 combined records derived from 127 Tender247 index leads and 46 TenderShark detail pages, with four cross-platform overlaps combined into shared source rows. The aggregator records remain labeled as third-party; they are not treated as official confirmations.

## Scope and source authority

The user's final scope was **Maharashtra only**. For the 2026 dataset, a record counted as in-year when its **publication date** was in 2026. The 10 October official capture was specifically from the portal's Civil Works results. The secondary-source data was also restricted to Maharashtra.

| Source | Role | Fields available in the saved collection | Authority and limits |
|---|---|---|---|
| Maharashtra eProcurement portal (`mahatenders.gov.in`) | Primary source for official detail-page captures | Tender ID and reference, title, organisation chain, location, published/closing/opening dates, values and fees, work description/eligibility, document names and source URL | Primary portal display at capture time. The captured status and later corrigenda were not independently checked. |
| Tender247 | Maharashtra index/listing leads | Source listing ID, title, location/category, values/EMD where shown, listing URL | Secondary source. Publication date was not captured for the index-only leads, so those leads were not added to the 2026 log on date evidence alone. |
| TenderShark | Maharashtra detail pages | Source detail URL, source-reported ID/reference, category/location, publication and closing dates, values/EMD where shown | Secondary source. The source's displayed publication date was used for the 2026 screen; tender details still require official notice/corrigendum verification. |

Other portals and broader sources were explored early in the work, including CPPP, Uttar Pradesh and Odisha/NIC pages. CAPTCHA, access, or socket restrictions prevented usable extraction, and no records from those sources were added. The final data remains Maharashtra-only.

## Collection history

| Date / stage | Activity and result | Evidence status |
|---|---|---|
| Earlier screenshot batches; exact capture dates are not preserved in the current evidence bundle | Prior task history records screenshot-based batches, including a later 31-record batch that brought that workbook snapshot to 68 rows. Duplicate IDs were entered once and screenshot groups without a readable Tender ID were excluded. A later user-requested clean reset preserved the workbook structure and a populated backup. | Historical conversation record. These batch totals are not added again to the current workbook total because the later 231-row baseline is not fully itemized against those temporary batch files. |
| Earlier link-based portal work | The extraction guide records that a prior chat added 189 linked records to a collection that already contained earlier records. The retained workspace does not contain the raw page-by-page JSONL for that 189-record batch, so it is not independently replayable from the current evidence files. | History-reported, not revalidated from a raw capture file in this audit. |
| 5 October 2026 | A separate Maharashtra-only aggregator workbook was prepared from Tender247 and TenderShark. The saved source notes say the source snapshot was collected on 5 October. | Workbooks and source notes retained locally. |
| 9 October 2026 | A manifest was generated from the supplied `WEB SCRAPED DATA MAHARASHTRA TENDERS (2).docx`, beginning after the `NEW ↓` marker and retaining section headings/positions. It contains 336 hyperlink occurrences reduced to 319 distinct URLs. At that snapshot, 190 were flagged already recorded and 129 as not yet recorded. The follow-up task switched to building the reusable extraction guide and skill; those 129 links were not extracted in that task. | Manifest retained. The recorded flags describe 9 October only and are not a current pending count. |
| 9–10 October 2026 | Two official detail links were tested after opening the portal homepage in the same browser session; both examples opened without a CAPTCHA. This verified the method for those examples only. | Documented observation in the extraction guide. |
| 10 October 2026 | The user opened the portal, solved the search CAPTCHA, and clicked Search. The visible Civil Works detail pages were captured in two JSONL batches. No automated CAPTCHA solving or search-form submission was used by the extractor. | Raw captures and a 107-URL manifest retained. |
| 11 October 2026 | The dated third-party detail records were merged into the Maharashtra workbook with a separate `External Sources` audit sheet, source-aware match decisions and unique record IDs. | Builder, pre-merge backup, final workbook and passing validation outputs retained. |

### Earlier screenshot history

Prior task messages report successive screenshot-driven workbook snapshots, including 20 records, a later 14-record addition reaching 37, and a later 31-record addition reaching 68. Those counts describe historic workbook states, not extra rows to add to the current total. Some screenshot-derived rows had no detail-page URL and could not be SQL-ready. Three screenshot groups without a visible Tender ID were excluded rather than assigned guessed IDs.

## Official Civil Works capture accounting

| Batch | Raw captured pages | Unique IDs in batch | Already represented when appended | Newly added | Publication-date range in capture |
|---|---:|---:|---:|---:|---|
| `2026-10-10-civil-capture.jsonl` | 107 | 107 | 0 | 107 | 9–10 October 2026 |
| `2026-10-10-civil-capture-pages-7-83.jsonl` | 1,241 | 1,241 | 5 | 1,236 | 25 March–9 October 2026 |
| **Total** | **1,348** | **1,344 distinct across both files** | **5 overlaps against the 338-row pre-second-batch log** | **1,343 added to the 231-row baseline** | **25 March–10 October 2026** |

All 107 rows in the first batch and all 1,241 rows in the second capture are marked `captured`, are categorized as `Civil Works`, have a 2026 publication date, and have no `missing_required` fields in the raw capture. The second file has four Tender IDs repeated from the first capture; one more second-batch Tender ID was already in the earlier 231-row log. Those five overlaps were not imported again.

The second-batch overlap IDs are:

- Repeated between the two 10 October capture files: `2026_MCGM_1312580_9`, `2026_MMC_1343674_11`, `2026_MMC_1343674_17`, and `2026_MMC_1343674_18`.
- Already in the 231-row baseline: `2026_NMC_1342575_23`.

The recorded capture windows were 12:30:13–12:35:04 UTC for batch 1 and 12:46:33–13:07:02 UTC for batch 2 on 10 October 2026.

The page extractor reads the visible detail-page DOM and records raw page fields, the requested/resolved page URL, capture time and document names/link presence. It does not fetch or download tender documents. The workbook stores document names, not the document contents or durable document URLs. New Civil Works rows keep status as `Unknown`; an active result list alone does not prove a tender remains open or that no corrigendum has changed it.

## Secondary-source collection and merge

The source workbooks preserve the two secondary sources separately before combination:

- `Maharashtra_Work_Tenders_2026_Expanded.xlsx`: 46 TenderShark detail records with a displayed 2026 publication date and 127 Tender247 index leads.
- `Maharashtra_Work_Tenders_Combined_2026.xlsx`: 169 combined source rows after four defensible Tender247/TenderShark overlaps were represented once while retaining both platforms' identifiers, values and URLs. The four Tender247 listing IDs recorded for those cross-platform matches were `101866252`, `102236361`, `104627883`, and `104513013`.

The final merge into the main workbook made these decisions:

| Disposition | Count | Treatment |
|---|---:|---|
| Matched to an existing Maharashtra Tender ID | 16 | Kept the official log row; recorded the secondary-source match and evidence in `External Sources` and in the official row's notes. No extra Tender Log row was created. |
| New dated third-party detail records | 45 | Added to `Tender Log` with synthetic keys of the form `tendershark:<source-UUID>`, source provenance and the raw source-reported ID/value strings in notes/audit fields. `Include?` remains `No`, and status remains `Unknown`, pending official verification. |
| Undated index leads | 108 | Preserved in `External Sources`; not counted in the 2026 Tender Log because a 2026 publication date was not captured. |
| **Total source rows retained for review** | **169** | Every row from the combined external-source workbook was copied to `External Sources`. |

The 16 cross-source matches were assessed using tender ID/reference when present plus project title/scope, location, value/EMD and/or deadline. Title similarity alone was not accepted as a match. Source-row to official Tender ID mappings:

| Combined source row | Official Tender ID | Tender Log row |
|---:|---|---:|
| 62 | `2026_CIDCO_1341159_1` | 1523 |
| 64 | `2026_PWDRP_1340912_3` | 172 |
| 69 | `2026_PWDRP_1340912_2` | 173 |
| 77 | `2026_MMRDA_1325856_1` | 1567 |
| 83 | `2026_SAI_1339997_1` | 1547 |
| 86 | `2026_MCGM_1337757_1` | 171 |
| 89 | `2026_CIDCO_1340477_1` | 1543 |
| 90 | `2026_MCGM_1336888_1` | 44 |
| 91 | `2026_MMB_1342450_1` | 1377 |
| 107 | `2026_MSIDC_1339226_1` | 1553 |
| 110 | `2026_MSIDC_1339232_1` | 1554 |
| 114 | `2026_MMRDA_1336820_1` | 1564 |
| 115 | `2026_MHADA_1342269_2` | 39 |
| 117 | `2026_MCGM_1341568_1` | 43 |
| 126 | `2026_DMA_1342088_1` | 1425 |
| 175 | `2026_SATAR_1290336_1` | 1582 |

For source row 175, the reference/project and EMD support the match, but the source deadline was older than the official page's deadline; the discrepancy is recorded rather than silently overwritten.

Potential duplicate groups within the undated Tender247 leads were flagged but not collapsed: rows 53/54, 94/95 and 96/97 have strong similarity signals; rows 39/42/44 are similar Ward 8 notices with no official IDs; rows 17/18 differ in location/value/deadline; rows 66/80 share a title but differ in value/deadline. These remain separate pending official-ID or source-page review.

The merged external audit sheet's platform labels break down to 123 Tender247-only rows, 4 rows carrying both TenderShark and Tender247 provenance, and 42 TenderShark-only rows. Separately, a prior review of the 1,574-record Maharashtra subset found six repeated organisation/reference/title groups covering 14 rows. Those text collisions were not treated as duplicates because Tender IDs and/or substantive fields differ; rows 139 and 142 remain an unresolved possible duplicate pair pending source-page review.

## Final workbook state and data-quality notes

The final workbook has three sheets: `Tender Log`, `Field Guide` and `External Sources`.

| Final measure | Value |
|---|---:|
| Tender Log IDs | 1,619, all unique |
| Included records | 1,574 |
| Detail-captured records | 1,573 |
| SQL-ready records | 1,571 |
| Mongo-detail-ready records | 1,573 |
| Newly added third-party records excluded from `Include?` | 45 |
| External review rows not in the 2026 log | 108 |

Three pre-existing Maharashtra rows have no `Source Detail URL` and therefore are not SQL-ready: Tender Log rows 9–11 (`2026_MCGM_1342628_1`, `2026_MCGM_1342626_1`, `2026_NMC_1342575_23`). The main workbook's summary counters reflect the final 1,619-row table. A formula-error scan during the workbook build found zero error matches; the final post-merge reconciliation also found no data/ID/source-row errors.

## Validation performed

The following checks were run against the saved artifacts on 11 October 2026:

| Check | Result |
|---|---|
| `mahatenders-extract/scripts/validate_capture.py` against the 107-row Civil Works manifest/capture | 107 URLs in manifest, 107 captured, 0 CAPTCHA, 0 unavailable, 0 not attempted, no errors |
| `mahatenders-extract/scripts/verify_civil_workbook.py` | 107 imported rows compared to raw official captures, no errors |
| `mahatenders-extract/scripts/verify_civil_remaining.py` | 1,236 newly imported rows compared, 5 overlaps excluded, 1,574 official IDs, no errors |
| `artifact_build/verify_external_merge.py` | 169 raw source rows copied; 45 added, 16 matched, 108 undated; 1,619 unique final IDs; no errors |
| Source/capture profile | Every record in both 10 October raw capture files had a unique Tender ID and URL within that file, `Civil Works` category, 2026 publication date and an empty `missing_required` list. Four Tender IDs/URLs overlap between the two capture files. |

The remaining-capture verifier was aligned to the final workbook after the third-party merge: the current table and summary formulas extend to row 1627 rather than the pre-merge row 1582. Its row-level comparison then passed with no errors.

## Limits and unresolved work

1. **Not a full-year archive.** The latest saved official captures are dated 10 October 2026. The calendar year was still in progress, so later 2026 tenders and portal changes are outside this snapshot.
2. **129-link snapshot needs reconciliation.** The 9 October manifest marked 129 of 319 distinct `NEW ↓` links as not yet recorded at that time. The later Civil Works capture URLs do not exactly equal those session-token URLs. The manifest has URLs but no Tender IDs, so overlap by Tender ID has not been established. Regenerate the manifest against the current workbook and resolve those links before describing them as still pending or complete.
3. **231-row pre-capture baseline is not fully traceable here.** The two 10 October capture files validate the 1,343 additions; retained raw captures do not individually reconstruct every record that was already in the 231-row baseline.
4. **Official status/corrigenda were not checked.** Captures establish what the detail pages displayed at capture time. They do not establish current open/closed status, amendments, award results or later corrigenda.
5. **Secondary records are leads.** The 45 TenderShark-derived additions have not all been independently verified against official tender pages. They remain excluded from the included-record count. The 108 undated Tender247 leads need a publication-date source before being considered for the 2026 log.
6. **Three missing source URLs.** The three rows listed above remain traceability gaps. Do not reconstruct a detail URL from a Tender ID or screenshot.
7. **Some possible duplicates remain unresolved.** The review flags listed above are not confirmed duplicates. The official collection's record key remains Tender ID; repeated organisation/reference/title text is only a review signal.
8. **Raw portal links are session-bearing.** Capture URLs include session/query parameters and may not open in another browser or remain valid. This report deliberately omits those full URLs. Redact the session/query values before publishing any raw manifest/capture file to a public repository.
9. **Repository boundary.** At the time of this 11 October report, the project folder had not yet been initialized as a Git repository. The audit and application are now being prepared for version control; the raw workbooks and capture JSONL files listed below remain outside the repository and are not part of a fresh clone.

## Evidence inventory and file fingerprints

Paths below are relative to the private parent `DCDS ESE` workspace, not this repository. SHA-256 fingerprints identify the saved local snapshots used for the report; the files themselves are not included in Git.

| Evidence artifact | Workspace-relative path | SHA-256 |
|---|---|---|
| Final merged workbook | `outputs/01a10826-579d-78f1-b00a-f33d738ff767/Maharashtra_Tender_Data_Collection_Cleared_2026_Updated.xlsx` | `20AF67F70ECE4DFECA9AD9CD7269847712857E391826969343873E2A729547B8` |
| Combined secondary-source workbook | `outputs/01a10826-579d-78f1-b00a-f33d738ff767/Maharashtra_Work_Tenders_Combined_2026.xlsx` | `3F182E98BA37AF76333B16943F6902072CCC4B666A7C87F8B9A7FDC91049904A` |
| Expanded pre-combination secondary-source workbook | `outputs/01a10826-579d-78f1-b00a-f33d738ff767/Maharashtra_Work_Tenders_2026_Expanded.xlsx` | `0BE6CEA0E31C0F13DBDB2CD12276F32BE94722C21E812FA9DB4DE4CFC5FC1C74` |
| 9 October `NEW ↓` URL manifest | `mahatenders-extract/artifacts/2026-10-09-after-new-links.jsonl` | `24F2CB96293FDD29D403282CAFD747FFA8B0C356258C3B48D4D77B6830DFAD76` |
| 10 October Civil Works 107-URL manifest | `mahatenders-extract/artifacts/2026-10-10-civil-manifest.jsonl` | `A402ABA66758AD149734F03084868C21288C60CE6569A9D4265D58B652878725` |
| 10 October Civil Works capture, batch 1 | `mahatenders-extract/artifacts/2026-10-10-civil-capture.jsonl` | `F58373A61A6B2FF8E6352C0BCDE8FCE9A464B361DD0E9A55FD7A0B2B1431CFDB` |
| 10 October Civil Works capture, batches/pages 7–83 | `mahatenders-extract/artifacts/2026-10-10-civil-capture-pages-7-83.jsonl` | `19FA45F540E06AB0BD9735165E044E4B8B228D6BF3558AD1E21415C3AF00C37B` |

Supporting extraction and validation code is in `mahatenders-extract/scripts/` and `artifact_build/`. The reusable extraction process is documented in `mahatenders-extract/GUIDE.md` and `mahatenders-extract/SKILL.md`.

## Re-running the saved checks from the original workspace

The following commands were run from the original parent workspace, where the extraction scripts and raw evidence files were stored. Those inputs are intentionally not included in a fresh clone, so these commands are historical references rather than a clone-ready audit workflow. Run them only when the corresponding local source files are available:

```powershell
python mahatenders-extract/scripts/validate_capture.py --manifest mahatenders-extract/artifacts/2026-10-10-civil-manifest.jsonl --capture mahatenders-extract/artifacts/2026-10-10-civil-capture.jsonl
python mahatenders-extract/scripts/verify_civil_workbook.py
python mahatenders-extract/scripts/verify_civil_remaining.py
python artifact_build/verify_external_merge.py
```

The 1,241-row raw capture is cross-checked against the final workbook by `verify_civil_remaining.py`; the 169 external rows are independently reconciled against the combined source workbook and pre-merge backup by `verify_external_merge.py`.

## Audit update rule

For each later scrape, append a dated manifest and raw capture, record the operator/browser conditions and the exact publication-date rule, preserve source strings and URLs, run the capture validator, deduplicate by stable Tender ID or source-specific ID, record every excluded/overlap decision, update the workbook fingerprints and rerun the merge checks. Do not overwrite this report's current snapshot counts; add a dated update or replace the report only after preserving the previous version in Git history.
