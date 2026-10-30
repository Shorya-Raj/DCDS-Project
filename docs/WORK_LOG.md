# DCDS Project Work Log

This is the chronological record of implementation and verification work. The [tender-data audit](WEB_SCRAPING_AUDIT.md) holds the source history, workbook counts, provenance decisions and collection limits. Add an entry as each project action is completed.

## 30 October 2026 — Tender extraction code prepared for GitHub

- Added the reusable `skills/mahatenders-extract/` source, a plain-language guide, and a README section. The visible-browser script takes a Word hyperlink manifest, saves raw detail-page fields in small resumable JSONL batches, and stops on a CAPTCHA. It does not write to the workbook or databases.
- Offline checks covered marker-based link selection, duplicate Word hyperlinks, exact-link retry, CAPTCHA stopping, and resume behavior. The source document produced 336 link occurrences and 319 distinct URLs after `NEW`; this regenerates the historical manifest without publishing those session-bearing URLs. The existing 129-row raw capture passed validation as 127 detail pages, two unavailable links and no pending link unattempted.
- This code publication is not a new live scrape. The standalone Playwright runner has not yet been tested against the live portal. The dated source and import statuses above remain unchanged.

## 12 October 2026 — Database restore, full import and app opened

### What changed

- The user pointed out that MySQL and MongoDB had worked earlier. The earlier 12 October entries do record that success. A later startup attempt then reported that the configured `%LOCALAPPDATA%\DCDS` installation was missing; a current check found that target root absent. No existing data files were present in the new MySQL or MongoDB data directories when they were created, so the setup rebuilt fresh local server/data folders rather than replacing files found there.
- Restored portable MySQL 8.4.9 and MongoDB 7.0.28 from their official vendor ZIP download hosts. Added `scripts/install_local_databases.ps1` for first-time recovery; it refuses to initialize non-empty MySQL or MongoDB data directories. Both servers use loopback-only bindings and remain user-run processes, not Windows services. `scripts/start_local_databases.ps1` remains the reboot/start command.
- Re-imported the accepted rows from the reviewed workbook. The loader reported 1,572 ready, held Tender Log rows 9–10 for missing page evidence, and excluded 45 `Include? = No` rows. No workbook rows were changed.
- Changed the Streamlit source selector's initial choice to **MySQL + MongoDB** so the populated course database opens by default; **Sample data** remains available as the offline fallback.

### Verification

- The project Python environment connected to both local databases.
- `check_data.py --expected-input` reported 1,572 MySQL tenders, 1,572 MongoDB documents and 1,572 source-plan records; the keys and shared fields matched.
- The same MySQL listing read used by the dashboard returned 1,572 rows. A MongoDB detail lookup found the matching document for the first listing's shared key.
- Streamlit is running at `http://127.0.0.1:8501/`; its health endpoint returned HTTP 200. The request to open that URL in the Codex browser panel was queued. The current rendered page has not yet been captured as new report evidence.
- The installer script passed a PowerShell syntax parse. No unit-test suite was run during this recovery.

### Audit correction and next step

- The earlier “Local database startup failure” entry remains as a record of what was observed at that point. The earlier “Local MySQL and MongoDB setup” entry remains historical evidence. This entry records the later missing-root finding and the recovery, so neither past success nor current recovery is presented as the other.
- Step 1, Step 5 and Step 7 are now updated in `PROJECT_PLAN.md` and `TEAM_PROJECT_AUDIT.md`. Step 8 remains in progress: confirm the live page visually, capture refreshed database-mode screenshots and SQL/MongoDB output screenshots, rehearse the demo, and record team/instructor confirmations and member contributions.

## 12 October 2026 — Diversification scrape queued

- Prepared the official MahaTenders advanced-search form for `Electrical Goods/Equipment`, Published Date 01/01/2026 through 12/10/2026, with Tender Category unrestricted so the portal's classification can be captured as shown.
- The portal displays a CAPTCHA before it will search. Following `mahatenders-extract`, no CAPTCHA was solved or bypassed and no search results were captured. The search plan at `mahatenders-extract/artifacts/2026-10-12-diversification-search-plan.csv` records the first category and remaining queue.
- Next required action: the user completes the visible CAPTCHA and clicks Search; then official result/detail links can be captured and validated. The prior 127 page captures remain pending mapping/import.

## 12 October 2026 — Pending official Works links

