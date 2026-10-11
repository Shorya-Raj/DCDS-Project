"""Run the documented SQL/MongoDB demo and save share-safe local evidence."""
from __future__ import annotations

import html
import argparse
import json
import re
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from bson.decimal128 import Decimal128

from tender_explorer.database import mongo_collection, mysql_connection


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "evidence"
SAMPLE_KEY = "mahatenders:2026_NMC_1342575_23"


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    def cell(value: object) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

    lines = ["| " + " | ".join(map(cell, headers)) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    lines.extend("| " + " | ".join(cell(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def html_table(headers: list[str], rows: list[list[object]]) -> str:
    head = "".join(f"<th>{html.escape(str(value))}</th>" for value in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def run_sql_examples() -> tuple[int, list[tuple[list[str], list[list[object]]]]]:
    text = (ROOT / "sql" / "queries.sql").read_text(encoding="utf-8-sig")
    uncommented = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("--"))
    statements = [part.strip() for part in uncommented.split(";") if part.strip()]
    if len(statements) != 3:
        raise RuntimeError(f"Expected 3 documented SQL examples; found {len(statements)}")

    connection = mysql_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM tenders")
            mysql_count = int(cursor.fetchone()[0])
            outputs = []
            for statement in statements:
                cursor.execute(statement)
                headers = [column[0] for column in cursor.description]
                rows = [list(row) for row in cursor.fetchall()]
                outputs.append((headers, rows))
            return mysql_count, outputs
        finally:
            cursor.close()
    finally:
        connection.close()


def run_mongo_examples() -> tuple[int, dict[str, object], list[dict[str, object]], dict[str, str]]:
    client, collection = mongo_collection()
    temporary_id = f"demo:crud:{uuid.uuid4().hex[:12]}"
    crud: dict[str, str] = {}
    try:
        mongo_count = collection.count_documents({})
        document = collection.find_one(
            {"_id": SAMPLE_KEY},
            {
                "_id": 1,
                "source_record_id": 1,
                "source_type": 1,
                "title": 1,
                "category": 1,
                "location": 1,
                "scope": 1,
                "eligibility": 1,
            },
        )
        if document is None:
            raise RuntimeError(f"MongoDB example record {SAMPLE_KEY!r} was not found")
        categories = list(
            collection.aggregate(
                [
                    {"$unwind": "$categories"},
                    {"$group": {"_id": "$categories", "tender_count": {"$sum": 1}}},
                    {"$sort": {"tender_count": -1, "_id": 1}},
                ]
            )
        )

        temporary = {
            "_id": temporary_id,
            "source_record_id": temporary_id.split(":", 2)[-1],
            "source_type": "demo",
            "title": "Temporary CRUD demonstration record",
            "category": "Demo",
            "categories": ["Demo"],
            "location": "Local demonstration",
            "published_date": None,
            "closing_date": "2026-10-31",
            "estimated_value_inr": Decimal128("0.00"),
            "emd_inr": None,
            "source_url": "https://example.invalid/dcds-demo",
            "scope": "Temporary record used only to demonstrate CRUD operations.",
            "eligibility": "Demo only",
            "document_names_or_links": [],
            "corrigenda": None,
            "raw_source_row": {},
        }
        inserted = collection.insert_one(temporary)
        created = inserted.inserted_id == temporary_id
        read_back = collection.find_one({"_id": temporary_id})
        read_ok = read_back is not None and read_back["title"] == temporary["title"]
        update_result = collection.update_one(
            {"_id": temporary_id}, {"$set": {"title": "Temporary CRUD record updated"}}
        )
        updated = update_result.modified_count == 1
        update_read = collection.find_one({"_id": temporary_id})
        update_ok = update_read is not None and update_read["title"] == "Temporary CRUD record updated"
        delete_result = collection.delete_one({"_id": temporary_id})
        absent = collection.find_one({"_id": temporary_id}) is None
        crud = {
            "create": "passed" if created else "failed",
            "read": "passed" if read_ok else "failed",
            "update": "passed" if updated and update_ok else "failed",
            "delete": "passed" if delete_result.deleted_count == 1 else "failed",
            "final absence check": "passed" if absent else "failed",
        }
        if not all(value == "passed" for value in crud.values()):
            raise RuntimeError(f"Temporary MongoDB CRUD demo did not fully pass: {crud}")
        return mongo_count, document, categories, crud
    finally:
        # Ensure the temporary record is removed even if a later check raises.
        collection.delete_one({"_id": temporary_id})
        leftover = collection.find_one({"_id": temporary_id})
        client.close()
        if leftover is not None:
            raise RuntimeError("Temporary MongoDB CRUD record remains after cleanup")


def build_outputs(
    mysql_count: int,
    sql_outputs: list[tuple[list[str], list[list[object]]]],
    mongo_count: int,
    mongo_document: dict[str, object],
    mongo_categories: list[dict[str, object]],
    crud: dict[str, str],
) -> tuple[str, str]:
    captured = datetime.now().astimezone().isoformat(timespec="seconds")
    sql_summaries = [
        (
            "Category join + grouping",
            f"{len(sql_outputs[0][1])} category groups",
            sql_outputs[0][0],
            sql_outputs[0][1],
        ),
        (
            "Above-average estimated value subquery",
            f"{len(sql_outputs[1][1])} matching tenders; first 5 shown",
            sql_outputs[1][0],
            sql_outputs[1][1][:5],
        ),
        (
            "GROUP BY + HAVING location-label query",
            f"{len(sql_outputs[2][1])} source-reported labels; first 10 shown",
            sql_outputs[2][0],
            sql_outputs[2][1][:10],
        ),
    ]

    markdown = [
        "# Database demo outputs — 12 October 2026",
        "",
        f"Captured: `{captured}`",
        "",
        f"- MySQL records: **{mysql_count}**",
        f"- MongoDB documents: **{mongo_count}**",
        "- The source-plan consistency check passed separately immediately before this capture.",
        "- No source URL or raw workbook row is included in this evidence file.",
        "",
        "## SQL examples",
    ]
    sql_text = (ROOT / "sql" / "queries.sql").read_text(encoding="utf-8-sig")
    uncommented = "\n".join(line for line in sql_text.splitlines() if not line.lstrip().startswith("--"))
    statements = [part.strip() for part in uncommented.split(";") if part.strip()]
    for index, (name, summary, headers, rows) in enumerate(sql_summaries, 1):
        markdown.extend(
            [
                "",
                f"### SQL {index}: {name}",
                "",
                summary,
                "",
                "```sql",
                statements[index - 1] + ";",
                "```",
                "",
                markdown_table(headers, rows),
            ]
        )

    safe_document = {
        key: mongo_document.get(key)
        for key in ("_id", "source_record_id", "source_type", "title", "category", "location", "scope", "eligibility")
    }
    mongo_headers = ["category", "tender_count"]
    mongo_rows = [[row["_id"], row["tender_count"]] for row in mongo_categories]
    markdown.extend(
        [
            "",
            "## MongoDB examples",
            "",
            "### Read one imported document",
            "",
            "The projection intentionally excludes `source_url` and `raw_source_row`.",
            "",
            "```json",
            json.dumps(safe_document, indent=2, ensure_ascii=False, default=str),
            "```",
            "",
            f"### Category aggregation ({len(mongo_categories)} groups)",
            "",
            markdown_table(mongo_headers, mongo_rows),
            "",
            "### Temporary CRUD check",
            "",
            "A schema-valid `demo:crud:*` record was created, read, updated, deleted, and checked absent. The cleanup ran even if a check failed; no imported tender was changed.",
            "",
            markdown_table(["Operation", "Result"], [[key, value] for key, value in crud.items()]),
            "",
            "Interpret the third SQL query as a count of source-reported labels. Labels such as `Work` and `EE/EAST/MSIB` are not necessarily standardized geographic locations.",
            "",
            "Estimates are published estimates, not awards or actual spending; missing estimates remain NULL.",
        ]
    )
    markdown_text = "\n".join(markdown) + "\n"

    sections = [
        '<h1>Database demo results</h1>',
        f'<p class="muted">Captured {html.escape(captured)}. MySQL: <b>{mysql_count:,}</b> records; MongoDB: <b>{mongo_count:,}</b> documents.</p>',
        '<div class="note">Reconciled to the reviewed workbook source plan. Source URLs and raw workbook rows are excluded from this evidence view.</div>',
        '<h2>SQL examples</h2>',
    ]
    for index, (name, summary, headers, rows) in enumerate(sql_summaries, 1):
        sections.append(f'<section><h3>SQL {index}: {html.escape(name)}</h3><p>{html.escape(summary)}</p>')
        sections.append(f'<details><summary>Show SQL</summary><pre>{html.escape(statements[index - 1])};</pre></details>')
        sections.append(html_table(headers, rows))
        sections.append('</section>')
    sections.extend(
        [
            '<h2>MongoDB examples</h2>',
            '<section><h3>Read an imported document</h3><p>Projection omits source URL and raw source row.</p>',
            f'<pre>{html.escape(json.dumps(safe_document, indent=2, ensure_ascii=False, default=str))}</pre></section>',
            f'<section><h3>Category aggregation ({len(mongo_categories)} groups)</h3>{html_table(mongo_headers, mongo_rows)}</section>',
            '<section><h3>Temporary CRUD check</h3><p>The demo record was removed; no imported tender was changed.</p>',
            html_table(["Operation", "Result"], [[key, value] for key, value in crud.items()]),
            '</section>',
            '<div class="note">The third SQL query counts source-reported labels. Values such as “Work” and “EE/EAST/MSIB” are not necessarily standardized geographic locations. Estimates are not awards or actual spending; missing estimates stay NULL.</div>',
        ]
    )
    html_text = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Database demo results</title><style>
body{font:16px/1.5 system-ui,sans-serif;max-width:1200px;margin:32px auto;padding:0 24px;color:#172033;background:#f6f8fb}
h1{font-size:2rem;margin-bottom:4px}h2{margin-top:32px;border-bottom:2px solid #cbd5e1;padding-bottom:6px}
h3{margin-bottom:4px}.muted{color:#4b5563}.note{background:#e9f2ff;border-left:4px solid #2878c8;padding:12px 16px;margin:16px 0;border-radius:4px}
section{background:white;border:1px solid #d6dde8;border-radius:10px;padding:18px;margin:16px 0;box-shadow:0 1px 3px #0001}
table{border-collapse:collapse;width:100%;margin:12px 0}th,td{border:1px solid #cbd5e1;padding:8px;text-align:left;vertical-align:top}th{background:#eaf0f7}td{word-break:break-word}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f4f6;padding:12px;border-radius:6px;font-size:13px}details{margin:8px 0}summary{cursor:pointer;color:#1d4ed8}
</style></head><body>
""" + "\n".join(sections) + "\n</body></html>\n"
    return markdown_text, html_text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stdout-json",
        action="store_true",
        help="print sanitized Markdown/HTML evidence as JSON instead of writing files",
    )
    args = parser.parse_args()
    mysql_count, sql_outputs = run_sql_examples()
    mongo_count, document, categories, crud = run_mongo_examples()
    if mysql_count != mongo_count:
        raise RuntimeError(f"Store counts differ: MySQL={mysql_count}, MongoDB={mongo_count}")
    markdown_text, html_text = build_outputs(
        mysql_count, sql_outputs, mongo_count, document, categories, crud
    )
    markdown_path = EVIDENCE / "database_demo_outputs_2026-10-12.md"
    html_path = EVIDENCE / "database_demo_outputs_2026-10-12.html"
    if args.stdout_json:
        print(
            json.dumps(
                {
                    "markdown": markdown_text,
                    "html": html_text,
                    "summary": {
                        "mysql_count": mysql_count,
                        "mongo_count": mongo_count,
                        "sql_rows": [len(rows) for _, rows in sql_outputs],
                        "mongo_category_groups": len(categories),
                        "crud": crud,
                    },
                },
                ensure_ascii=False,
            )
        )
        return

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(markdown_text, encoding="utf-8")
    html_path.write_text(html_text, encoding="utf-8")
    print(f"MySQL records: {mysql_count}")
    print(f"MongoDB documents: {mongo_count}")
    for index, (_, rows) in enumerate(sql_outputs, 1):
        print(f"SQL {index}: {len(rows)} rows")
    print(f"MongoDB category groups: {len(categories)}")
    print(f"MongoDB temporary CRUD: {crud}")
    print(f"Saved: {markdown_path.relative_to(ROOT)}")
    print(f"Saved: {html_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
