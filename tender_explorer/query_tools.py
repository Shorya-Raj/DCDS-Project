"""Build dashboard searches and validate user-entered read-only queries."""
from __future__ import annotations

import json
import math
import re
from datetime import date


FILTER_OPTIONS_SQL = {
    "categories": "SELECT name FROM categories ORDER BY name",
    "locations": "SELECT name FROM locations ORDER BY name",
}

TENDER_COLUMNS = """SELECT t.tender_key, t.source_record_id, t.source_type, t.title,
       c.name AS category, l.name AS location, t.estimated_value_inr, t.emd_inr,
       t.published_date, t.closing_date, t.source_url
FROM tenders AS t
JOIN categories AS c ON c.category_id = t.category_id
JOIN locations AS l ON l.location_id = t.location_id"""

MONGO_RESULT_FIELDS = (
    "_id", "source_record_id", "title", "category", "location",
    "closing_date", "estimated_value_inr", "emd_inr",
)
MONGO_SEARCH_FIELDS = set(MONGO_RESULT_FIELDS) | {"source_type", "published_date", "categories"}
MONGO_COMPARISONS = {"$eq", "$ne", "$gt", "$gte", "$lt", "$lte", "$in", "$exists"}


def filtered_tender_query(
    selected_categories: tuple[str, ...],
    all_categories: tuple[str, ...],
    selected_locations: tuple[str, ...],
    search: str,
    only_open: bool,
    today: date,
) -> tuple[str, tuple]:
    """Return the exact parameterized MySQL query used by the sidebar."""
    clauses = []
    params = []
    if not selected_categories:
        clauses.append("1 = 0")
    elif set(selected_categories) != set(all_categories):
        clauses.append("c.name IN (" + ", ".join(["%s"] * len(selected_categories)) + ")")
        params.extend(selected_categories)
    if selected_locations:
        clauses.append("l.name IN (" + ", ".join(["%s"] * len(selected_locations)) + ")")
        params.extend(selected_locations)
    if search:
        clauses.append(
            "(LOCATE(%s, LOWER(t.title)) > 0 OR "
            "LOCATE(%s, LOWER(l.name)) > 0 OR "
            "LOCATE(%s, LOWER(t.source_record_id)) > 0)"
        )
        params.extend([search.casefold()] * 3)
    if only_open:
        clauses.append("t.closing_date >= %s")
        params.append(today)
    query = TENDER_COLUMNS
    if clauses:
        query += "\nWHERE " + "\n  AND ".join(clauses)
    query += "\nORDER BY t.closing_date, t.tender_key"
    return query, tuple(params)


def _sql_code_without_literals(query: str) -> str:
    """Mask quoted values so safety checks inspect SQL syntax, not search text."""
    output = []
    quote = None
    index = 0
    while index < len(query):
        char = query[index]
        if quote:
            if char == "\\" and index + 1 < len(query):
                output.extend("  ")
                index += 2
                continue
            if char == quote:
                if index + 1 < len(query) and query[index + 1] == quote:
                    output.extend("  ")
                    index += 2
                    continue
                quote = None
            output.append(" ")
        elif char in {"'", '"', "\u0060"}:
            quote = char
            output.append(" ")
        else:
            output.append(char)
        index += 1
    if quote:
        raise ValueError("Finish the quoted text before running the SQL query.")
    return "".join(output)


def validate_sql_query(query: str) -> str:
    """Accept one plain SELECT; the database also runs it in a read-only transaction."""
    query = query.strip()
    if not query or len(query) > 5000:
        raise ValueError("Enter one SELECT query of at most 5,000 characters.")
    code = _sql_code_without_literals(query)
    if not re.match(r"^\s*SELECT\b", code, flags=re.IGNORECASE):
        raise ValueError("Only SELECT queries are supported here.")
    if any(marker in code for marker in (";", "--", "/*", "*/", "#", "@", ":=")):
        raise ValueError("Use one SELECT query without comments, variables, or semicolons.")
    blocked = re.search(
        r"\b(INTO|OUTFILE|DUMPFILE|FOR\s+(?:UPDATE|SHARE)|LOCK|UNLOCK|"
        r"LOAD_FILE|SLEEP|BENCHMARK|GET_LOCK|RELEASE_LOCK)\b",
        code,
        flags=re.IGNORECASE,
    )
    if blocked:
        raise ValueError(f"{blocked.group(0).upper()} is not supported in read-only searches.")
    if not re.search(r"\bFROM\b", code, flags=re.IGNORECASE):
        raise ValueError("Search the project tables: tenders, categories, or locations.")
    return query


def _simple_value(value) -> bool:
    if type(value) is float:
        return math.isfinite(value)
    return value is None or type(value) in {str, int, bool}


def _validate_mongo_condition(field: str, condition) -> None:
    if _simple_value(condition):
        return
    if not isinstance(condition, dict) or not condition:
        raise ValueError(f"Use a value or a comparison object for {field}.")
    for operator, value in condition.items():
        if operator not in MONGO_COMPARISONS:
            raise ValueError(f"MongoDB operator {operator} is not supported in searches.")
        if operator == "$in":
            if not isinstance(value, list) or not 1 <= len(value) <= 25 or not all(_simple_value(item) for item in value):
                raise ValueError("$in needs 1 to 25 simple values.")
        elif operator == "$exists":
            if type(value) is not bool:
                raise ValueError("$exists needs true or false.")
        elif not _simple_value(value):
            raise ValueError(f"{operator} needs a simple value.")


def _validate_mongo_object(value: dict, depth: int = 0) -> None:
    if depth > 3 or len(value) > 20:
        raise ValueError("Keep the MongoDB search to at most 20 conditions and 3 nested levels.")
    for field, condition in value.items():
        if field in {"$and", "$or"}:
            if not isinstance(condition, list) or not 1 <= len(condition) <= 10:
                raise ValueError(f"{field} needs a list of 1 to 10 search objects.")
            for item in condition:
                if not isinstance(item, dict):
                    raise ValueError(f"{field} entries must be search objects.")
                _validate_mongo_object(item, depth + 1)
        elif field in MONGO_SEARCH_FIELDS:
            _validate_mongo_condition(field, condition)
        else:
            raise ValueError(f"Search field {field} is not available here.")


def _reject_json_constant(value):
    raise ValueError(f"{value} is not valid JSON. Use a normal number or null.")


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Field {key} appears twice in the JSON filter.")
        result[key] = value
    return result


def parse_mongo_filter(text: str) -> dict:
    """Parse a bounded MongoDB find filter; no commands or raw document fields."""
    if len(text) > 3000:
        raise ValueError("Keep the MongoDB filter below 3,000 characters.")
    try:
        value = json.loads(text, parse_constant=_reject_json_constant, object_pairs_hook=_unique_json_object)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Use valid JSON: {exc.msg} (line {exc.lineno}).") from exc
    if not isinstance(value, dict):
        raise ValueError("A MongoDB find filter must be a JSON object.")
    _validate_mongo_object(value)
    return value