- Used the `mahatenders-extract` skill on the 129 distinct links in the supplied DOCX that lacked an exact URL match in the reviewed book. Saved the ordered raw page capture and link-by-link reconciliation in `mahatenders-extract/artifacts/`.
- Captured 127 official 2026 Works detail pages with distinct Tender IDs absent from the current workbook. Two links were result pagination, not tenders. The capture validator found no errors and no pending link left unattempted.
- Kept the reviewed workbook and the 1,572-record MySQL/MongoDB accepted import unchanged. The 127 captures are ready for workbook field mapping and source review before a versioned import. Full provenance and counts are in the tender-data audit above.

## 12 October 2026 — Step 8 report draft

### Draft prepared

- Created `reports/Maharashtra_Works_Tender_Explorer_Report_2026-10-12.docx` as an editable review draft using the project implementation records, verified database results, saved course PDFs and current reviewed workbook snapshot.
- Covered the project purpose, source scope, system requirements, MySQL/MongoDB design, shared record key, implementation, demonstration query results, testing evidence, limitations and references. Embedded the two safe database-mode dashboard screenshots. No portal session URL or credentials were added.
- Kept the document explicitly at draft/review status. The course outcome PDF lists CO1–CO4 while the lab rubric maps the miniproject to CO1–CO5; the instructor must confirm the intended CO5 wording. The saved rubric does not specify a report template or confirmed submission format, and team member names were not invented.

### File check and remaining review

- The bundled Python `python-docx` reader reopened the saved file successfully: 68 paragraphs, 6 tables and 2 embedded images. Checked the extracted text for the reported metrics and for token-like source URL content; the expected metrics were present and no `sessionToken` or `token=` text was found.
- Rendered the DOCX to a six-page PDF and PNGs with the provided renderer after LibreOffice was installed. Visually inspected every page: tables, code and both screenshots fit; no clipping or overlap was found. No layout repair was needed.
- Step 8 remains in progress. Still required: instructor/team confirmation of report format, title, rubric/date and CO5 wording; SQL/MongoDB output screenshots; rehearsal; and team contribution names/summary.

## 12 October 2026 — Dashboard code review and UI refinement

### Findings and changes

- Compared `app.py` with the current MySQL/MongoDB model and assessment flow. The page printed each captured `source_url` in full even though official portal URLs can carry session values. The results table also expanded the page, while location filtering and ID lookup were not directly available.
- Replaced raw URL display with a host-checked source link. It uses HTTPS for MahaTenders/Tender247, removes query strings and fragments, and hides links for unrecognized hosts. The original URL remains stored in the local databases for provenance and is not printed by the UI.
- Added a source-reported location multiselect, search by tender/source ID, a manual refresh for the 60-second data cache, fixed-height results table, and cached MongoDB detail reads. Database errors now show actionable guidance and the exception type without rendering raw connection text.
- Reopened the existing Streamlit tab after the app server was restarted. Sample mode displayed 129 records. Database mode displayed 1,572 records, INR 2,886.86 crore in reported estimates and coverage of 1,332 / 1,572; the selected MahaTenders record returned MongoDB details, and its rendered source link omitted the session query. No tender data or schemas were changed.

### Review status and follow-up

- These were UI-only changes and no automated tests were added or run. The live browser review confirmed both modes load and the current database detail/link behavior renders as intended.
- The overview/detail screenshots in `docs/evidence/` and the two report images predate this refinement. Capture updated dashboard evidence before finalizing the report/demo. Query-output screenshots, rehearsal and team/instructor confirmations remain pending under Step 8.
- The localhost Streamlit app is running on `127.0.0.1:8501` for the team to review. It can be stopped with Ctrl+C in its server terminal.

## 12 October 2026 — Category chart zero baseline

### Change

- Replaced Streamlit's automatic category bar-chart scale with an Altair chart whose count scale has an explicit minimum of zero. This prevents the nonnegative listing counts from showing negative tick marks like those in the earlier dashboard screenshot.
- Kept category labels sorted by count, added readable integer tick labels and hover details, and made chart height adjust to the number of visible categories.
- Updated the README, numbered plan and team audit book to describe the zero baseline.

### Browser review

