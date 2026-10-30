"""Open saved MahaTenders detail links and save their visible fields as JSONL.

This script uses an ordinary, visible Chromium window. It does not search the
portal, submit a CAPTCHA, download tender documents, or write to a workbook.
"""

import argparse
from datetime import datetime, timezone
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

PORTAL_HOME = "https://mahatenders.gov.in/nicgep/app"
EXTRACTOR = Path(__file__).with_name("page_extractor.js")


def read_jsonl(path):
    """Yield JSON objects, reporting the line number if a file is malformed."""
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number}: invalid JSON") from error
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            yield row


def check_source_url(url):
    """Only navigate to user-supplied links on the official portal."""
    parts = urlparse(url)
    if parts.scheme != "https" or parts.hostname != "mahatenders.gov.in" or parts.path != "/nicgep/app":
        raise ValueError("Manifest contains a URL outside the official MahaTenders app")


def load_work(manifest_path, output_path, pending_only):
    manifest = list(read_jsonl(manifest_path))
    if not manifest:
        raise ValueError("Manifest is empty")
    if pending_only and any(row.get("already_recorded") is None for row in manifest):
        raise ValueError("--pending-only needs a manifest compared with --existing-workbook")

    urls = [row.get("url") for row in manifest]
    if any(not isinstance(url, str) for url in urls) or len(set(urls)) != len(urls):
        raise ValueError("Manifest needs one unique URL per row")
    for url in urls:
        check_source_url(url)

    previous = list(read_jsonl(output_path)) if output_path.exists() else []
    completed_urls = [row.get("url") for row in previous]
    if any(not isinstance(url, str) for url in completed_urls) or len(set(completed_urls)) != len(completed_urls) or any(url not in urls for url in completed_urls):
        raise ValueError("Existing capture contains duplicate or unknown URLs; review it before resuming")

    remaining = [
        row for row in manifest
        if row["url"] not in completed_urls
        and (not pending_only or row.get("already_recorded") is False)
    ]
    return remaining, len(previous)


def read_page(page, manifest_row, extractor_code):
    """Read one rendered page; retry once through the homepage if it is blank."""
    url = manifest_row["url"]
    metadata = {"url": url, "categories": manifest_row.get("categories", [])}
    last_error = None

    for attempt in range(2):
        try:
            if attempt:
                page.goto(PORTAL_HOME, wait_until="domcontentloaded", timeout=30000)
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            # The portal can populate the detail table just after navigation.
            try:
                page.wait_for_function(
                    "document.body && (document.body.innerText.includes('Tender ID') || "
                    "/captcha/i.test(document.body.innerText))",
                    timeout=6000,
                )
            except Exception:
                pass  # The extractor below classifies a blank or error page.
            record = page.evaluate(extractor_code, metadata)
            if record["status"] in {"captured", "captcha"}:
                return record
        except Exception as error:
            last_error = type(error).__name__

    return {
        "url": url,
        "resolved_url": getattr(page, "url", None),
        "categories": metadata["categories"],
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "unavailable",
        "fields": {},
        "documents": [],
        "reason": last_error or "Required detail fields were not visible after one retry",
    }


def capture(manifest_path, output_path, pending_only, max_pages, delay_seconds):
    remaining, previous_count = load_work(manifest_path, output_path, pending_only)
    if not remaining:
        print("No new links to capture.")
        return 0

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise SystemExit("Install Playwright first: python -m pip install playwright") from error

    extractor_code = EXTRACTOR.read_text(encoding="utf-8")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    captured = 0
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=False)
        page = context.new_page()
        try:
            page.goto(PORTAL_HOME, wait_until="domcontentloaded", timeout=30000)
            with output_path.open("a", encoding="utf-8", newline="\n") as output:
                for manifest_row in remaining[:max_pages]:
                    record = read_page(page, manifest_row, extractor_code)
                    record["sequence"] = manifest_row["sequence"]
                    record["source_document"] = manifest_row.get("source_document")
                    output.write(json.dumps(record, ensure_ascii=False) + "\n")
                    output.flush()
                    captured += 1
                    tender_id = record.get("fields", {}).get("Tender ID", "")
                    print(f"{record['sequence']}: {record['status']} {tender_id}")
                    if record["status"] == "captcha":
                        print("CAPTCHA shown. Capture stopped; ask the user to take over.")
                        return 2
                    time.sleep(delay_seconds)
        finally:
            context.close()
            browser.close()

    print(f"Saved {captured} new rows ({previous_count + captured} total) to {output_path}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="JSONL made by make_manifest.py")
    parser.add_argument("--output", type=Path, required=True, help="local JSONL capture file")
    parser.add_argument("--pending-only", action="store_true", help="use only URLs marked not yet recorded")
    parser.add_argument("--max-pages", type=int, default=10, help="small batch size (default: 10)")
    parser.add_argument("--delay-seconds", type=float, default=1.5)
    args = parser.parse_args()
    if args.max_pages < 1 or args.delay_seconds < 0:
        parser.error("--max-pages must be positive and --delay-seconds cannot be negative")
    try:
        return capture(args.manifest, args.output, args.pending_only, args.max_pages, args.delay_seconds)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    sys.exit(main())
