"""
Tab 1 — Live Market Regime Analysis.

Sections:
  1. Top metrics banner
  2. Hero recommendation banner + forecast probability chart
  3. Interactive historical chart (Regime Line / Candlestick)
  4. Engineered feature decomposition tabs (Returns, Volatility, Momentum)
  5. Markov transition heatmap + persistence table
  6. Power BI / Excel CSV export
"""

from __future__ import annotations
from typing import Any, Dict

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from src.utils.translations import (
    t,
    translate_regime,
    translate_action,
    translate_risk_level,
    translate_rationale,
)
from app.ui.styles import format_asset_price, REGIME_COLORS


# ─────────────────────────────────────────────────────────────────────────────
# 1. Top Metrics Banner
# ─────────────────────────────────────────────────────────────────────────────

def render_metrics(results: Dict[str, Any], lang: str, selected_fiat: str, fiat_symbol: str) -> None:
    m1, m2, m3, m4, m5 = st.columns([1.3, 1.5, 1.1, 0.9, 0.9])
    translated_curr_regime = translate_regime(results["current_regime"], lang=lang)
    is_24_7 = results.get("is_24_7", True)
    persistence_suffix = t(
        "days_suffix_calendar" if is_24_7 else "days_suffix_trading", lang=lang
    )

    with m1:
        st.metric(
            label=t("metric_current_price", lang=lang, fiat=selected_fiat),
            value=format_asset_price(results["latest_close"], fiat_symbol),
            delta=f"{results['change_24h_pct']:+.2f}% (24h)",
            help=t("metric_current_price_help", lang=lang, fiat=selected_fiat),
        )
    with m2:
        st.metric(
            label=t("metric_current_regime", lang=lang),
            value=translated_curr_regime,
            help=t("metric_current_regime_help", lang=lang, regime=translated_curr_regime),
        )
    with m3:
        st.metric(
            label=t("metric_persistence", lang=lang),
            value=f"{results['regime_streak_days']} {persistence_suffix}",
            help=t("metric_persistence_help", lang=lang),
        )
    with m4:
        st.metric(
            label=t("metric_volatility", lang=lang),
            value=f"{results['current_volatility_pct']:.2f}%",
        )
    with m5:
        st.metric(
            label=t("metric_momentum", lang=lang),
            value=f"{results['current_momentum_pct']:+.2f}%",
        )


# ─────────────────────────────────────────────────────────────────────────────
# 2. Hero Recommendation Banner + Forecast Probability Chart
# ─────────────────────────────────────────────────────────────────────────────