- Reloaded the running dashboard in sample mode: the category axis ran from 0 to 45 and the chart rendered with all three categories.
- Switched to MySQL + MongoDB mode: the dashboard still showed 1,572 matches, ₹2,886.86 Cr in reported estimates and coverage of 1,332 / 1,572. The category axis ran from 0 to 1,344 across all eight categories, with no negative tick marks.
- The first refresh exposed an Altair 6 data-shape requirement; the chart input was corrected and the final sample/database views rendered successfully.
- This was a manual browser review; no automated test suite was run. The saved dashboard screenshots and report images still predate the current UI and should be recaptured during Step 8.

## 12 October 2026 — Local database startup failure

### What was observed

- The user ran `scripts/start_local_databases.ps1`; it stopped before starting MySQL and reported that the MySQL installation was missing under `%LOCALAPPDATA%\DCDS`.
- Confirmed that this configured folder is absent. `C:\Program Files\MySQL` contains MySQL Shell 9.7 only, not MySQL Server; no MongoDB server folder was found. The dashboard screenshot shows a MySQL `InterfaceError` while loading database mode.
- Confirmed that the reviewed workbook at `outputs/01a10826-579d-78f1-b00a-f33d738ff767/01_CURRENT_Maharashtra_Works_TenderBook_Reviewed_2026-10-11.xlsx` is still present.

### Current status and next action

- The previous 1,572-record import and reconciliation remain valid historical evidence, but current database files and service availability cannot be confirmed from the absent configured root. No server reinstall or reimport has been performed in this check.
- Do not treat the startup script as an installer: it only starts the portable server files when they already exist. Restore MySQL 8.4.9 and MongoDB 7.0.28 under the expected local root, initialize/configure the services, then import the reviewed workbook and rerun `check_data.py --expected-input` before presenting database mode.
- Updated Steps 1, 5 and 7 in the numbered project plan and team audit to distinguish past verification from current availability. Sample mode remains available without the database services.

## 12 October 2026 — Local MySQL and MongoDB setup

### Work completed

- Repaired the existing `%USERPROFILE%\.venvs\dcds-project` launcher with the installed Python 3.12.10 and installed its missing `openpyxl` dependency from `requirements.txt`.
- Downloaded official vendor ZIP archives and set up user-run MySQL 8.4.9 and MongoDB 7.0.28 under `%LOCALAPPDATA%\DCDS`. A user-scoped MongoDB MSI was unavailable, and this session had no administrator rights for Windows service installation.
- Initialized MySQL with a generated root password, created the `dcds_tenders` database and a limited `dcds` account, and saved generated credentials in the Git-ignored project `.env`. Temporary setup files containing the initial root secret were removed after configuration.
- Bound both databases to `127.0.0.1`, disabled MySQL's unused X Protocol listener, and saved local startup configuration. Added `scripts/start_local_databases.ps1` for starting the portable servers after a reboot.
- Removed the downloaded ZIP archives after extracting and verifying the running server binaries; the data directories and logs remain under `%LOCALAPPDATA%\DCDS`.

### Verification and next boundary

- The project's `mysql_connection()` connected as `dcds@localhost` to MySQL 8.4.9 and the `dcds_tenders` database. Its `mongo_collection()` pinged MongoDB 7.0.28.
- Listener inspection showed MySQL only on `127.0.0.1:3306` and MongoDB only on `127.0.0.1:27017`; there was no MySQL X Protocol listener on port 33060.
- The startup script reported both listeners and successfully restarted the empty MongoDB instance after a graceful shutdown.
- The MySQL project database had zero tables and the MongoDB project database had no collections. No tender import, schema creation, query demonstration or database-mode dashboard run was performed in this setup stage.

## 12 October 2026 — Database contract and 25-record pilot

### Design and implementation

- Standardized identity across the mapper, MySQL, MongoDB, checker and dashboard. The source's original identifier is kept in `source_record_id`; the shared key is `mahatenders:<Tender ID>` for official records and `tender247:<listing-id>` for Tender247 records.
- Updated the MySQL schema with source ID/type and publication date, source-ID uniqueness, category/location foreign keys, and exact decimal money columns. Added MongoDB JSON Schema validation plus a unique source-type/source-ID index.
- Expanded `check_data.py` to compare record counts and key sets, verify each key against its source type and ID, and compare shared values including dates and exact decimal amounts. Category/location labels are compared without regard to capitalization because the MySQL lookup names use a case-insensitive collation; MongoDB and its raw source row retain the source spelling.
- Updated the dashboard to show original source IDs and avoid converting decimal money to floating point for its table display. The importer refuses to load into an older incompatible MySQL table until it is explicitly backed up and migrated.

### Source preparation and pilot result

