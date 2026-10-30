---
name: mahatenders-extract
description: Extract official MahaTenders detail pages from user-supplied links or a Word document, preserving source fields and validating local captures.
---

# MahaTenders extraction

Read [GUIDE.md](GUIDE.md) for the human workflow and script commands. Use the current user's requested start point and output format.

- Make an ordered manifest from the supplied Word hyperlinks with `scripts/make_manifest.py`. Keep repeated document positions, but open each distinct URL once. An `already_recorded` flag means only that the exact URL was in the comparison workbook; session query values may change. Reconcile captured tenders by `Tender ID` before importing.
- For a local, visible-browser run, use `scripts/capture_tenders.py` in small batches. Its page reader is `scripts/page_extractor.js`. If the environment's computer-use rules require a different browser tool, use that tool to open the same links and run the read-only page function; keep the capture schema unchanged.
- Accept a page as `captured` only when it shows `Tender ID`, `Title`, and `Published Date`. Keep raw portal text, the exact source URL, document names, and capture time. Document headings are provenance; the portal's `Product Category` is a separate field.
- If a detail link fails, retry that exact link once after opening the official homepage in the same browser context. Record a persistent failure as `unavailable`. If a CAPTCHA appears, stop and ask the user to take over; do not solve or bypass it.
- Save raw captures locally, outside Git. Do not commit manifests, workbooks, capture files, browser profiles, credentials, or session-bearing URLs. Validate a batch with `scripts/validate_capture.py`; resolve repeated Tender IDs before data import.

The scripts collect raw evidence. They do not update a workbook or database unless the user separately asks for that work.
