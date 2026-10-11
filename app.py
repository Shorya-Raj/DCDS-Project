"""Streamlit dashboard for Maharashtra works tender listings."""
from __future__ import annotations

from collections import Counter
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st

from tender_explorer.normalize import document_for, load_records

ROOT = Path(__file__).resolve().parent
SAMPLE = ROOT / "data" / "sample_tenders.json"

st.set_page_config(page_title="Maharashtra Works Tender Explorer", layout="wide")
st.title("Maharashtra Works Tender Explorer")
st.caption("Civil, road, and infrastructure works listings in Maharashtra")


@st.cache_data
def sample_rows():
    return load_records(SAMPLE)


@st.cache_data(ttl=60)
def database_rows():
    from tender_explorer.database import mysql_connection, read_tenders

    connection = mysql_connection()
    try:
        return read_tenders(connection)
    finally:
        connection.close()


mode = st.sidebar.radio("Data source", ["Sample data", "MySQL + MongoDB"])
if mode == "Sample data":
    st.info(
        "Sample mode contains 129 Tender247 category listings. These are third-party leads, "
        "not official MahaTenders tender-detail records."
    )
else:
    st.info(
        "Database mode shows the records imported from your selected source file. "
        "The workbook loader uses official Tender IDs, excludes rows marked Include? = No, "
        "and holds included rows that lack a detail capture, exact tender-detail URL, or required fields. "
        "Portal status is a dated snapshot."
    )

try:
    rows = sample_rows() if mode == "Sample data" else database_rows()
except Exception as exc:
    st.error(f"Could not load {mode}: {exc}")
    st.stop()

if not rows:
    st.warning("No tenders found. Load data first.")
    st.stop()

categories = sorted({row["category"] for row in rows})
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
search = st.sidebar.text_input("Search title or location").strip().casefold()
only_open = st.sidebar.checkbox("Closing today or later", value=False)

from datetime import date

filtered = [
    row for row in rows
    if row["category"] in selected_categories
    and (not search or search in row["title"].casefold() or search in row["location"].casefold())
    and (not only_open or row["closing_date"] >= date.today())
]

total_value = sum(
    (row["estimated_value_inr"] or Decimal("0")) for row in filtered
)
with_value = sum(row["estimated_value_inr"] is not None for row in filtered)
left, middle, right = st.columns(3)
left.metric("Matching tenders", len(filtered))
middle.metric("Sum of reported estimates", f"₹{total_value / Decimal('10000000'):,.2f} Cr")
right.metric("Reported-value coverage", f"{with_value}/{len(filtered)}")
st.caption("Only reported estimated values contribute to the sum. Blank values stay missing; estimates are not awarded value or actual spending.")

if not filtered:
    st.warning("No listings match these filters.")
    st.stop()

counts = Counter(row["category"] for row in filtered)
st.subheader("Listings by category")
st.bar_chart(counts, horizontal=True)

st.subheader("Browse tenders")
table = [
    {
        "Record ID": row["listing_id"],
        "Title": row["title"],
        "Category": row["category"],
        "Location": row["location"],
        "Closing date": row["closing_date"],
        "Estimated value (₹)": float(row["estimated_value_inr"]) if row["estimated_value_inr"] is not None else None,
        "EMD (₹)": float(row["emd_inr"]) if row["emd_inr"] is not None else None,
    }
    for row in filtered
]
st.dataframe(table, width="stretch", hide_index=True)

labels = {
    row["tender_key"]: f'{row["listing_id"]} — {row["title"][:90]}'
    for row in filtered
}
selected_key = st.selectbox("Inspect a listing", list(labels), format_func=labels.get)
record = next(row for row in filtered if row["tender_key"] == selected_key)

if mode == "Sample data":
    detail = document_for(record)
else:
    from tender_explorer.database import mongo_collection

    try:
        mongo_client, collection = mongo_collection()
        try:
            detail = collection.find_one({"_id": selected_key})
        finally:
            mongo_client.close()
    except Exception as exc:
        st.error(f"MongoDB detail lookup failed: {exc}")
        detail = None

st.subheader("Listing details")
st.write(f'**Title:** {record["title"]}')
st.write(f'**Location:** {record["location"]}')
st.write(f'**Category:** {record["category"]}')
st.write(f'**Closing date:** {record["closing_date"]}')
host = (urlparse(record["source_url"]).hostname or "").casefold()
if host == "mahatenders.gov.in":
    source_label = "Official MahaTenders detail page"
elif host.endswith("tender247.com"):
    source_label = "Tender247 category listing"
else:
    source_label = host or "Source not identified"
st.write(f"**Record ID:** {record['listing_id']}")
st.write(f"**Source type:** {source_label}")
st.write(f'**Source URL:** {record["source_url"]}')
st.caption("Portal status and deadlines describe the captured snapshot; verify the live notice before relying on them.")
if detail:
    st.write(f'**Scope / source text:** {detail.get("scope") or detail.get("listing_text") or detail.get("title") or "Not available"}')
    st.write(f'**Eligibility:** {detail.get("eligibility") or "Not available in this snapshot"}')
    st.write(f'**Documents:** {detail.get("document_references") or detail.get("document_names_or_links") or "Not available in this snapshot"}')
    st.write(f'**Corrigenda:** {detail.get("corrigenda") or detail.get("corrigendum_snapshot") or "Not available in this snapshot"}')
    if detail.get("portal_status_snapshot"):
        st.write(f'**Portal status snapshot:** {detail["portal_status_snapshot"]} (collected {detail.get("status_collected_on") or "date not recorded"})')
else:
    st.warning("No matching MongoDB document for this listing.")

with st.expander("About the data model"):
    st.write(
        "MySQL stores searchable tender fields and normalized category/location tables. "
        "MongoDB stores source-specific details under the same Tender ID key. "
        "Missing source fields remain missing."
    )