- Re-ran the current workbook plan from `outputs/01a10826-579d-78f1-b00a-f33d738ff767/01_CURRENT_Maharashtra_Works_TenderBook_Reviewed_2026-10-11.xlsx`. It reported 1,572 ready, Tender Log rows 9 and 10 held, and 45 `Include? = No` rows excluded. The deterministic 25-record sample was rechecked without a database connection.
- Confirmed MySQL 8.4.9 and MongoDB 7.0.28 were reachable from the project's Python environment; both project databases were empty before the pilot.
- Imported the same 25 official records twice. After the first import, the initial strict text comparison found one capitalization-only location difference (`AHILYANAGAR` versus `Ahilyanagar`). The comparison was aligned with MySQL's case-insensitive lookup semantics while leaving the source spelling intact in MongoDB. Reconciliation then passed after the first import and again after the repeat import.
- Each final reconciliation reported 25 MySQL records, 25 MongoDB documents, matching keys, valid source-derived identities, and no shared-field mismatches. The repeat pass did not add duplicates.
- Saved the exact deterministic sample IDs in `IMPORT_PILOT_IDS_2026-10-12.csv`. The workbook SHA-256 at this checkpoint was `FAA13CA941E03F94621D1D27B85E9911036CBB6D9A20C00AE89885B0DDEF593A`.
- A syntax-only check passed for all 8 Python files. The unit-test suite was not rerun for this checkpoint.

### Remaining boundary

- At the end of the pilot checkpoint, no full workbook import, SQL/MongoDB query demonstration, CRUD/aggregation demonstration or database-mode dashboard check had been performed.
- Continue to hold rows 9 and 10. Record #1356's title/location discrepancy remains a source-review flag; this pilot did not resolve it.

## 12 October 2026 — Accepted workbook import (Step 5)

- Loaded the 1,572 records accepted by the current reviewed-workbook import plan. The two included rows without sufficient page evidence remained held; the 45 rows marked `Include? = No` remained excluded.
- Ran `python -m tender_explorer.check_data --expected-input <reviewed-workbook-path>`. It reported 1,572 MySQL records, 1,572 MongoDB documents, and 1,572 expected source records. Both stores matched each other and the source plan; keys, source identities, dates, amounts and shared fields agreed.
- The pilot sample is included in the full accepted set. The deterministic 25-ID record remains available for the earlier repeat-import evidence.
- No SQL/MongoDB query or CRUD/aggregation demonstration and no database-mode dashboard check have been performed yet.
- Next: Step 6, run the SQL examples and demonstrate MongoDB read, aggregation, update and delete behavior with a temporary document that is removed afterward.

## 12 October 2026 — SQL and MongoDB operations (Step 6)

- Ran all three statements in `sql/queries.sql` against the 1,572 accepted tenders: category join/grouping returned 8 groups, the above-average estimate subquery returned 75 tenders, and `HAVING COUNT(*) >= 3` returned 113 source-reported location labels. Some labels (for example `Work` and `EE/EAST/MSIB`) need review before being described as standardized geographic locations.
- Counted 240 accepted records with a missing estimated value. They remain `NULL`; no zero values were substituted.
- Read the imported tender `mahatenders:2026_NMC_1342575_23` from MongoDB and ran the project category aggregation, which returned 8 category groups.
- Demonstrated MongoDB create, read, update and delete using a temporary schema-valid document. The delete succeeded and a final lookup confirmed that the temporary document was absent. No imported tender document was changed or removed.
- Next: Step 7, verify the database-backed Streamlit view shows MySQL records and their matching MongoDB details.

## 12 October 2026 — Database-mode dashboard check (Step 7)

- Started the existing Streamlit app on loopback and selected **MySQL + MongoDB** mode in the browser.
- The page showed 1,572 matching tenders from MySQL. Selecting a tender displayed its original source ID, official source type, scope text and eligibility details retrieved from the matching MongoDB document.
- The 25-record pilot and the full accepted source set had already passed the cross-store checker. After the temporary CRUD demonstration was cleaned up, the final `check_data.py --expected-input <reviewed-workbook-path>` run again reported 1,572 records in each database, 1,572 source-plan records, and matching keys and shared fields.
- Stopped the temporary Streamlit server after the browser check. Sample mode remains the offline fallback.
- Step 7 is complete. Step 8 (final submission and demo materials) remains in progress.

## 12 October 2026 — Team audit book

