"""Presentation components for the local Works Atlas interface."""
from html import escape
from pathlib import Path
from decimal import Decimal
import streamlit as st


def apply_styles():
    st.html(f"<style>{Path(__file__).with_name('styles.css').read_text(encoding='utf-8')}</style>")


def show_header():
    st.html('''<header class="atlas-header">
      <div class="atlas-masthead"><span class="atlas-logo" aria-hidden="true">W<span>／</span>A</span>
      <span>WORKS ATLAS <small>MAHARASHTRA</small></span><span class="edition">PUBLIC PROCUREMENT / RECORD EXPLORER</span></div>
      <div class="atlas-intro"><div><p class="eyebrow">THE WORK BEHIND THE PLACES</p>
      <h1>A closer look at<br><em>what gets built.</em></h1>
      <p class="intro-copy">Explore Maharashtra’s public works. Find a tender,<br>follow its details, understand the data.</p></div>
      <svg class="atlas-drawing" viewBox="0 0 500 190" fill="none" aria-hidden="true">
      <defs><pattern id="atlas-grid" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" stroke="currentColor" opacity=".13"/></pattern></defs>
      <rect width="500" height="190" fill="url(#atlas-grid)"/>
      <g stroke="currentColor" stroke-width="1.4"><path d="M20 135H480M20 142H480M110 160V35H120V160M370 160V35H380V160M115 40Q245 200 375 40M25 125L115 40M375 40L475 125"/>
      <path d="M50 103V135M75 78V135M150 78V135M185 106V135M220 121V135M255 124V135M290 116V135M325 96V135M350 70V135M410 70V135M440 97V135" opacity=".65"/>
      <path d="M30 173H470M30 169V177M470 169V177" opacity=".4"/></g>
      <text x="190" y="185" fill="currentColor" font-family="monospace" font-size="8" letter-spacing="3">CONNECTING THE DETAILS</text></svg></div>
      </header>''')


def show_sidebar_brand():
    """Compatibility helper for older entry points."""
    with st.sidebar:
        st.markdown("### Works Atlas")
        st.caption("Maharashtra · public works records")


def section_label(number, text):
    st.html(f'<div class="section-label"><span>{escape(str(number))}</span>{escape(text)}</div>')


def format_money(value):
    if value is None:
        return "Not reported"
    amount = Decimal(str(value))
    if abs(amount) >= 10000000:
        return f"₹{amount / Decimal('10000000'):,.2f} Cr"
    if abs(amount) >= 100000:
        return f"₹{amount / Decimal('100000'):,.2f} L"
    return f"₹{amount:,.0f}"


def tender_card(row, selected=False):
    """Render escaped source data; interactive controls remain native widgets."""
    closing = row['closing_date'].strftime('%d %b %Y') if row['closing_date'] else 'Not reported'
    st.html(f'''<article class="tender-card {'is-selected' if selected else ''}">
      <div class="card-top"><span class="category-tag">{escape(row['category'])}</span><span class="card-arrow" aria-hidden="true">↗</span></div>
      <p class="record-id">{escape(row['source_record_id'])}</p>
      <h3>{escape(row['title'])}</h3>
      <p class="card-location">{escape(row['location'])}</p>
      <div class="card-facts"><div><span>REPORTED ESTIMATE</span><strong>{format_money(row['estimated_value_inr'])}</strong></div>
      <div><span>CLOSING DATE</span><strong>{closing}</strong></div></div></article>''')


def record_heading(row):
    st.html(f'''<div class="record-heading"><p class="eyebrow">{escape(row['category'])}</p>
    <h3>{escape(row['title'])}</h3><p class="record-id">{escape(row['source_record_id'])}</p></div>''')
