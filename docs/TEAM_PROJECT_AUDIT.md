# Team Project Audit Book

**Project:** Maharashtra Works Tender Explorer (working title)  
**Updated:** 12 October 2026  
**Purpose:** Give every team member a plain-language record of what the team built, what was checked, and what still needs to be prepared.

## How to use this book

Use the original numbered sequence below when giving project updates. Steps 1–7 have been completed and rechecked where indicated. Step 8 is in progress; a report draft is prepared for review. The detailed chronological record is in [`WORK_LOG.md`](WORK_LOG.md); this book is the quick team briefing.

The words **done**, **pending**, and **needs team confirmation** mean different things. A dry run checks the import plan without writing to a database. A live import writes records. A screenshot or sample-mode run does not prove that database mode works. Each status below says what evidence exists.

## Project in one minute

The project is a Python and Streamlit dashboard for browsing Maharashtra civil, road, and infrastructure tender listings. It has an offline sample mode and a database mode.

- **MySQL** holds information that is useful for searching, filtering, joining, and counting, such as source ID, title, category, location, dates, estimated value, EMD, and source URL.
- **MongoDB** holds the matching tender document, including flexible details such as department, work description, eligibility, documents, and the saved source row.
- Both databases use one shared key, so a tender selected from MySQL can retrieve its detail document from MongoDB.

This dataset contains published estimates, not awarded contract values or money paid. The dashboard must not describe estimated tender value as actual spending.

## Original numbered work sequence

| Step | Work | Status | What the evidence says |
|---:|---|---|---|
| 1 | Check setup and choose how to run the databases. | **Done; services restored.** | The earlier log records a successful portable setup, but its configured data root and server processes were absent during the latest check. MySQL 8.4.9 and MongoDB 7.0.28 were restored under `%LOCALAPPDATA%\DCDS`, with both ports bound to `127.0.0.1`. Run `scripts/start_local_databases.ps1` after a reboot. The one-time installer is `scripts/install_local_databases.ps1`; it refuses to initialize non-empty data folders. |
| 2 | Confirm the database design and record identity. | **Done** | Importer, schema, dashboard, and checker use the same source-prefixed key. MySQL constraints and MongoDB validation were applied by the pilot import. See [`ARCHITECTURE.md`](ARCHITECTURE.md). |
| 3 | Prepare and check the import source. | **Done for this workbook snapshot** | The fresh plan found 1,572 accepted records, held Tender Log rows 9–10, and excluded 45 rows marked `Include? = No`. A deterministic 25-record plan was checked without opening a database connection. |
| 4 | Load and reconcile the 25-record pilot. | **Done** | The same 25 records were imported twice. After each pass, both stores contained 25 records and the consistency check passed. The exact IDs are in [`IMPORT_PILOT_IDS_2026-10-12.csv`](IMPORT_PILOT_IDS_2026-10-12.csv). |
| 5 | Load accepted workbook rows. | **Done and reconciled again.** | Re-imported 1,572 ready rows from the reviewed workbook. MySQL has 1,572 tenders, MongoDB has 1,572 detail documents, and all IDs and shared fields match the source plan. Two included rows remain held for missing evidence; 45 excluded rows remain out of the import. |
| 6 | Demonstrate SQL/MongoDB database work. | **Done** | All three SQL examples ran on the imported data. MongoDB read and aggregation ran on project records; create/read/update/delete were demonstrated with a temporary document that was removed. |
| 7 | Connect and check the dashboard in database mode. | **Verified with the restored databases.** | The dashboard query path returned all 1,572 MySQL rows; a MongoDB detail lookup found the document with the same tender key. Streamlit health returned HTTP 200 and the app is open at `http://127.0.0.1:8501/`. The app now opens in MySQL + MongoDB mode; Sample data remains selectable. Capture refreshed screenshots before hand-in. |
| 8 | Finish hand-in and demo materials. | **In progress; report draft prepared.** | The report draft is `reports/Maharashtra_Works_Tender_Explorer_Report_2026-10-12.docx`. It contains two safe dashboard screenshots; all six pages were rendered and visually reviewed on 12 October, with no clipping or overlap found. Sanitized SQL/MongoDB outputs are saved, but screenshots of those outputs, refreshed dashboard screenshots, rehearsal, contribution record and instructor/team confirmations remain. |

## Current data snapshot

The source is the reviewed workbook at `outputs/01a10826-579d-78f1-b00a-f33d738ff767/01_CURRENT_Maharashtra_Works_TenderBook_Reviewed_2026-10-11.xlsx`. It is kept outside the code repository because source URLs can contain browser-session values. Its SHA-256 fingerprint at the import checkpoint was `FAA13CA941E03F94621D1D27B85E9911036CBB6D9A20C00AE89885B0DDEF593A`.