- Created `TEAM_PROJECT_AUDIT.md` as a plain-language briefing for the project team. It summarizes the original numbered sequence, source counts and review flags, SQL/MongoDB design, import and demo evidence, reproduction commands, and remaining hand-in work.
- Linked the audit book from the README and context notes so another project chat can find the current status quickly.
- Step 8 remains in progress: final report, saved demonstration evidence, rubric/team confirmation, rehearsal, and contribution record are still outstanding.

## 12 October 2026 — Lab ESE rubric check (Step 8)

- Read and visually checked `course_materials/course_documents/DCDSL Evaluation Plan_with detailed rubrics.pdf`. The separately named `(1).pdf` copy is byte-identical; both have SHA-256 `ec95ce40c948c0fa8c2de352ef0502d77fac9c41038fcc3c5fa61cf66adfef3e`.
- The saved rubric lists the Python-based SQL/NoSQL miniproject as a 10-mark component worth 40%, covering CO1–CO5. Its ESE date is shown as tentative: 26–30 October 2026.
- The six criteria are application design/functionality (2 marks), Python implementation (2), SQL/NoSQL integration (2), advanced queries/data retrieval (2), code quality/documentation/output/UI (1), and testing/validation/security/error handling (1).
- Updated the numbered plan and team audit to use these exact criteria. The instructor still needs to confirm that this rubric/date remain current and provide any report template or submission-format requirements; the PDF does not specify them.

## 12 October 2026 — App/database recheck and demo evidence (Step 8)

### Work completed

- Reran `python -m unittest discover -s tests -v`: all 7 tests passed.
- Started the portable local MySQL and MongoDB services using `scripts/start_local_databases.ps1`. PowerShell required a process-scoped `-ExecutionPolicy Bypass` for this invocation; no saved execution-policy setting was changed. Both services accepted local connections at `127.0.0.1:3306` and `127.0.0.1:27017`.
- Reran `python -m tender_explorer.check_data --expected-input <reviewed-workbook-path>`. It reported 1,572 MySQL tenders, 1,572 MongoDB documents and 1,572 source-plan records, with matching keys and shared fields.
- Ran the dashboard using `python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true`, selected **MySQL + MongoDB**, and confirmed the page showed 1,572 matching tenders, ₹2,886.86 Cr in reported estimates and value coverage of 1,332/1,572. A selected listing displayed its MongoDB scope and eligibility details.
- Saved `docs/evidence/database_dashboard_overview.jpg` and `docs/evidence/database_dashboard_mongo_detail.jpg`. The overview shows the selected database mode and headline metrics. The detail screenshot omits the Source URL because the captured portal URL contains a session query value.
- Ran `scripts/capture_database_demo_evidence.py` against both databases. It recorded all three SQL examples, a MongoDB document read and category aggregation, and create/read/update/delete using a temporary document. The CRUD checks passed and final lookup confirmed the temporary record was absent. The script excludes source URLs and raw workbook rows from output.
- Saved the sanitized outputs in `docs/evidence/database_demo_outputs_2026-10-12.md` and `.html`. The outputs report SQL result sizes of 8 category groups, 75 above-average tenders and 113 source-reported location labels, plus 8 MongoDB category groups.

### Evidence boundary and next action

- The browser blocked opening the local HTML output for a screenshot and instructed not to use a local server or alternate route to render it. No workaround was attempted. The SQL/MongoDB query-output screenshots remain pending; the sanitized Markdown and HTML output files are available for the team to review.
- The temporary Streamlit process was stopped after the UI check. The two local database services remain running for the next project step.
- The app/database verification requested before report work is complete. The report draft and successful six-page visual review are recorded in the newer “Step 8 report draft” entry above. Step 8 remains in progress while the remaining team/demo materials are prepared.

## 12 October 2026 — Tender book naming, copies, and archive

### Review decisions

- Named `01_CURRENT_Maharashtra_Works_TenderBook_Reviewed_2026-10-11.xlsx` as the current work and import-mapping book. It retains 1,619 unique Tender IDs; 1,572 official rows are SQL-ready, 2 remain held for missing detail-page evidence, and 45 third-party rows are excluded from the first import.
- Kept the merged baseline, the expanded source book, and the combined 169-row source book because each supports comparison, source provenance, or the recorded merge.
- Retired the old separate Tender247-only workbook from the active file list. It has the same 127 listing IDs and the same titles, locations, tender categories, values, EMDs, countdowns, and URLs as the Expanded book's `Earlier Index Leads`; four raw source-category values differ. The earlier workbook is retained in `Archive/Superseded/` rather than discarded.
- Kept both 10 October workbook checkpoints and all prior inspection sidecars and the preview image in `Archive/`.

