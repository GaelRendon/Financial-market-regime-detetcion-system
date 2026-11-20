"""
Sidebar panel: asset search, fiat currency, lookback window, language switcher,
and the run-analysis button.

Returns a SidebarConfig dataclass consumed by app.py and the UI tabs.
"""

from dataclasses import dataclass
import streamlit as st

from src.utils.translations import t, translate_regime, SUPPORTED_LANGUAGES
from src.utils.assets import search_asset_suggestions, extract_symbol_from_choice, get_directory_dataframe
from app.ui.styles import CURRENCY_SYMBOLS


@dataclass
class SidebarConfig:
    coin_ticker: str
    selected_fiat: str
    fiat_symbol: str
    full_ticker: str
    selected_period: str
    lang: str
    run_button: bool


def render_sidebar(lang: str) -> SidebarConfig:
    """Render all sidebar controls and return the resolved configuration."""

    st.sidebar.title(t("sidebar_title", lang=lang))
    st.sidebar.markdown(t("sidebar_subtitle", lang=lang))

    # ── Asset Search ─────────────────────────────────────────────────────────
    search_query = st.sidebar.text_input(
        t("search_asset_label", lang=lang),
        value=st.session_state.get("current_search_query", "BTC"),
        placeholder=t("search_asset_placeholder", lang=lang),
        help=t("search_asset_help", lang=lang),
    )

    suggestions = search_asset_suggestions(search_query, lang=lang, max_results=6)
    suggestion_displays = (
        [s["display"] for s in suggestions] if suggestions
        else ["🪙 BTC — Bitcoin (Cryptocurrency)"]
    )

    selected_choice = st.sidebar.selectbox(
        t("autocomplete_suggestions_label", lang=lang),
        options=suggestion_displays,
        index=0,
    )

    coin_ticker = extract_symbol_from_choice(selected_choice)

    # ── Asset Directory ───────────────────────────────────────────────────────
    with st.sidebar.expander(t("directory_expander_title", lang=lang), expanded=False):
        st.caption(t("directory_caption", lang=lang))
        st.dataframe(get_directory_dataframe(lang=lang), use_container_width=True, hide_index=True)
        st.info(t("directory_note", lang=lang))

    # ── Fiat Currency ─────────────────────────────────────────────────────────
    selected_fiat = st.sidebar.selectbox(
        t("fiat_currency_label", lang=lang),
        ["USD", "MXN", "EUR", "GBP", "CAD"],
        index=0,
    )
    fiat_symbol = CURRENCY_SYMBOLS.get(selected_fiat, "$")
    full_ticker = f"{coin_ticker}-{selected_fiat}"

    # ── Historical Lookback Window ────────────────────────────────────────────
    horizon_map = {
        t("horizon_1y", lang=lang): "1y",
        t("horizon_2y", lang=lang): "2y",
        t("horizon_3y", lang=lang): "3y",
        t("horizon_5y", lang=lang): "5y",
        t("horizon_max", lang=lang): "max",
    }
    horizon_labels = list(horizon_map.keys())
    selected_horizon_label = st.sidebar.selectbox(
        t("lookback_window_label", lang=lang), horizon_labels, index=2
    )
    selected_period = horizon_map[selected_horizon_label]

    # ── About the Model ───────────────────────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### {t('about_model_title', lang=lang)}")
    st.sidebar.caption(t("about_model_caption", lang=lang))

    # ── Run Button ────────────────────────────────────────────────────────────
    run_button = st.sidebar.button(
        t("run_button", lang=lang), type="primary", use_container_width=True
    )

    return SidebarConfig(
        coin_ticker=coin_ticker,
        selected_fiat=selected_fiat,
        fiat_symbol=fiat_symbol,
        full_ticker=full_ticker,
        selected_period=selected_period,
        lang=lang,
        run_button=run_button,
    )
