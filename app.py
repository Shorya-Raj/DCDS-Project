"""Streamlit dashboard for Maharashtra works tender listings."""
from __future__ import annotations

from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import streamlit as st
import altair as alt

from tender_explorer.normalize import document_for, load_records
from tender_explorer.query_tools import filtered_tender_query
from tender_explorer.query_ui import show_query_explorer
from tender_explorer.presentation import apply_styles, show_header, show_sidebar_brand, section_label, tender_card, record_heading, format_money

ROOT = Path(__file__).resolve().parent
SAMPLE = ROOT / "data" / "sample_tenders.json"

st.set_page_config(page_title="Maharashtra Works Tender Explorer", page_icon="🏛️", layout="wide")
apply_styles()
show_header()



@st.cache_data
def sample_rows():
    return load_records(SAMPLE)


@st.cache_data(ttl=60)
def database_filter_options():
    from tender_explorer.database import mysql_connection, read_filter_options

    connection = mysql_connection()
    try:
        return read_filter_options(connection)
    finally:
        connection.close()


def database_rows(query: str, params: tuple):
    from tender_explorer.database import mysql_connection, read_filtered_tenders

    connection = mysql_connection()
    try:
        return read_filtered_tenders(connection, query, params)
    finally:
        connection.close()


def database_detail(tender_key: str):
    from tender_explorer.database import mongo_collection

    mongo_client, collection = mongo_collection()
    try:
        return collection.find_one({"_id": tender_key})
    finally:
        mongo_client.close()


def sanitized_source_url(raw_url: str) -> tuple[str | None, str]:
    """Return a safe source link with query strings and fragments removed."""
    try:
        parsed = urlparse(raw_url)
    except ValueError:
        return None, ""

    host = (parsed.hostname or "").casefold()
    trusted_host = any(
        host == domain or host.endswith(f".{domain}")
        for domain in ("mahatenders.gov.in", "tender247.com")
    )
    if not trusted_host or parsed.scheme.casefold() not in {"http", "https"}:
        return None, host

    safe_url = urlunparse(("https", host, parsed.path or "/", "", "", ""))
    return safe_url, host


source_panel, refresh_panel = st.columns([4, 1], vertical_alignment="bottom")
with source_panel:
    mode = st.radio("Data source", ["Sample data", "MySQL + MongoDB"], index=1, horizontal=True)
with refresh_panel:
    refresh = st.button("Refresh database data", icon=":material/refresh:", disabled=mode == "Sample data", width="stretch")

if mode == "MySQL + MongoDB" and refresh:
    database_filter_options.clear()
    st.rerun()

try:
    if mode == "Sample data":
        source_rows = sample_rows()
        categories = sorted({row["category"] for row in source_rows})
        locations = sorted({row["location"] for row in source_rows})
    else:
        categories, locations = database_filter_options()
except Exception as exc:
    st.error(f"Could not load {mode}.")
    if mode == "MySQL + MongoDB":
        st.caption("Check that both local database services are running and the project .env settings are correct.")
    st.caption(f"Diagnostic type: {type(exc).__name__}. Detailed connection errors are hidden to protect local configuration.")
    st.stop()

search = st.text_input("Search title, location, or source ID", placeholder="Search by work, place or tender ID…", icon=":material/search:").strip().casefold()
with st.expander("Refine results · category, location & closing date", expanded=False):
    category_panel, location_panel = st.columns(2)
    selected_categories = category_panel.multiselect(
        "Category", categories, default=categories, key=f"category_{mode}"
    )
    selected_locations = location_panel.multiselect(
        "Location", locations, default=[], key=f"location_{mode}",
        help="Choose source-reported location labels. Leave empty to include all locations.",
    )
    only_open = st.checkbox("Closing today or later", value=False)
    st.caption("Dates describe the collected snapshot. Empty category selection returns no records.")
if mode == "Sample data":
    st.info("Sample mode: 129 third-party Tender247 category listings; these are leads, not official tender-detail records.")

dashboard_sql = None
dashboard_params = ()
if mode == "MySQL + MongoDB":
    dashboard_sql, dashboard_params = filtered_tender_query(
        tuple(selected_categories), tuple(categories), tuple(selected_locations),
        search, only_open, date.today(),
    )
    try:
        filtered = database_rows(dashboard_sql, dashboard_params)
    except Exception as exc:
        st.error("Could not load the filtered MySQL tenders.")
        st.caption(f"Diagnostic type: {type(exc).__name__}. Check the database service and .env settings.")
        st.stop()
else:
    filtered = [
        row for row in source_rows
        if row["category"] in selected_categories
        and (not selected_locations or row["location"] in selected_locations)
        and (
            not search
            or search in row["title"].casefold()
            or search in row["location"].casefold()
            or search in row["source_record_id"].casefold()
        )
        and (
            not only_open
            or (row["closing_date"] is not None and row["closing_date"] >= date.today())
        )
    ]