### File actions and verification

- Renamed the four active workbooks so their role and snapshot date are clear; created date-stamped, byte-identical backup copies of all four and verified their SHA-256 hashes.
- Moved the two historical checkpoints, the superseded separate-source snapshot, and inspection artifacts into labeled archive folders. No workbook contents or Tender Log rows were edited, deleted, or merged.
- Added `outputs/01a10826-579d-78f1-b00a-f33d738ff767/TENDER_BOOKS_INDEX.md` and updated the audit, extraction scripts, and workbook builders to use the new paths.
- `verify_external_merge.py`: 169 source rows, 45 added third-party details, 16 matches, 108 undated leads, 1,619 unique records, no errors.
- `verify_civil_workbook.py`: 107 captures compared, no errors. `verify_civil_remaining.py`: 1,236 compared, 5 overlaps, 1,574 official IDs, no errors.
- Node syntax checks passed for all updated workbook builders. No database import was run.

## 12 October 2026 — Repository foundation

### Work completed

- Prepared the existing application, SQL examples, sample data, audit and work log for the private GitHub repository.
- Added setup guidance, an architecture/ER diagram, source-handling notes, an assessment checklist and a team pull-request process.
- Updated local Compose settings to require passwords from an ignored `.env` file and bind database ports to loopback.
- Kept the reviewed workbooks and raw capture files outside the repository because official links may contain browser-session query values.
- Created the `project/repository-foundation` branch and opened PR #1 with the complete project tree.

### Verification status

- The GitHub repository was confirmed private, with `main` as its default branch and push access for the connected account.
- The local project directory did not contain Git metadata; the files were added to GitHub through the authenticated repository API.
- No database services, workbook import or tests were run as part of this documentation/repository setup.

## 11 October 2026 — Import preparation and environment check

### Starting record state

- The reviewed workbook contains 1,619 unique Tender IDs: 1,574 included official rows and 45 third-party rows excluded from the first import.
- The importer accepts 1,572 rows. Tender Log rows 9 and 10 remain held for missing detail-page evidence; record #1356 remains flagged for the Satpur/P.No.09 versus Nashik East/P.No.14 discrepancy.
- The reviewed workbook and the original merged workbook are retained; no rows were deleted or merged.

### Work completed

- Re-read the `Clarify task` chat and carried forward its next step: confirm the held-row state, prepare the 25-record database test, then reconcile before the full load.
- Rechecked rows 9–11 and record #1356 in the reviewed workbook. Row 11 has its official detail URL; rows 9–10 remain held.
- Added `--sample-size` to the loader. It selects the same evenly spread sample on every run, so the planned first batch can be imported twice to test idempotency.
- Added the canonical `categories` array to official MongoDB detail documents so the existing MongoDB category aggregation includes them. Optional opening and collection dates now serialize as ISO dates.
- Updated the README with the sample-import sequence and linked this log.

### Verification

- Python compilation succeeded for `normalize.py`, `load_data.py` and `test_normalize.py`.
- All 7 unit tests passed.
- Full workbook dry run: 1,572 ready, 2 held, 45 `Include? = No` excluded.
- 25-record sample dry run: 25 selected deterministically; no database connection was opened.
- Workbook data was not changed in this work session.

### Environment and remaining work

- The saved virtual-environment launcher points to the unavailable Windows Store Python. Its package directory contains Streamlit 1.65.0, MySQL Connector 9.7.0, PyMongo 4.18.2, `python-dotenv` 1.2.4 and `openpyxl` 3.1.5. With that directory on `PYTHONPATH`, the bundled Python 3.12.14 runtime can use those dependencies; the saved launcher itself remains broken.
- Docker and Podman commands are unavailable; WSL is not installed. MySQL port 3306 and MongoDB port 27017 refuse connections.
- A local Streamlit server started with the compatibility workaround. The browser rendered 129 sample listings; searching `Nashik` returned 2 rows with 2/2 reported values. Both the app health endpoint and root page returned HTTP 200. The server and test tab were closed.
- The programmatic Streamlit `AppTest` attempt did not finish within about 35 seconds and was stopped. The browser smoke test verified the sample-mode UI instead.
- No database import has been verified. The database sample, repeat pass, consistency check and full load remain pending.

