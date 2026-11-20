"""
Tab 3 — Multi-Asset Portfolio Overview.

Sections:
  1. Asset selector + Analyze button
  2. Color-coded regime snapshot table
  3. Normalized price performance chart (all assets rebased to 100)
"""

from __future__ import annotations
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from src.inference import RegimeInferenceEngine
from src.utils.translations import t, translate_regime, translate_action, translate_risk_level
from app.ui.styles import format_asset_price, REGIME_COLORS

# ── Regime → badge colour mapping ────────────────────────────────────────────
_REGIME_BG: Dict[str, str] = {
    "Moderate-Volatility Bullish": "#D1FAE5",   # green-tint
    "Low-Volatility Neutral":      "#DBEAFE",   # blue-tint
    "High-Volatility Transition":  "#FEF3C7",   # yellow-tint
    "High-Volatility Bearish":     "#FEE2E2",   # red-tint
}
_REGIME_FG: Dict[str, str] = {
    "Moderate-Volatility Bullish": "#065F46",
    "Low-Volatility Neutral":      "#1E40AF",
    "High-Volatility Transition":  "#92400E",
    "High-Volatility Bearish":     "#991B1B",
}
_ACTION_BG: Dict[str, str] = {
    "BUY / OVERWEIGHT":            "#D1FAE5",
    "HOLD / ACCUMULATE":           "#DBEAFE",
    "REDUCE EXPOSURE / DEFENSIVE": "#FEF3C7",
    "SELL / CASH (FLAT)":          "#FEE2E2",
}
_ACTION_FG: Dict[str, str] = {
    "BUY / OVERWEIGHT":            "#065F46",
    "HOLD / ACCUMULATE":           "#1E40AF",
    "REDUCE EXPOSURE / DEFENSIVE": "#92400E",
    "SELL / CASH (FLAT)":          "#991B1B",
}

# Default portfolio (diverse across asset classes)
_DEFAULT_ASSETS = ["BTC", "NVDA", "GC=F", "ETH", "^GSPC"]

# Sparkline colour palette (one per asset)
_SPARKLINE_COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EF4444"]