| Count | Meaning |
|---:|---|
| 1,619 | Unique records in the reviewed Tender Log, including separate third-party source rows |
| 1,574 | Official records marked included in the workbook |
| 1,572 | Official records ready and loaded into both databases |
| 2 | Included rows still held because exact detail-page evidence is missing (Tender Log rows 9 and 10) |
| 45 | Third-party rows marked `Include? = No`; they were not loaded in the first official import |
| 240 | Loaded records with no reported estimated value; the database keeps these values as `NULL` |
| 108 | Undated Tender247 leads kept as leads; they were not promoted into the dated official set |

The counts describe the saved workbook, not a complete archive of every tender published in 2026. Refresh the workbook plan before any later import if that file changes.

One source-review flag remains: record #1356 (`2026_NMC_1342575_11`) has a captured title mentioning Satpur/P.No.09 while its location and work description mention Nashik East/P.No.14. The title was kept as captured; the discrepancy needs checking against the official notice document. It was not resolved by the database import.

## How the shared key works

The source's original ID is kept in `source_record_id`. The databases use a prefixed key so two different websites cannot accidentally claim the same ID:

| Source | Original ID | Shared database key |
|---|---|---|
| MahaTenders | `2026_NMC_1342575_23` | `mahatenders:2026_NMC_1342575_23` |
| Tender247 | `104833153` | `tender247:104833153` |

In MySQL the shared key is `tender_key`. In MongoDB the same string is the document's `_id`. The checker also rebuilds the key from `source_type` and `source_record_id` to ensure the parts agree.

## What each database stores

### MySQL

There are three tables:

- `tenders` stores the shared listing fields and references one category and one location.
- `categories` stores one row for each category name.
- `locations` stores one row for each location name.

The category and location references are foreign keys. Estimated value and EMD use decimal columns, so the values stay exact to cents. Missing values stay `NULL`, not zero.

### MongoDB

The `tender_details` collection stores one document per tender key. A document repeats the fields needed to identify and check the listing and adds source-specific detail fields. The collection validator checks required common fields and types; a unique index prevents the same source ID and source type from appearing twice.

MySQL's category/location lookup names compare without regard to capitalization. MongoDB keeps the spelling from the source record. The consistency checker treats capitalization differences in those labels as equivalent while comparing the rest of the shared values.

## Demonstration results already recorded

- Category join and grouping: **8 category groups**.
- Above-average estimated-value subquery: **75 tenders**.
- `HAVING COUNT(*) >= 3`: **113 source-reported location labels**. Some entries such as `Work` and `EE/EAST/MSIB` may not be standardized geographic locations, so interpret this result as a label count until the source values are reviewed.
- MongoDB category aggregation: **8 groups**.
- MongoDB temporary CRUD example: the document was created, read, updated, deleted, and then confirmed absent. No accepted tender was deleted or modified for this example.
- The missing estimate count remained **240** after import.

The saved database-mode screenshots are `docs/evidence/database_dashboard_overview.jpg` and `docs/evidence/database_dashboard_mongo_detail.jpg`. They show valid database results and MongoDB-backed scope/eligibility, but were captured before the 12 October UI refinements; refresh both screenshots before using them as final UI evidence. The current dashboard sanitizes the source link and keeps the category-count axis at zero. Sanitized SQL and MongoDB example results are saved in `docs/evidence/database_demo_outputs_2026-10-12.md` and `.html`; screenshots of those query outputs are still pending. The exact run and verification details are in [`WORK_LOG.md`](WORK_LOG.md).

## Rubric checklist for Step 8

The saved DCDS Lab ESE rubric, reviewed locally on 12 October, lists the miniproject as **10 marks** and **40%** of the lab evaluation, mapped to CO1–CO5. The course PDF is not included in this repository. The date is marked tentative (26–30 October 2026), so confirm it and the required report format with the instructor.

| Criterion | Marks | Evidence to prepare |
|---|---:|---|
| Application design and functionality | 2 | Show the main dashboard flow, filters, summaries, table, and tender details. |
| Python programming implementation | 2 | Explain the importer, normalization, database access, and app modules. |
| SQL and NoSQL integration | 2 | Show MySQL fields linked to the matching MongoDB document through the shared key. |
| Advanced queries and data retrieval | 2 | Demonstrate SQL joins/subqueries/grouping and MongoDB aggregation. |
| Code quality, documentation, output and UI | 1 | Present readable modules, project documentation, and clear output. |
| Testing, validation, security and error handling | 1 | Show source-plan reconciliation, validation, missing/held values, local-only DB ports, ignored `.env`, and error handling. The current unit-test suite was rerun on 12 October: all 7 tests passed. |

## Reproducing the local checks

The commands below are run from `DCDS-Project`. They assume the local Python environment, database binaries, and ignored `.env` file have already been set up on that computer. The `.env` contains passwords and must not be shared or committed. Other team computers need their own database setup and credentials; `127.0.0.1` means the same computer, not a shared team server.

