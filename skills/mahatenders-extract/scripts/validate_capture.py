"""Check a raw JSONL capture against a document link manifest."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


def read_jsonl(path):
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{number}: {exc}") from exc
                if not isinstance(value, dict):
                    raise ValueError(f"{path}:{number}: expected a JSON object")
                yield value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args()
    manifest = list(read_jsonl(args.manifest))
    capture = list(read_jsonl(args.capture))
    expected = {record["url"] for record in manifest}
    pending_expected = {record["url"] for record in manifest if record.get("already_recorded") is False}
    url_counts = Counter(record.get("url") for record in capture if isinstance(record.get("url"), str))
    id_counts = Counter(
        str(record.get("fields", {}).get("Tender ID", "")).strip()
        for record in capture
        if record.get("status") == "captured" and isinstance(record.get("fields"), dict)
    )
    errors = []
    for number, record in enumerate(capture, 1):
        url = record.get("url", "")
        fields = record.get("fields", {})
        if not isinstance(url, str) or url not in expected:
            errors.append(f"capture line {number}: URL is not in manifest")
        if not isinstance(url, str) or urlparse(url).hostname != "mahatenders.gov.in":
            errors.append(f"capture line {number}: unexpected source host")
        if record.get("status") not in {"captured", "captcha", "unavailable"}:
            errors.append(f"capture line {number}: invalid status")
        if not isinstance(fields, dict):
            errors.append(f"capture line {number}: fields must be an object")
            continue
        if record.get("status") == "captured":
            for key in ("Tender ID", "Title", "Published Date"):
                if not str(fields.get(key, "")).strip():
                    errors.append(f"capture line {number}: missing {key}")
    errors.extend(f"URL captured {count} times: {url}" for url, count in url_counts.items() if count > 1)
    errors.extend(f"Tender ID captured {count} times: {tender_id}" for tender_id, count in id_counts.items() if tender_id and count > 1)
    report = {
        "manifest_urls": len(expected),
        "capture_rows": len(capture),
        "captured": sum(record.get("status") == "captured" for record in capture),
        "captcha": sum(record.get("status") == "captcha" for record in capture),
        "unavailable": sum(record.get("status") == "unavailable" for record in capture),
        "not_attempted": len(expected - set(url_counts)),
        "pending_not_attempted": len(pending_expected - set(url_counts)) if pending_expected else None,
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
