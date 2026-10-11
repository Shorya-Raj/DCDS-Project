"""Import validated tender records into MySQL and MongoDB."""
from __future__ import annotations

import argparse
from pathlib import Path

from tender_explorer.normalize import document_for, load_records, plan_mahatenders_workbook

DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "data" / "sample_tenders.json"


def select_spread_sample(records: list[dict], sample_size: int) -> list[dict]:
    """Select a deterministic, evenly spread sample while preserving source order."""
    if sample_size < 1:
        raise ValueError("Sample size must be at least 1")
    if sample_size >= len(records):
        return records
    if sample_size == 1:
        return [records[len(records) // 2]]
    last_index = len(records) - 1
    indices = [(position * last_index) // (sample_size - 1) for position in range(sample_size)]
    return [records[index] for index in indices]


def import_records(path: Path, dry_run: bool = False, sample_size: int | None = None) -> int:
    if path.suffix.casefold() in {".xlsx", ".xlsm"}:
        plan = plan_mahatenders_workbook(path)
        records = plan["records"]
        print(
            f"Workbook plan: {len(records)} records ready; "
            f"{len(plan['held'])} included rows held for review; "
            f"{plan['excluded_count']} Include?=No rows excluded."
        )
        for row in plan["held"]:
            print(f"Held Tender Log row {row['excel_row']} ({row['tender_id']}): {'; '.join(row['reasons'])}")
    else:
        records = load_records(path)
        print(f"Validated {len(records)} JSON records.")
    if sample_size is not None:
        records = select_spread_sample(records, sample_size)
        print(f"Using deterministic spread sample: {len(records)} records.")
    if dry_run:
        print("Dry run only; no database connection was opened.")
        return len(records)
    from tender_explorer.database import mysql_connection, mongo_collection, prepare_schema, upsert_tender

    sql = mysql_connection()
    mongo_client, details = mongo_collection()
    try:
        prepare_schema(sql)
        for record in records:
            try:
                upsert_tender(sql, record)
                sql.commit()
                details.replace_one({"_id": record["tender_key"]}, document_for(record), upsert=True)
            except Exception:
                sql.rollback()
                raise
        return len(records)
    finally:
        mongo_client.close()
        sql.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--dry-run", action="store_true", help="Validate the import mapping without connecting to either database")
    parser.add_argument("--sample-size", type=int, help="Import a deterministic, evenly spread sample for the first database test")
    args = parser.parse_args()
    count = import_records(args.input, dry_run=args.dry_run, sample_size=args.sample_size)
    if not args.dry_run:
        print(f"Imported {count} records into MySQL and MongoDB.")
        print("Run python -m tender_explorer.check_data to confirm matching IDs.")


if __name__ == "__main__":
    main()