Next: install a working CPython environment with `requirements.txt`; start MySQL 8 and MongoDB 7 (or Docker); configure local `.env`; run the 25-record import twice and `check_data` after each pass; then import all 1,572 accepted records and reconcile the final counts. Keep rows 9 and 10 held unless exact official evidence is captured, and resolve record #1356 from its notice document.

## 19 October 2026 — Query explorer and live database filters

- Moved the database-mode sidebar filters from Python over a previously loaded table into parameterized MySQL queries. The displayed SQL and bound values now match the actual tender result query; the selected listing's MongoDB find_one lookup is also shown.
- Added a Query explorer with editable read-only SQL SELECT searches, validated MongoDB JSON find filters, examples, result tables, and an in-app guide. SQL runs in a read-only transaction; both custom searches have a three-second time limit and show at most 100 rows. MongoDB result projection excludes raw source rows and captured source URLs.
- Added the user guide at docs/QUERY_EXPLORER_GUIDE.md and linked it from the README and dashboard sidebar.

### Verification

- Existing data-normalization tests and new query-safety tests: 13 passed.
- Six live filter cases returned exactly the same tender keys as the earlier Python-filter behavior, including all 1,572 records, the 1,344 Civil Works records, a 46-row Nashik search, and no-match cases.
- Live SQL examples returned the expected count and category grouping; live MongoDB searches returned one Tender ID match and a capped category result.
- In the browser, database mode showed 1,572 tenders, the Nashik filter showed 46, both custom search buttons returned rows, the guide displayed the MongoDB operators, and a DELETE statement was rejected without running.
- Sample mode still showed its 129 bundled listings and explained that its filtering runs in Python. Database mode was restored afterward.

## 20 October 2026 — Interface redesign

- Reorganised the long dashboard into Tenders, Overview, and Query studio workspaces. Search is central; a record inspector sits beside the results on wide screens and below them on narrow screens.
- Added a local architectural header, summary-card styling, clearer section hierarchy, and a supported Streamlit theme. Following user feedback, replaced white surfaces with muted sage and warm-grey tones.
- Kept existing database/filter/search behavior, source provenance, sample-mode warning, and source-link sanitization. Updated the README and query guide for the new navigation.
- All 13 existing tests passed. AppTest verified database record count (1,572), listing selection, Nashik filtering (46), SQL results (20), capped MongoDB results (100), empty filters, and sample mode (129). Browser checks covered tabs, guide, desktop, and narrow-screen layout.
- Design rationale and research links: docs/INTERFACE_DESIGN.md. Local changes only; no GitHub publishing was performed in this redesign.

## 20 October 2026 — Database recovery and workbook re-import check

- Restarted the local MySQL and MongoDB services after the dashboard could not connect, then re-imported the reviewed workbook into the project databases.
- The importer loaded 1,572 ready records, left two rows held for missing evidence, and skipped 45 rows marked `Include? = No`.
- `tender_explorer.check_data --expected-input <reviewed-workbook-path>` confirmed 1,572 MySQL records and 1,572 MongoDB documents, with matching keys and shared fields against the workbook.
- This records the verified local database state. The reviewed workbook, database files, logs, and `.env` credentials remain outside the repository.

## 24 October 2026 — Works Atlas interface update

- Reworked the dashboard presentation around the Works Atlas direction: charcoal, ivory, and amber colors, original bridge linework, expandable filters, card and table browsing, six-record pages, and presentation sorting.
- Kept the existing data paths and project limits: MySQL filtering remains parameterized, MongoDB details use the shared tender key, custom searches stay bounded, and source links remain sanitized.
- Updated the README, project plan, team audit, and interface notes, and added the UI verification script. The interface notes include a flowchart showing the sample and database paths.
- Recorded verification from the implementation work: all 13 existing normalization/query-safety tests passed; Streamlit AppTest covered the 1,572-record database view, cards/table, selection, pagination, search/filter/sort cases, SQL and MongoDB searches, sample mode (129), and return to database mode. The health endpoint returned ok.
- A screenshot-based visual review of this redesign has not been completed. Refresh the dashboard evidence and inspect desktop and narrow-screen layouts before hand-in. The AppTest results are functional checks, not visual proof.
- No workbook import was run for this interface update. The reviewed workbook, local database files, logs, and credentials remain outside the repository.
