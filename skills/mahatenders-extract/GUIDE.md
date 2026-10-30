# Collecting MahaTenders detail pages

This folder contains the source code behind the project's official tender-detail collection method. It is written for a teammate to run and inspect, and its `SKILL.md` gives a new agent the same boundaries. It does not contain the actual tender links or captured records.

## How it works

1. `make_manifest.py` reads the **hyperlink targets** in a Word document, starting just after a named marker such as `NEW`. It keeps the original order and section labels, and writes one JSON line per distinct URL.
2. `capture_tenders.py` opens the official MahaTenders homepage in a visible Chromium window. It then visits up to 10 supplied detail links per run. `page_extractor.js` reads the rendered table fields, including Tender ID, title, organisation, dates, estimated value, fees, work description, location, category and document names. The script saves each page to local JSONL before moving on.
3. `validate_capture.py` checks that captured URLs came from the manifest, marks unattempted links, and rejects repeated URLs or Tender IDs and missing required fields.

The script uses the displayed detail page. It does not search for tenders, fill a CAPTCHA, submit a bid, download documents, or write to the project workbook or databases. The script's normal browser route is an alternative for a teammate running it locally; agents should use the browser tools allowed in their own environment.

## Run a small batch

Use Python 3.10 or newer. Install the browser dependency separately from the dashboard requirements. Playwright needs its matching Chromium binary:

```powershell
python -m pip install playwright openpyxl
python -m playwright install chromium
```

From the repository root, with your own Word document and optional comparison workbook:

```powershell
python skills/mahatenders-extract/scripts/make_manifest.py "C:\path\to\links.docx" --after-marker NEW --existing-workbook "C:\path\to\collection.xlsx" --output data/raw/mahatenders-links.jsonl
python skills/mahatenders-extract/scripts/capture_tenders.py --manifest data/raw/mahatenders-links.jsonl --output data/raw/mahatenders-capture.jsonl --pending-only --max-pages 10
python skills/mahatenders-extract/scripts/validate_capture.py --manifest data/raw/mahatenders-links.jsonl --capture data/raw/mahatenders-capture.jsonl
```

Omit `--existing-workbook` and `--pending-only` when you want to open all links in the document. The workbook comparison is read only. `--pending-only` uses an **exact URL match**, so it is only a convenience filter. URLs with different portal session values may still identify the same tender. Check the official `Tender ID` before importing or merging records.

The capture script appends to its JSONL file. Run the same command again for the next batch: it skips URLs already in that file. To retry an `unavailable` row after investigation, remove that row from the local capture file first. The validator reports how many links remain. Its success exit code means the recorded rows are structurally valid; it does not mean the manifest is complete when `not_attempted` is above zero.

## What to inspect

Each captured row contains the supplied URL, resolved page URL, timestamp, section labels, raw portal fields, and document names. `status` is `captured`, `captcha`, or `unavailable`. A valid detail page must have a Tender ID, title and published date. Missing optional fields remain missing or retain the portal's `NA` text. Values and dates are left as displayed; normalization belongs in a later reviewed import step.

The document's section heading may disagree with the portal's `Product Category`. Keep both. A link can also lead to a pagination or error page rather than a tender detail; mark it `unavailable` and never invent its ID from the URL.

The portal's search form may require a CAPTCHA even when a supplied detail link opens normally. If the script reports `captcha`, it saves that status and stops. Ask the user to take over. If a link does not show the required fields, the script reopens the homepage and retries the exact link once, then records `unavailable`. It does not try guessed URLs or hidden endpoints.

## Data handling and verification

`data/raw/` is ignored by Git. Keep manifests, captures, workbooks and browser profiles out of commits because official links can contain session-specific query values. Commit only the scripts, the skill, and this explanation. Before publishing code changes, inspect `git diff --cached` for URLs and local paths.

The method was checked on two official detail pages in the Codex in-app browser on 9 October 2026. The later audit records a 12 October run of 129 supplied links: 127 detail pages and two pagination links. Those observations support the field mapping, but this standalone Playwright runner has not been tested against the live portal in this code change. Review a small local batch before relying on a large run. See [the project scraping audit](https://github.com/Shorya-Raj/DCDS-Project/blob/main/docs/WEB_SCRAPING_AUDIT.md) for the dated collection history.
