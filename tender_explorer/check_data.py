"""Compare tender identity and shared fields across MySQL and MongoDB."""
from __future__ import annotations

import argparse
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from tender_explorer.database import mysql_connection, mongo_collection
from tender_explorer.normalize import load_records, make_tender_key


SHARED_FIELDS = (
    "source_record_id",
    "source_type",
    "title",
    "category",
    "location",
    "published_date",
    "closing_date",
    "estimated_value_inr",
    "emd_inr",
    "source_url",
)
MONEY_FIELDS = {"estimated_value_inr", "emd_inr"}
DATE_FIELDS = {"published_date", "closing_date"}


def _identity_error(store: str, key: str, record: dict):
    try:
        expected = make_tender_key(record["source_type"], record["source_record_id"])
    except (KeyError, TypeError, ValueError) as exc:
        return (store, key, f"invalid source identity ({exc})")
    if key != expected:
        return (store, key, f"expected key {expected!r} from source type and record ID")
    return None


def _canonical(field: str, value):
    if value is None:
        return None
    if field in {"category", "location"}:
        # MySQL lookup-table names use the server's case-insensitive collation;
        # MongoDB keeps the source spelling in the common document fields.
        return str(value).strip().casefold()
    if field in MONEY_FIELDS:
        if hasattr(value, "to_decimal"):
            value = value.to_decimal()
        return Decimal(str(value)).quantize(Decimal("0.01"))
    if field in DATE_FIELDS:
        if isinstance(value, datetime):
            value = value.date()
        if isinstance(value, date):
            return value.isoformat()
        return date.fromisoformat(str(value)).isoformat()
    return value


def _compare_records(tender_key, first_name, first, second_name, second):
    mismatches = []
    for field in SHARED_FIELDS:
        try:
            first_value = _canonical(field, first[field])
            second_value = _canonical(field, second[field])
        except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
            mismatches.append((tender_key, field, f"invalid value ({exc})"))
            continue
        if first_value != second_value:
            mismatches.append(
                (tender_key, field, f"{first_name}={first_value!r}; {second_name}={second_value!r}")
            )
    return mismatches


def main(expected_input: Path | None = None):
    sql = mysql_connection()
    mongo_client, details = mongo_collection()
    try:
        cursor = sql.cursor(dictionary=True)
        cursor.execute(
            """SELECT t.tender_key, t.source_record_id, t.source_type, t.title,
                      c.name AS category, l.name AS location, t.published_date,
                      t.closing_date, t.estimated_value_inr, t.emd_inr, t.source_url
               FROM tenders AS t
               JOIN categories AS c ON c.category_id=t.category_id
               JOIN locations AS l ON l.location_id=t.location_id"""
        )
        sql_records = {row["tender_key"]: row for row in cursor.fetchall()}
        cursor.close()

        projection = {"_id": 1, **{field: 1 for field in SHARED_FIELDS}}
        mongo_records = {row["_id"]: row for row in details.find({}, projection)}
        sql_ids, mongo_ids = set(sql_records), set(mongo_records)
        only_sql = sorted(sql_ids - mongo_ids)
        only_mongo = sorted(mongo_ids - sql_ids)
        mismatches = []
        identity_errors = []
        expected_records = None
        if expected_input is not None:
            expected_records = {row["tender_key"]: row for row in load_records(expected_input)}
            expected_ids = set(expected_records)
            only_expected_sql = sorted(expected_ids - sql_ids)
            only_expected_mongo = sorted(expected_ids - mongo_ids)
            unexpected_sql = sorted(sql_ids - expected_ids)
            unexpected_mongo = sorted(mongo_ids - expected_ids)
        else:
            only_expected_sql = only_expected_mongo = []
            unexpected_sql = unexpected_mongo = []

        for key, row in sql_records.items():
            error = _identity_error("MySQL", key, row)
            if error:
                identity_errors.append(error)
        for key, row in mongo_records.items():
            error = _identity_error("MongoDB", key, row)
            if error:
                identity_errors.append(error)

        for tender_key in sorted(sql_ids & mongo_ids):
            mismatches.extend(
                _compare_records(tender_key, "MySQL", sql_records[tender_key], "MongoDB", mongo_records[tender_key])
            )
        if expected_records is not None:
            for tender_key in sorted(set(expected_records) & sql_ids):
                mismatches.extend(
                    _compare_records(tender_key, "source plan", expected_records[tender_key], "MySQL", sql_records[tender_key])
                )
            for tender_key in sorted(set(expected_records) & mongo_ids):
                mismatches.extend(
                    _compare_records(tender_key, "source plan", expected_records[tender_key], "MongoDB", mongo_records[tender_key])
                )

        print(f"MySQL: {len(sql_ids)} tender records; MongoDB: {len(mongo_ids)} tender documents")
        if only_sql:
            print(f"Only in MySQL ({len(only_sql)}): {only_sql[:10]}")
        if only_mongo:
            print(f"Only in MongoDB ({len(only_mongo)}): {only_mongo[:10]}")
        if expected_records is not None:
            print(f"Source plan: {len(expected_records)} expected tender records")
            if only_expected_sql:
                print(f"Expected but missing in MySQL ({len(only_expected_sql)}): {only_expected_sql[:10]}")
            if only_expected_mongo:
                print(f"Expected but missing in MongoDB ({len(only_expected_mongo)}): {only_expected_mongo[:10]}")
            if unexpected_sql:
                print(f"Not in source plan but present in MySQL ({len(unexpected_sql)}): {unexpected_sql[:10]}")
            if unexpected_mongo:
                print(f"Not in source plan but present in MongoDB ({len(unexpected_mongo)}): {unexpected_mongo[:10]}")
        if identity_errors:
            print(f"Invalid source identities: {len(identity_errors)}")
            for error in identity_errors[:10]:
                print(f"{error[0]} | {error[1]} | {error[2]}")
        if mismatches:
            print(f"Shared-field mismatches: {len(mismatches)}")
            for mismatch in mismatches[:10]:
                print(f"{mismatch[0]} | {mismatch[1]} | {mismatch[2]}")
            raise SystemExit(1)
        if (only_sql or only_mongo or identity_errors or only_expected_sql or only_expected_mongo
                or unexpected_sql or unexpected_mongo):
            raise SystemExit(1)
        print("Both stores match each other and the source plan; shared fields and source-derived keys agree.")
    finally:
        mongo_client.close()
        sql.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--expected-input",
        type=Path,
        help="Also compare both databases with an import source JSON/XLSX plan",
    )
    main(parser.parse_args().expected_input)