total_value = sum(
    (row["estimated_value_inr"] or Decimal("0")) for row in filtered
)
with_value = sum(row["estimated_value_inr"] is not None for row in filtered)
left, middle, right = st.columns(3)
left.metric("Matching tenders", f"{len(filtered):,}")
middle.metric("Sum of reported estimates", f"₹{total_value / Decimal('10000000'):,.2f} Cr")
right.metric("Reported-value coverage", f"{with_value:,} / {len(filtered):,}")
st.caption("Only reported estimated values contribute to the sum. Blank values stay missing; estimates are not awarded value or actual spending.")

browse_tab, overview_tab, query_tab = st.tabs(
    ["Tenders", "Overview", "Query studio"]
)
selected_key = None
with browse_tab:
    st.subheader("Browse tenders")
    st.caption("Browse the collection, then open a record to see its source details.")
    if not filtered:
        st.info("No tenders match this search. Try a shorter search or broaden Category, Location and Closing date in Refine results.")
    else:
        view_panel, sort_panel = st.columns([2, 1])
        with view_panel:
            view = st.radio("Browse as", ["Cards", "Table"], horizontal=True)
        with sort_panel:
            sort_order = st.selectbox("Sort records", ["Source order", "Closing soonest", "Highest estimate", "Title A–Z"])
        display_rows = list(filtered)
        if sort_order == "Closing soonest":
            display_rows.sort(key=lambda row: (row["closing_date"] is None, row["closing_date"] or date.max))
        elif sort_order == "Highest estimate":
            display_rows.sort(key=lambda row: (row["estimated_value_inr"] is None, -(row["estimated_value_inr"] or Decimal("0"))))
        elif sort_order == "Title A–Z":
            display_rows.sort(key=lambda row: row["title"].casefold())
        labels = {row["tender_key"]: f'{row["source_record_id"]} — {row["title"][:90]}' for row in display_rows}
        if st.session_state.get("atlas_selected") not in labels:
            st.session_state["atlas_selected"] = next(iter(labels))
        results_panel, detail_panel = st.columns([1.7, 1], gap="large")
        with results_panel:
            section_label("01", "Matching records")
            table = [
                {
                    "Source record ID": row["source_record_id"],
                    "Title": row["title"],
                    "Category": row["category"],
                    "Location": row["location"],
                    "Closing date": row["closing_date"],
                    "Estimated value (₹)": row["estimated_value_inr"],
                    "EMD (₹)": row["emd_inr"],
                }
                for row in display_rows
            ]
            if view == "Table":
                st.dataframe(table, width="stretch", height=620, hide_index=True)
                st.caption("Use the table toolbar to search, show columns, or download CSV. Choose a record in the inspector to read its details.")
            else:
                fingerprint = (mode, tuple(selected_categories), tuple(selected_locations), search, only_open, sort_order)
                if st.session_state.get("atlas_page_filters") != fingerprint:
                    st.session_state["atlas_page"] = 1
                    st.session_state["atlas_page_filters"] = fingerprint
                pages = max(1, (len(display_rows) + 5) // 6)
                if st.session_state.get("atlas_page", 1) > pages:
                    st.session_state["atlas_page"] = 1
                page = int(st.number_input("Page", min_value=1, max_value=pages, step=1, key="atlas_page"))
                offset = (page - 1) * 6
                st.caption(f"Records {offset + 1:,}–{min(offset + 6, len(display_rows)):,} of {len(display_rows):,} · Page {page} of {pages}")
                for start in range(offset, min(offset + 6, len(display_rows)), 2):
                    card_columns = st.columns(2)
                    for column, row in zip(card_columns, display_rows[start:start + 2]):
                        with column, st.container(border=True):
                            tender_card(row, row["tender_key"] == st.session_state["atlas_selected"])
                            if st.button("Inspect record", key=f'open_{row["tender_key"]}', width="stretch", help=row["source_record_id"]):
                                st.session_state["atlas_selected"] = row["tender_key"]
                                st.rerun()

        with detail_panel:
            section_label("02", "Record inspector")
            with st.container(border=True):
                selected_key = st.selectbox("Inspect a listing", list(labels), format_func=labels.get, key="atlas_selected")
                record = next(row for row in filtered if row["tender_key"] == selected_key)

                if mode == "Sample data":
                    detail = document_for(record)
                else:
                    try:
                        detail = database_detail(selected_key)
                    except Exception as exc:
                        st.error("Could not load this listing's MongoDB details.")
                        st.caption(f"Diagnostic type: {type(exc).__name__}. Check that MongoDB is running and try refreshing the data.")
                        detail = None

                record_heading(record)
                fact_left, fact_right = st.columns(2)
                fact_left.metric("Reported estimate", format_money(record["estimated_value_inr"]))
                fact_right.metric("EMD", format_money(record["emd_inr"]))
                st.write(f'**Location:** {record["location"]}')
                st.write(f'**Category:** {record["category"]}')
                st.write(f'**Closing date:** {record["closing_date"] or "Not reported"}')
                safe_source_link, host = sanitized_source_url(record["source_url"])
                if host == "mahatenders.gov.in":
                    source_label = "Official MahaTenders detail page"
                elif host.endswith("tender247.com"):
                    source_label = "Tender247 category listing"
                else:
                    source_label = host or "Source not identified"
                id_label = "Tender ID" if record["source_type"] == "MahaTenders official detail page" else "Source record ID"
                st.write(f"**{id_label}:** {record['source_record_id']}")
                st.write(f"**Source type:** {source_label}")
                if safe_source_link:
                    st.link_button(
                        "Open source page (session parameters removed)",
                        safe_source_link,
                        help="The captured URL stays in the local database. Query strings and fragments are removed from this link.",
                    )
                else:
                    st.caption("The captured source URL is stored locally but is not shown because its domain could not be verified.")
                st.caption("Portal status and deadlines describe the captured snapshot; verify the live notice before relying on them.")
                if detail:
                    st.divider()
                    st.write(f'**Scope / source text:** {detail.get("scope") or detail.get("title") or detail.get("listing_text") or "Not available"}')
                    st.write(f'**Eligibility:** {detail.get("eligibility") or "Not available in this snapshot"}')
                    st.write(f'**Documents:** {detail.get("document_references") or detail.get("document_names_or_links") or "Not available in this snapshot"}')
                    st.write(f'**Corrigenda:** {detail.get("corrigenda") or detail.get("corrigendum_snapshot") or "Not available in this snapshot"}')
                    if detail.get("portal_status_snapshot"):
                        st.write(f'**Portal status snapshot:** {detail["portal_status_snapshot"]} (collected {detail.get("status_collected_on") or "date not recorded"})')
                else:
                    st.warning("No matching MongoDB document for this listing.")

with overview_tab:
    section_label("01", "The bigger picture")
    if not filtered:
        st.info("Choose filters with matching records to see the category overview.")
    else:
        counts = Counter(row["category"] for row in filtered)
        st.subheader("Listings by category")
        st.caption("How the matching records are distributed across work categories.")
        category_data = [
            {"category": category, "count": count}
            for category, count in counts.items()
        ]
        category_chart = (
            alt.Chart(alt.Data(values=category_data))
            .mark_bar(color="#E5B870", cornerRadiusEnd=4, size=19)
            .encode(
                x=alt.X(
                    "count:Q",
                    title="Tender count",
                    scale=alt.Scale(domainMin=0),
                    axis=alt.Axis(format=",d"),
                ),
                y=alt.Y(
                    "category:N",
                    title=None,
                    sort="-x",
                    axis=alt.Axis(labelLimit=280),
                ),
                tooltip=[
                    alt.Tooltip("category:N", title="Category"),
                    alt.Tooltip("count:Q", title="Tender count", format=",d"),
                ],
            )
            .properties(height=max(240, 36 * len(category_data)))
            .configure_view(strokeWidth=0)
            .configure_axis(gridColor="#454740", labelColor="#CCC9BF", titleColor="#CCC9BF", labelFontSize=12, titleFontSize=12, domain=False, tickSize=0, labelPadding=10)
        )
        chart_panel, insight_panel = st.columns([2, 1], gap="large")
        with chart_panel:
            st.altair_chart(category_chart, width="stretch")
        with insight_panel, st.container(border=True):
            section_label("02", "Reading the collection")
            top_category, top_count = counts.most_common(1)[0]
            st.markdown(f"**{top_category}** is the largest category in this selection.")
            st.metric("Share of matching records", f"{top_count / len(filtered):.1%}")
            st.metric("Source location labels", f"{len({row['location'] for row in filtered}):,}")
            st.caption("Location labels are preserved as reported by the source; they are not normalized district counts.")
            st.caption(f"{len(filtered) - with_value:,} records have no reported estimate. Missing values are excluded from the estimate total.")


    if mode == "Sample data":
        st.info(
            "Sample mode contains 129 Tender247 category listings. These are third-party leads, "
            "not official MahaTenders tender-detail records."
        )
    else:
        with st.expander("About these records · imported snapshot", expanded=False):
            st.info(
                "Database mode shows the records imported from your selected source file. "
                "The workbook loader uses official Tender IDs, excludes rows marked Include? = No, "
                "and holds included rows that lack a detail capture, exact tender-detail URL, or required fields. "
                "Portal status is a dated snapshot."
            )

    with st.expander("About the data model"):
        st.write(
            "MySQL stores searchable tender fields and normalized category/location tables. "
            "MongoDB stores source-specific details under the same source-prefixed key. "
            "The original source record ID is kept as a separate field. "
            "Missing source fields remain missing."
        )
with query_tab:
    show_query_explorer(dashboard_sql, dashboard_params, selected_key, mode)