def _pill(text: str, bg: str, fg: str) -> str:
    """Render a colored HTML pill badge."""
    return (
        f"<span style='background:{bg}; color:{fg}; padding:2px 8px; "
        f"border-radius:999px; font-size:0.78rem; font-weight:600; "
        f"white-space:nowrap;'>{text}</span>"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 1. Asset selector
# ─────────────────────────────────────────────────────────────────────────────

def _render_selector(lang: str, selected_period: str) -> tuple[List[str], bool]:
    """Render the asset multiselect and run button. Returns (tickers, run_clicked)."""
    st.markdown(t("portfolio_description", lang=lang))

    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        chosen = st.multiselect(
            t("portfolio_select_label", lang=lang),
            options=_DEFAULT_ASSETS,
            default=_DEFAULT_ASSETS[:3],
            help=t("portfolio_select_help", lang=lang),
            max_selections=5,
        )
        # Allow freeform extra tickers via a text box
        custom_raw = st.text_input(
            "➕ Add custom tickers (comma-separated, e.g. AAPL, MELI, SOL):",
            value="",
            placeholder="TSLA, AMD, SOL-USD…",
        )
        custom_tickers = [t.strip().upper() for t in custom_raw.split(",") if t.strip()]
        all_tickers = list(dict.fromkeys(chosen + custom_tickers))  # deduplicate, preserve order

    with col_btn:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        run_clicked = st.button(
            t("portfolio_run_button", lang=lang),
            type="primary",
            use_container_width=True,
        )

    return all_tickers, run_clicked


# ─────────────────────────────────────────────────────────────────────────────
# 2. Run analysis across all selected tickers
# ─────────────────────────────────────────────────────────────────────────────

def _run_portfolio_analysis(
    tickers: List[str],
    selected_period: str,
    selected_fiat: str,
    lang: str,
) -> Dict[str, Any]:
    """Run analyze_ticker for every ticker; return dict keyed by ticker."""
    engine = RegimeInferenceEngine()
    portfolio_results: Dict[str, Any] = {}

    if len(tickers) > 5:
        st.warning(t("portfolio_max_warning", lang=lang))
        tickers = tickers[:5]

    progress = st.progress(0, text="")
    for i, ticker in enumerate(tickers):
        full_ticker = ticker if "-" in ticker else f"{ticker}-{selected_fiat}"
        progress.progress((i + 1) / len(tickers),
                          text=t("portfolio_analyzing", lang=lang, ticker=full_ticker))
        try:
            result = engine.analyze_ticker(full_ticker, period=selected_period)
            portfolio_results[full_ticker] = result
        except Exception:
            st.warning(t("portfolio_error_ticker", lang=lang, ticker=full_ticker))

    progress.empty()
    return portfolio_results


# ─────────────────────────────────────────────────────────────────────────────
# 3. Regime snapshot table
# ─────────────────────────────────────────────────────────────────────────────

def _render_snapshot_table(
    portfolio: Dict[str, Any],
    lang: str,
    fiat_symbol: str,
) -> None:
    st.markdown(t("portfolio_summary_title", lang=lang))

    rows_html = []
    for full_ticker, res in portfolio.items():
        regime      = res["current_regime"]
        forecast    = res["forecast_regime"]
        action      = res["recommendation"]["action"]
        risk        = res["recommendation"]["risk_level"]

        regime_pill   = _pill(translate_regime(regime,   lang=lang),
                               _REGIME_BG.get(regime,   "#F1F5F9"),
                               _REGIME_FG.get(regime,   "#1E293B"))
        forecast_pill = _pill(translate_regime(forecast, lang=lang),
                               _REGIME_BG.get(forecast, "#F1F5F9"),
                               _REGIME_FG.get(forecast, "#1E293B"))
        action_pill   = _pill(translate_action(action,   lang=lang),
                               _ACTION_BG.get(action,   "#F1F5F9"),
                               _ACTION_FG.get(action,   "#1E293B"))

        price_str = format_asset_price(res["latest_close"], fiat_symbol)
        chg       = res["change_24h_pct"]
        chg_color = "#10B981" if chg >= 0 else "#EF4444"
        chg_str   = f"<span style='color:{chg_color};font-weight:600'>{chg:+.2f}%</span>"

        rows_html.append(
            f"<tr>"
            f"<td style='font-weight:700; padding:10px 14px; border-bottom:1px solid #F1F5F9;'>{full_ticker}</td>"
            f"<td style='padding:10px 14px; border-bottom:1px solid #F1F5F9;'>{price_str}</td>"
            f"<td style='padding:10px 14px; border-bottom:1px solid #F1F5F9;'>{chg_str}</td>"
            f"<td style='padding:10px 14px; border-bottom:1px solid #F1F5F9;'>{regime_pill}</td>"
            f"<td style='padding:10px 14px; border-bottom:1px solid #F1F5F9;'>{forecast_pill}</td>"
            f"<td style='padding:10px 14px; border-bottom:1px solid #F1F5F9;'>{action_pill}</td>"
            f"<td style='padding:10px 14px; border-bottom:1px solid #F1F5F9;'>{res['current_volatility_pct']:.2f}%</td>"
            f"<td style='padding:10px 14px; border-bottom:1px solid #F1F5F9; color:({'#10B981' if res['current_momentum_pct']>=0 else '#EF4444'}); font-weight:600'>{res['current_momentum_pct']:+.2f}%</td>"
            f"<td style='padding:10px 14px; border-bottom:1px solid #F1F5F9;'>{translate_risk_level(risk, lang=lang)}</td>"
            f"</tr>"
        )

    col_labels = [
        t("portfolio_col_asset",      lang=lang),
        t("portfolio_col_price",      lang=lang),
        t("portfolio_col_change",     lang=lang),
        t("portfolio_col_regime",     lang=lang),
        t("portfolio_col_forecast",   lang=lang),
        t("portfolio_col_suggestion", lang=lang),
        t("portfolio_col_volatility", lang=lang),
        t("portfolio_col_momentum",   lang=lang),
        t("portfolio_col_risk",       lang=lang),
    ]
    header_html = "".join(
        f"<th style='text-align:left; padding:10px 14px; background:#F8FAFC; "
        f"border-bottom:2px solid #CBD5E1; font-size:0.80rem; font-weight:700; color:#334155; "
        f"white-space:nowrap'>{col}</th>"
        for col in col_labels
    )

    table_html = (
        f"<div style='overflow-x:auto; border-radius:10px; border:1px solid #E2E8F0; margin-top:8px;'>"
        f"<table style='width:100%; border-collapse:collapse; font-size:0.88rem; background-color:#FFFFFF;'>"
        f"<thead><tr>{header_html}</tr></thead>"
        f"<tbody>{''.join(rows_html)}</tbody>"
        f"</table>"
        f"</div>"
    )
    st.markdown(table_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Normalized performance chart
# ─────────────────────────────────────────────────────────────────────────────

def _render_normalized_chart(
    portfolio: Dict[str, Any],
    lang: str,
    selected_fiat: str,
) -> None:
    st.markdown("")
    st.markdown(t("portfolio_normalized_title", lang=lang))
    st.caption(t("portfolio_normalized_help", lang=lang))

    fig = go.Figure()
    for idx, (full_ticker, res) in enumerate(portfolio.items()):
        hist = res["df_history"]["Close"].dropna()
        if hist.empty:
            continue
        normalized = (hist / hist.iloc[0]) * 100
        color = _SPARKLINE_COLORS[idx % len(_SPARKLINE_COLORS)]
        fig.add_trace(go.Scatter(
            x=normalized.index,
            y=normalized.values,
            mode="lines",
            name=full_ticker,
            line=dict(color=color, width=2),
        ))

    fig.add_hline(y=100, line_dash="dash", line_color="#CBD5E1",
                  annotation_text="Base (100)", annotation_position="left")

    fig.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
        yaxis_title="Indexed Price (Base = 100)",
        xaxis_title=t("timeline_chart_date", lang=lang),
        height=400,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

def render_tab_portfolio(
    lang: str,
    selected_fiat: str,
    fiat_symbol: str,
    selected_period: str,
) -> None:
    """Render the full Portfolio Overview tab."""
    st.markdown(t("portfolio_title", lang=lang))

    tickers, run_clicked = _render_selector(lang, selected_period)

    # Cache key: combination of tickers + fiat + period
    cache_key = f"portfolio_{'_'.join(sorted(tickers))}_{selected_fiat}_{selected_period}"

    needs_refresh = (
        run_clicked
        or "portfolio_results" not in st.session_state
        or st.session_state.get("portfolio_cache_key") != cache_key
    )

    if needs_refresh and tickers:
        with st.spinner(""):
            portfolio = _run_portfolio_analysis(tickers, selected_period, selected_fiat, lang)
        st.session_state["portfolio_results"]   = portfolio
        st.session_state["portfolio_cache_key"] = cache_key

    portfolio = st.session_state.get("portfolio_results", {})

    if not portfolio:
        st.info(t("portfolio_empty_warning", lang=lang))
        return

    st.markdown("---")
    _render_snapshot_table(portfolio, lang, fiat_symbol)
    st.markdown("---")
    _render_normalized_chart(portfolio, lang, selected_fiat)
