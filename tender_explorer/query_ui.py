"""On-demand query viewer and safe search controls for the Streamlit dashboard."""
from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from urllib.parse import urlparse, urlunparse

import streamlit as st

from tender_explorer.query_tools import FILTER_OPTIONS_SQL, MONGO_RESULT_FIELDS


SQL_EXAMPLES = {
    "Find Civil Works tenders": """SELECT t.source_record_id, t.title, c.name AS category,
       l.name AS location, t.closing_date
FROM tenders AS t
JOIN categories AS c ON c.category_id = t.category_id
JOIN locations AS l ON l.location_id = t.location_id
WHERE c.name = 'Civil Works'
ORDER BY t.closing_date DESC
LIMIT 20""",
    "Count tenders by category": """SELECT c.name AS category, COUNT(*) AS tender_count
FROM tenders AS t
JOIN categories AS c ON c.category_id = t.category_id
GROUP BY c.category_id, c.name
ORDER BY tender_count DESC""",
    "Tenders with reported estimates": """SELECT source_record_id, title, estimated_value_inr
FROM tenders
WHERE estimated_value_inr IS NOT NULL
ORDER BY estimated_value_inr DESC
LIMIT 20""",
}
MONGO_EXAMPLES = {
    "Find Civil Works details": '{"category": "Civil Works"}',
    "Find one Tender ID": '{"source_record_id": "2026_ANMC_1340445_10"}',
    "Closing on or after a date": '{"closing_date": {"$gte": "2026-10-01"}}',
    "Missing reported estimate": '{"estimated_value_inr": null}',
}


def _safe_display_value(value):
    """Hide source URL parameters and make database values readable."""
    if hasattr(value, "to_decimal"):
        return str(value.to_decimal())
    if isinstance(value, (date, Decimal)):
        return value.isoformat() if isinstance(value, date) else str(value)
    if isinstance(value, str) and value.lower().startswith(("http://", "https://")):
        try:
            parsed = urlparse(value)
            host = (parsed.hostname or "").casefold()
        except ValueError:
            return "[source link hidden]"
        if parsed.scheme in {"http", "https"} and any(
            host == domain or host.endswith("." + domain)
            for domain in ("mahatenders.gov.in", "tender247.com")
        ):
            return urlunparse(("https", host, parsed.path or "/", "", "", ""))
        return "[source link hidden]"
    if isinstance(value, (list, dict)):
        return json.dumps(value, default=str, ensure_ascii=False)
    if isinstance(value, bytes):
        return "[binary value]"
    return value


def _show_rows(rows, truncated):
    if not rows:
        st.info("No records matched this query.")
        return
    st.dataframe(
        [{field: _safe_display_value(value) for field, value in row.items()} for row in rows],
        width="stretch", hide_index=True, height=360,
    )
    st.caption(
        f"Showing the first {len(rows)} rows." +
        (" More rows matched; narrow the query to see them." if truncated else "")
    )