def render_recommendation(
    results: Dict[str, Any], lang: str, full_ticker: str
) -> None:
    rec = results["recommendation"]
    badge_color = rec["badge_color"]
    css_class = f"action-box action-box-{badge_color}"

    translated_forecast_regime = translate_regime(results["forecast_regime"], lang=lang)
    translated_action = translate_action(rec["action"], lang=lang)
    translated_risk_level = translate_risk_level(rec["risk_level"], lang=lang)
    translated_rationale = translate_rationale(
        results["forecast_regime"], lang=lang, default_text=rec["rationale"]
    )

    action_color = {
        "green": "#047857", "blue": "#1D4ED8",
        "orange": "#B45309", "red": "#B91C1C",
    }.get(badge_color, "#1D4ED8")

    exposure_text = t("exposure_suffix", lang=lang, pct=int(rec["position"] * 100))

    col_action, col_prob = st.columns([1.2, 1.0])

    with col_action:
        st.markdown(f"""
        <div class='{css_class}'>
            <div style='font-size: 0.95rem; font-weight: 600; text-transform: uppercase; color: #475569;'>
                {t('forecast_heading', lang=lang)} <span style='font-weight: 800;'>{translated_forecast_regime}</span>
            </div>
            <div class='action-title' style='color: {action_color};'>
                {t('suggestion_heading', lang=lang)} {translated_action} ({exposure_text})
            </div>
            <div style='margin-bottom: 8px;'>
                <b>{t('risk_level_label', lang=lang)}</b> {translated_risk_level}
            </div>
            <div style='font-size: 0.95rem; line-height: 1.5; color: #334155;'>
                {translated_rationale}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_prob:
        probs = results["forecast_probabilities"]
        prob_records = [
            {"Regime": translate_regime(r, lang=lang), "RawRegime": r, "Probability": p}
            for r, p in probs.items()
        ]
        prob_df = pd.DataFrame(prob_records).sort_values(by="Probability", ascending=True)

        bar_colors = [REGIME_COLORS.get(r, "#64748B") for r in prob_df["RawRegime"]]

        fig_prob = go.Figure()
        fig_prob.add_trace(go.Bar(
            y=prob_df["Regime"],
            x=prob_df["Probability"] * 100,
            orientation="h",
            marker=dict(color=bar_colors),
            text=[f"{p*100:.1f}%" for p in prob_df["Probability"]],
            textposition="auto",
        ))
        fig_prob.update_layout(
            title=t("chart_forecast_confidence_title", lang=lang, ticker=full_ticker),
            xaxis_title=t("chart_probability_axis", lang=lang),
            yaxis_title="",
            margin=dict(l=10, r=10, t=40, b=10),
            height=260,
        )
        st.plotly_chart(fig_prob, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Interactive Historical Chart (Line / Candlestick)
# ─────────────────────────────────────────────────────────────────────────────

def render_price_chart(
    results: Dict[str, Any], lang: str, full_ticker: str, selected_fiat: str
) -> None:
    st.markdown(t("timeline_section_title", lang=lang))
    hist_df = results["df_history"]

    # View switcher + date filter popover
    col_view, col_exp = st.columns([1.6, 1.2])
    with col_view:
        chart_view = st.segmented_control(
            t("chart_view_label", lang=lang),
            options=["line", "candle"],
            format_func=lambda opt: (
                t("chart_view_line", lang=lang) if opt == "line"
                else t("chart_view_candle", lang=lang)
            ),
            default="line",
            label_visibility="collapsed",
        ) or "line"

    with col_exp:
        with st.popover(t("chart_custom_dates_expander", lang=lang), use_container_width=True):
            st.caption(t("chart_quick_range_help", lang=lang))
            min_date = hist_df.index[0].date()
            max_date = hist_df.index[-1].date()
            enable_custom = st.checkbox(t("chart_filter_enable", lang=lang), value=False)
            c1, c2 = st.columns(2)
            with c1:
                custom_start = st.date_input(
                    t("chart_start_date", lang=lang),
                    value=min_date, min_value=min_date, max_value=max_date,
                    disabled=not enable_custom,
                )
            with c2:
                custom_end = st.date_input(
                    t("chart_end_date", lang=lang),
                    value=max_date, min_value=min_date, max_value=max_date,
                    disabled=not enable_custom,
                )

    # Date slicing (display only — does not affect the ML model)
    plot_df = hist_df
    if enable_custom and custom_start and custom_end and custom_start <= custom_end:
        sliced = hist_df.loc[pd.to_datetime(custom_start):pd.to_datetime(custom_end)]
        plot_df = sliced if not sliced.empty else hist_df

    fig = go.Figure()

    if chart_view == "candle" and {"Open", "High", "Low", "Close"}.issubset(plot_df.columns):
        fig.add_trace(go.Candlestick(
            x=plot_df.index,
            open=plot_df["Open"],
            high=plot_df["High"],
            low=plot_df["Low"],
            close=plot_df["Close"],
            name=t("chart_candle_trace", lang=lang),
            increasing_line_color="#10B981", increasing_fillcolor="#10B981",
            decreasing_line_color="#EF4444", decreasing_fillcolor="#EF4444",
        ))
        chart_title = t("chart_candle_title", lang=lang, ticker=full_ticker)
    else:
        for r_name, r_color in REGIME_COLORS.items():
            mask = plot_df["Market_Regime"] == r_name
            if mask.any():
                fig.add_trace(go.Scatter(
                    x=plot_df.index[mask],
                    y=plot_df["Close"][mask],
                    mode="markers",
                    name=translate_regime(r_name, lang=lang),
                    marker=dict(size=4, color=r_color),
                ))
        fig.add_trace(go.Scatter(
            x=plot_df.index,
            y=plot_df["Close"],
            mode="lines",
            name=t("timeline_close_price", lang=lang),
            line=dict(color="#94A3B8", width=1),
            opacity=0.7,
        ))
        chart_title = t("timeline_chart_title", lang=lang, ticker=full_ticker)

    # Quick-range buttons + mini-map rangeslider
    range_buttons = [
        dict(count=7,  label="7D",  step="day",   stepmode="backward"),
        dict(count=1,  label="1M",  step="month", stepmode="backward"),
        dict(count=3,  label="3M",  step="month", stepmode="backward"),
        dict(count=1,  label="1Y",  step="year",  stepmode="backward"),
        dict(step="all", label="ALL" if lang == "en" else "TODO"),
    ]
    xaxis_kwargs: dict = dict(
        title=t("timeline_chart_date", lang=lang),
        rangeselector=dict(
            buttons=range_buttons,
            bgcolor="#F8FAFC", activecolor="#3B82F6",
            font=dict(size=11, color="#1E293B"),
        ),
        rangeslider=dict(visible=True, thickness=0.08),
        type="date",
    )
    if not results.get("is_24_7", True):
        xaxis_kwargs["rangebreaks"] = [dict(bounds=["sat", "mon"])]

    fig.update_xaxes(**xaxis_kwargs)
    fig.update_layout(
        title=dict(text=chart_title, x=0, xanchor="left", y=1.0, yanchor="top", font=dict(size=14)),
        yaxis_title=t("timeline_chart_price", lang=lang, fiat=selected_fiat),
        hovermode="x unified",
        legend=dict(
            orientation="h", yanchor="top", y=0.99, xanchor="right", x=0.99,
            bgcolor="rgba(255,255,255,0.75)", bordercolor="#E2E8F0",
            borderwidth=1, font=dict(size=11),
        ),
        height=500,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Engineered Feature Decomposition Tabs
# ─────────────────────────────────────────────────────────────────────────────

def render_features(results: Dict[str, Any], lang: str) -> None:
    st.markdown(t("features_section_title", lang=lang))
    hist_df = results["df_history"]
    f1, f2, f3 = st.tabs([
        t("features_tab_returns", lang=lang),
        t("features_tab_volatility", lang=lang),
        t("features_tab_momentum", lang=lang),
    ])

    with f1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist_df.index, y=hist_df["Returns"] * 100,
            mode="lines", name=t("features_chart_return_axis", lang=lang),
            line=dict(color="#6366F1", width=1),
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.update_layout(height=300, yaxis_title=t("features_chart_return_axis", lang=lang),
                          margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with f2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist_df.index, y=hist_df["Volatility"] * 100,
            mode="lines", name=t("features_chart_vol_axis", lang=lang),
            line=dict(color="#EC4899", width=1.5),
        ))
        fig.update_layout(height=300, yaxis_title=t("features_chart_vol_axis", lang=lang),
                          margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with f3:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist_df.index, y=hist_df["Momentum"] * 100,
            mode="lines", name=t("features_chart_mom_axis", lang=lang),
            line=dict(color="#14B8A6", width=1.5),
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.update_layout(height=300, yaxis_title=t("features_chart_mom_axis", lang=lang),
                          margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Markov Transition Heatmap + Persistence Table
# ─────────────────────────────────────────────────────────────────────────────

def render_markov(results: Dict[str, Any], lang: str) -> None:
    st.markdown("---")
    st.markdown(t("markov_section_title", lang=lang))
    col_mat, col_pers = st.columns([1.2, 1.0])

    with col_mat:
        tm = results["transition_matrix"]
        fig = go.Figure(data=go.Heatmap(
            z=tm.values * 100,
            x=[translate_regime(c, lang=lang) for c in tm.columns],
            y=[translate_regime(i, lang=lang) for i in tm.index],
            colorscale="Blues",
            text=[[f"{v*100:.1f}%" for v in row] for row in tm.values],
            texttemplate="%{text}",
            hoverongaps=False,
        ))
        fig.update_layout(
            title=t("markov_heatmap_title", lang=lang),
            xaxis_title=t("markov_next_day_axis", lang=lang),
            yaxis_title=t("markov_current_day_axis", lang=lang),
            height=320, margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_pers:
        st.markdown(t("markov_persistence_title", lang=lang))
        pers = results["persistence_stats"]
        rows = [
            {
                t("table_col_regime", lang=lang): translate_regime(reg, lang=lang),
                t("table_col_self_prob", lang=lang): f"{vals['self_transition_prob']}%",
                t("table_col_exp_duration", lang=lang): f"{vals['expected_duration_days']} {t('days_suffix', lang=lang)}",
            }
            for reg, vals in pers.items()
        ]
        st.markdown(t("markov_expected_holding", lang=lang), unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption(t("markov_caption", lang=lang))


# ─────────────────────────────────────────────────────────────────────────────
# 6. Power BI / Excel CSV Export
# ─────────────────────────────────────────────────────────────────────────────

def render_export(
    results: Dict[str, Any], lang: str, coin_ticker: str,
    selected_fiat: str, full_ticker: str,
) -> None:
    st.markdown("---")
    st.markdown(t("export_section_title", lang=lang))
    st.markdown(t("export_description", lang=lang))

    export_df = results["df_history"].copy().reset_index()
    export_df["Asset"] = coin_ticker
    export_df["Currency"] = selected_fiat
    export_df["Suggested_Position"] = export_df["Market_Regime"].map({
        "Moderate-Volatility Bullish": 1.0,
        "Low-Volatility Neutral":      1.0,
        "High-Volatility Transition":  0.5,
        "High-Volatility Bearish":     0.0,
    })

    st.download_button(
        label=t("export_button", lang=lang, ticker=full_ticker),
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name=f"{full_ticker.lower()}_regime_analysis_powerbi.csv",
        mime="text/csv",
        type="secondary",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

def render_tab_analysis(
    results: Dict[str, Any],
    lang: str,
    selected_fiat: str,
    fiat_symbol: str,
    full_ticker: str,
    coin_ticker: str,
) -> None:
    """Render the full Live Market Regime Analysis tab."""
    render_metrics(results, lang, selected_fiat, fiat_symbol)
    st.markdown("---")
    render_recommendation(results, lang, full_ticker)
    render_price_chart(results, lang, full_ticker, selected_fiat)
    render_features(results, lang)
    render_markov(results, lang)
    render_export(results, lang, coin_ticker, selected_fiat, full_ticker)
