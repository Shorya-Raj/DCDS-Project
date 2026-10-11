# Data sources and handling

## What is in the repository

| Source | Location | What it contains | What it does not prove |
|---|---|---|---|
| Tender247 sample snapshot | `data/sample_tenders.json` | 129 civil, road and infrastructure category listings; source-reported title, category, location, closing date, estimate and EMD where present | Official notice details, complete eligibility, corrigenda, bids, awards or actual spending |
| MahaTenders reviewed workbook | Kept outside Git | Official Tender Log rows with source-specific review fields and exact detail URLs where captured | A live/current portal status; a completed import into the project databases |
| External-source audit workbook and capture files | Kept outside Git | Historical source captures, manifests, raw source text and merge evidence | Files available to someone who only clones this repository |

The bundled JSON was supplied as a sample snapshot. Its original collection timestamp is not available in the file, so the repository does not assign it a new collection date. The app labels its source URLs as Tender247 category listings.

## Official workbook import rule

The workbook loader reads the `Tender Log` sheet, uses the official `Tender ID` as its stable key, and accepts rows marked `Include? = Yes` only when the detail capture, exact official detail URL and required fields are present. Rows marked `No` are excluded from the import plan. Included rows without evidence are reported as held for review. It does not delete workbook rows.

The 11 October 2026 audit records a dry run of the reviewed copy: 1,572 rows ready, 2 included rows held, and 45 third-party rows excluded. The dry run opened no database connection. Those counts describe that saved workbook snapshot and should be refreshed before a later full import.

## Keep the source trail intact

- Keep raw workbooks, capture JSONL files, browser screenshots and any session-bearing portal URL outside Git.
- Do not reconstruct an official detail URL from a Tender ID or screenshot.
- Keep source-reported text and blank values; record corrections with their evidence instead of silently replacing values.
- Use Tender ID as the official record key. Similar titles, organisation names or reference numbers are review signals, not proof that rows are duplicates.
- Keep Tender247 IDs namespaced (`tender247:<id>`). Do not merge a third-party lead into an official row without a documented official-source match.
- Treat portal status as a dated snapshot. Check the live notice before relying on a deadline or status.
- If data is refreshed, record the source, collection date/time, inclusion rule, input fingerprint, import result and unresolved rows in the work log.

## Reproducing the recorded counts

The workbooks and raw captures used in the audit are intentionally not included here. Some official URLs carry browser-session parameters. The audit includes snapshot counts, decisions and file fingerprints, but a fingerprint alone cannot reproduce or recover a source file. A fresh clone can run the bundled sample; it cannot recreate the external workbook audit without the locally retained evidence files.
