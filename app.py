"""
Financial Market Regime Detection System — Streamlit entry point.

This file is intentionally thin: it wires together the sidebar,
inference engine, and UI tabs. All rendering logic lives in app/ui/.
"""

import os
import sys

import streamlit as st

# ── Path bootstrap ────────────────────────────────────────────────────────────
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Market Regime Detection System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ───────────────────────────────────────────────────────────────────
from src.inference import RegimeInferenceEngine
from src.utils.translations import t, SUPPORTED_LANGUAGES
from app.ui.styles import inject_css
from app.ui.sidebar import render_sidebar
from app.ui.tab_analysis import render_tab_analysis
from app.ui.tab_simulator import render_tab_simulator

# ── Global CSS ────────────────────────────────────────────────────────────────
inject_css()

# ── Language state ────────────────────────────────────────────────────────────
if "app_language" not in st.session_state:
    st.session_state["app_language"] = "en"
lang = st.session_state["app_language"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
cfg = render_sidebar(lang)

# ── Page header ───────────────────────────────────────────────────────────────
col_header, col_lang = st.columns([0.88, 0.12])
with col_header:
    st.markdown(f"<div class='main-header'>{t('main_header', lang=lang)}</div>",
                unsafe_allow_html=True)
    st.markdown(f"<div class='sub-header'>{t('sub_header', lang=lang, ticker=cfg.full_ticker)}</div>",
                unsafe_allow_html=True)

with col_lang:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    with st.popover(f"🌐 {lang.upper()}", use_container_width=True):
        st.caption(f"**{t('sidebar_language', lang=lang)}**")
        lang_options = list(SUPPORTED_LANGUAGES.values())
        current_option = SUPPORTED_LANGUAGES.get(lang, "EN (English)")
        selected_option = st.radio(
            "Select language:", lang_options,
            index=lang_options.index(current_option) if current_option in lang_options else 0,
            label_visibility="collapsed",
        )
        new_lang = "en" if selected_option.startswith("EN") else "es"
        if new_lang != lang:
            st.session_state["app_language"] = new_lang
            st.rerun()

# ── Inference engine ──────────────────────────────────────────────────────────
if (
    cfg.run_button
    or "inference_results" not in st.session_state
    or st.session_state.get("last_ticker")  != cfg.full_ticker
    or st.session_state.get("last_period")  != cfg.selected_period
):
    with st.spinner(t("spinner_fetching", lang=lang, ticker=cfg.full_ticker)):
        try:
            engine  = RegimeInferenceEngine()
            results = engine.analyze_ticker(
                cfg.full_ticker, period=cfg.selected_period,
                force_refresh=cfg.run_button,
            )
            st.session_state["inference_results"] = results
            st.session_state["last_ticker"]        = cfg.full_ticker
            st.session_state["last_period"]        = cfg.selected_period
        except Exception as exc:
            st.error(t("ticker_error_friendly", lang=lang, ticker=cfg.full_ticker))
            st.caption(f"Technical detail: {exc}")
            st.stop()

results = st.session_state.get("inference_results")

# ── Tabs ──────────────────────────────────────────────────────────────────────
if results:
    tab_analysis, tab_simulator = st.tabs([
        t("tab_analysis",  lang=lang),
        t("tab_simulator", lang=lang),
    ])

    with tab_analysis:
        render_tab_analysis(
            results=results,
            lang=lang,
            selected_fiat=cfg.selected_fiat,
            fiat_symbol=cfg.fiat_symbol,
            full_ticker=cfg.full_ticker,
            coin_ticker=cfg.coin_ticker,
        )

    with tab_simulator:
        render_tab_simulator(
            results=results,
            lang=lang,
            coin_ticker=cfg.coin_ticker,
            selected_fiat=cfg.selected_fiat,
            fiat_symbol=cfg.fiat_symbol,
            full_ticker=cfg.full_ticker,
        )
