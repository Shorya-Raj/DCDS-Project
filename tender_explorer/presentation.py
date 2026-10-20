"""Visual presentation only; database and search behavior live in their own modules."""
from pathlib import Path

import streamlit as st


def apply_styles():
    st.html(f"<style>{Path(__file__).with_name('styles.css').read_text(encoding='utf-8')}</style>")


def show_header():
    st.html('''
    <header class="explorer-hero">
      <div class="hero-copy">
        <p class="eyebrow">MAHARASHTRA WORKS TENDER EXPLORER</p>
        <h1>Public works.<br><span>A clearer view.</span></h1>
        <p class="hero-description">Search the records. Understand the work.<br>Explore civil and infrastructure tenders across Maharashtra.</p>
        <p class="hero-footnote">ONE PLACE TO EXPLORE THE RECORDS BEHIND PUBLIC WORKS.</p>
      </div>
      <div class="blueprint" aria-hidden="true">
        <div class="blueprint-label">BUILDING A CLEARER PICTURE</div>
        <div class="blueprint-art"><i class="building low"></i><i class="building tower"></i><i class="building mid"></i><i class="building high"></i><i class="ground"></i></div>
        <span class="blueprint-caption">DISCOVER / INSPECT / UNDERSTAND</span>
      </div>
    </header>
    ''')


def show_sidebar_brand():
    with st.sidebar:
        st.html('''<div class="sidebar-brand"><span class="brand-mark" aria-hidden="true">MW</span><div><strong>Works Explorer</strong><small>MAHARASHTRA</small></div></div>''')
        st.markdown("### Refine your view")
        st.caption("Choose a source, then narrow your search.")


def section_label(number, text):
    # Only static, developer-authored labels are passed to this helper.
    st.html(f'<div class="section-label"><span>{number}</span>{text}</div>')