If the pinned server files are missing and both data folders are empty, restore them once:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install_local_databases.ps1
```

The installer downloads the project-pinned portable versions from the official vendors, stores binaries/configuration/data/logs under `%LOCALAPPDATA%\DCDS`, and binds the database ports to this computer only. It stops rather than initializing a non-empty database folder. After setup, or after a reboot, start/check the services with:

```powershell
powershell -File scripts/start_local_databases.ps1
```

For a future source refresh, first run the deterministic 25-record pilot and check it twice before loading the accepted workbook set:

```powershell
python -m tender_explorer.load_data --input "../outputs/01a10826-579d-78f1-b00a-f33d738ff767/01_CURRENT_Maharashtra_Works_TenderBook_Reviewed_2026-10-11.xlsx" --sample-size 25
python -m tender_explorer.check_data
```

Repeat those two commands once. Only after both checks pass should the accepted set be loaded:

```powershell
python -m tender_explorer.load_data --input "../outputs/01a10826-579d-78f1-b00a-f33d738ff767/01_CURRENT_Maharashtra_Works_TenderBook_Reviewed_2026-10-11.xlsx"
```

Check the imported records against the saved workbook plan:

```powershell
python -m tender_explorer.check_data --expected-input "../outputs/01a10826-579d-78f1-b00a-f33d738ff767/01_CURRENT_Maharashtra_Works_TenderBook_Reviewed_2026-10-11.xlsx"
```

Run the dashboard:

```powershell
python -m streamlit run app.py
```

Choose **MySQL + MongoDB** in the sidebar to use the imported records. Choose **Sample data** for the 129-record offline Tender247 example. Sample records are third-party category listings, not official tender detail pages.

If the source workbook is updated, first run an offline plan with `--dry-run`. Do not load it until the team has reviewed the counts and held rows. The loader uses repeat-safe upserts, but the team still needs to run the reconciliation afterward.

## Remaining team work

1. Confirm the registered title and whether the saved rubric is current; its date (26–30 October 2026) is marked tentative. Ask for the final schedule and report/submission format, which are not specified in the saved rubric ([GitHub issue #2](https://github.com/Shorya-Raj/DCDS-Project/issues/2)).
2. Assign names to the work areas in [`PROJECT_PLAN.md`](PROJECT_PLAN.md); no team member names have been recorded in the project plan yet.
3. Map and review the 127 newly captured official Works detail pages before any import. They are not yet included in the reviewed workbook or databases ([GitHub issue #8](https://github.com/Shorya-Raj/DCDS-Project/issues/8)). Reconcile the historical 129-link manifest and review the two held rows ([issue #4](https://github.com/Shorya-Raj/DCDS-Project/issues/4)); do not recreate official detail URLs from IDs or screenshots.
4. Review record #1356 against its official notice document and record the evidence before changing any source value ([GitHub issue #4](https://github.com/Shorya-Raj/DCDS-Project/issues/4)).
5. Review the report content and confirm the instructor’s format before finalizing `reports/Maharashtra_Works_Tender_Explorer_Report_2026-10-12.docx`; it is a review draft, and all six pages have passed visual layout review. Refresh the dashboard screenshots after the final interface refinement, add screenshots of SQL/MongoDB output examples and rehearse the demo ([GitHub issue #5](https://github.com/Shorya-Raj/DCDS-Project/issues/5)). The existing dashboard images and sanitized text/HTML outputs are saved under `docs/evidence/`.
6. Make sure every team member can explain the shared key, why SQL and MongoDB are both used in this design, the missing-value rule, and the fact that tender estimates are not actual spending.
7. Broaden the official dataset beyond Works only after the user completes the visible MahaTenders CAPTCHA and clicks Search. The 12 October Electrical Goods/Equipment query plan has no captured results yet ([GitHub issue #9](https://github.com/Shorya-Raj/DCDS-Project/issues/9)).

## Project records

- [`PROJECT_PLAN.md`](PROJECT_PLAN.md) — canonical numbered sequence and status.
- [`WORK_LOG.md`](WORK_LOG.md) — dated setup, import, query and dashboard evidence.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — current schema, relationships and record identity.
- [`DATA_SOURCES.md`](DATA_SOURCES.md) — source rules and safe handling.
- [`WEB_SCRAPING_AUDIT.md`](WEB_SCRAPING_AUDIT.md) — collection history, source limitations and dated import checkpoints.
- [`IMPORT_PILOT_IDS_2026-10-12.csv`](IMPORT_PILOT_IDS_2026-10-12.csv) — exact records used in the repeat-import pilot.
- [`evidence/database_demo_outputs_2026-10-12.md`](evidence/database_demo_outputs_2026-10-12.md) — sanitized SQL and MongoDB output notes.
- [`../reports/Maharashtra_Works_Tender_Explorer_Report_2026-10-12.docx`](../reports/Maharashtra_Works_Tender_Explorer_Report_2026-10-12.docx) — editable project report draft.
- [`README.md`](../README.md) — install/run instructions for the code.