def show_query_explorer(dashboard_sql, dashboard_params, selected_key, mode):
    st.subheader("Query explorer")
    if mode == "Sample data":
        st.info(
            "Sample data is filtered in Python from the bundled JSON file. "
            "Choose MySQL + MongoDB to see live database queries and run your own searches."
        )
        return

    with st.expander("Queries used by the dashboard", expanded=False):
        st.write("The sidebar filters run this parameterized MySQL query:")
        st.code(dashboard_sql, language="sql")
        st.write("Bound values for the %s placeholders, in order:")
        st.json([value.isoformat() if isinstance(value, date) else value for value in dashboard_params])
        st.caption("The values are bound separately so search text cannot become SQL code.")
        if selected_key:
            st.write("Selecting a listing reads its detail from MongoDB with:")
            st.code(f'collection.find_one({{"_id": {selected_key!r}}})', language="python")
        else:
            st.caption("No listing is selected, so there is no MongoDB detail lookup.")
        with st.expander("Other database reads for sidebar choices"):
            st.code(FILTER_OPTIONS_SQL["categories"], language="sql")
            st.code(FILTER_OPTIONS_SQL["locations"], language="sql")
            st.caption("These two option lists are cached for up to 60 seconds.")

    sql_tab, mongo_tab, guide_tab = st.tabs(["Write SQL", "Write MongoDB filter", "Query guide"])

    with sql_tab:
        st.caption("Run one SELECT query. Results are limited to 100 rows and the database uses a read-only transaction.")
        if "sql_editor" not in st.session_state:
            st.session_state["sql_editor"] = SQL_EXAMPLES["Find Civil Works tenders"]
        sql_example = st.selectbox("SQL example", list(SQL_EXAMPLES), key="sql_example")
        if st.button("Load SQL example"):
            st.session_state["sql_editor"] = SQL_EXAMPLES[sql_example]
        with st.form("sql_query_form"):
            sql_text = st.text_area("SQL query", key="sql_editor", height=220)
            run_sql = st.form_submit_button("Run SQL search")
        if run_sql:
            from tender_explorer.database import run_read_only_sql
            try:
                result, truncated = run_read_only_sql(sql_text)
                st.session_state["sql_result"] = (result, truncated, sql_text)
                st.session_state["sql_error"] = None
            except Exception as exc:
                st.session_state["sql_result"] = None
                if isinstance(exc, ValueError):
                    st.session_state["sql_error"] = str(exc)
                else:
                    st.session_state["sql_error"] = f"{type(exc).__name__}: {str(exc)[:240]}"
        if st.session_state.get("sql_error"):
            st.error(st.session_state["sql_error"])
        if st.session_state.get("sql_result") is not None:
            result, truncated, executed = st.session_state["sql_result"]
            st.write("Results from the last SQL search:")
            st.code(executed, language="sql")
            _show_rows(result, truncated)

    with mongo_tab:
        st.caption(
            "Write a JSON find filter for tender_details. Only searchable fields and "
            "read-only comparisons are accepted; results show safe summary fields."
        )
        if "mongo_editor" not in st.session_state:
            st.session_state["mongo_editor"] = MONGO_EXAMPLES["Find Civil Works details"]
        mongo_example = st.selectbox("MongoDB example", list(MONGO_EXAMPLES), key="mongo_example")
        if st.button("Load MongoDB example"):
            st.session_state["mongo_editor"] = MONGO_EXAMPLES[mongo_example]
        with st.form("mongo_query_form"):
            mongo_text = st.text_area("MongoDB filter (JSON)", key="mongo_editor", height=130)
            run_mongo = st.form_submit_button("Run MongoDB search")
        if run_mongo:
            from tender_explorer.database import run_read_only_mongo
            try:
                result, truncated = run_read_only_mongo(mongo_text)
                st.session_state["mongo_result"] = (result, truncated, mongo_text)
                st.session_state["mongo_error"] = None
            except Exception as exc:
                st.session_state["mongo_result"] = None
                if isinstance(exc, ValueError):
                    st.session_state["mongo_error"] = str(exc)
                else:
                    st.session_state["mongo_error"] = f"{type(exc).__name__}: {str(exc)[:240]}"
        if st.session_state.get("mongo_error"):
            st.error(st.session_state["mongo_error"])
        if st.session_state.get("mongo_result") is not None:
            result, truncated, executed = st.session_state["mongo_result"]
            st.write("Results from the last MongoDB search:")
            st.code(
                "db.tender_details.find(" + executed + ", " +
                json.dumps({field: 1 for field in MONGO_RESULT_FIELDS}) + ").limit(101)",
                language="javascript",
            )
            _show_rows(result, truncated)

    with guide_tab:
        st.markdown("**Start with an example**, change a value, then press its Run button. The editor will not run while you type.")
        st.markdown(
            "**SQL:** Search structured fields in the tenders table. JOIN categories or "
            "JOIN locations to search their names. WHERE filters rows, ORDER BY sorts them, "
            "and LIMIT narrows results. Put text in single quotes and dates in YYYY-MM-DD "
            "form. Write one SELECT without a semicolon. Available tables: tenders, "
            "categories, locations."
        )
        st.code(SQL_EXAMPLES["Find Civil Works tenders"], language="sql")
        st.markdown(
            "**MongoDB:** Search source details in tender_details. Write a JSON object "
            "with double-quoted field names and text. Use null for missing values. "
            "Supported comparisons and combinations:"
        )
        st.code("$eq, $ne, $gt, $gte, $lt, $lte, $in, $exists, $and, $or", language="text")
        st.code(MONGO_EXAMPLES["Closing on or after a date"], language="json")
        st.markdown(
            "**Fields to try:** source_record_id, title, category, location, closing_date, "
            "estimated_value_inr, and emd_inr. Values and deadlines describe the saved "
            "snapshot, not current portal status."
        )
