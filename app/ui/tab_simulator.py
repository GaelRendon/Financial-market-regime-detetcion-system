"""
Tab 2 — Optional 7-Day Money Growth Simulator.

Sections:
  1. Description + mandatory disclaimer banner
  2. Capital input + run button
  3. Summary metrics (Starting Capital, Expected Capital, P&L, Confidence Corridor)
  4. 7-Day forward trajectory chart (Monte Carlo corridors)
  5. Day-by-day forecast breakdown table + CSV download
"""

from __future__ import annotations
from typing import Any, Dict

import streamlit as st
import plotly.graph_objects as go

from src.inference import RegimeInferenceEngine
from src.utils.translations import t, translate_regime


def render_tab_simulator(
    results: Dict[str, Any],
    lang: str,
    coin_ticker: str,
    selected_fiat: str,
    fiat_symbol: str,
    full_ticker: str,
) -> None:
    """Render the full 7-Day Money Growth Simulator tab."""

    st.markdown(t("sim_title", lang=lang))
    st.markdown(t("sim_description", lang=lang, coin=coin_ticker, fiat=selected_fiat))

    # ── Disclaimer banner ────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background-color:#FEF3C7; border-left:6px solid #D97706;
                padding:18px 22px; border-radius:8px;
                margin-top:10px; margin-bottom:25px;">
        <div style="font-size:1.15rem; font-weight:800; color:#92400E; margin-bottom:6px;">
            {t('sim_disclaimer_title', lang=lang)}
        </div>
        <div style="font-size:0.95rem; color:#78350F; line-height:1.5;">
            {t('sim_disclaimer_body', lang=lang)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Capital input + run button ───────────────────────────────────────────
    col_input, col_btn = st.columns([1.5, 1.0])
    with col_input:
        default_capital = 10_000.0 if selected_fiat == "MXN" else 1_000.0
        user_capital = st.number_input(
            t("sim_input_capital", lang=lang, fiat=selected_fiat, symbol=fiat_symbol),
            min_value=1.0,
            max_value=100_000_000.0,
            value=default_capital,
            step=100.0,
            format="%.2f",
        )
    with col_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        run_sim = st.button(t("sim_button", lang=lang), type="primary", use_container_width=True)

    # ── Run / cache simulation ───────────────────────────────────────────────
    needs_rerun = (
        run_sim
        or "sim_result" not in st.session_state
        or st.session_state.get("sim_ticker") != full_ticker
        or st.session_state.get("sim_capital") != user_capital
    )
    if needs_rerun:
        engine = RegimeInferenceEngine()
        sim_res = engine.simulate_forward_trajectory(
            analysis_result=results,
            initial_capital=user_capital,
            horizon_days=7,
            n_simulations=1_000,
        )
        st.session_state["sim_result"]  = sim_res
        st.session_state["sim_ticker"]  = full_ticker
        st.session_state["sim_capital"] = user_capital

    sim = st.session_state.get("sim_result")
    if not sim:
        return

    st.markdown("---")

    # ── Summary metrics ──────────────────────────────────────────────────────
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric(t("sim_starting_capital", lang=lang),
                  f"{fiat_symbol}{sim['initial_capital']:,.2f}")
    with s2:
        st.metric(t("sim_expected_capital", lang=lang),
                  f"{fiat_symbol}{sim['final_expected_capital']:,.2f}",
                  delta=f"{sim['final_pct_return']:+.2f}%")
    with s3:
        st.metric(t("sim_projected_pnl", lang=lang),
                  f"{fiat_symbol}{sim['final_net_profit']:+,.2f}",
                  delta=f"{sim['final_pct_return']:+.2f}%")
    with s4:
        st.metric(
            t("sim_confidence_corridor", lang=lang),
            f"{fiat_symbol}{sim['lower_bound_10th']:,.0f} – {fiat_symbol}{sim['upper_bound_90th']:,.0f}",
            help=t("sim_confidence_corridor_help", lang=lang),
        )

    # ── 7-Day trajectory chart ───────────────────────────────────────────────
    st.markdown(f"#### 📈 {t('sim_title', lang=lang).replace('### 🔮 ', '')}")
    dates_list = sim["dates"]
    corridors  = sim["corridors"]

    fig = go.Figure()

    # 80 % confidence band (10th–90th)
    fig.add_trace(go.Scatter(
        x=dates_list + dates_list[::-1],
        y=corridors["p90"] + corridors["p10"][::-1],
        fill="toself", fillcolor="rgba(37,99,235,0.12)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip", showlegend=True,
        name=t("sim_legend_80ci", lang=lang),
    ))
    # 50 % interquartile band (25th–75th)
    fig.add_trace(go.Scatter(
        x=dates_list + dates_list[::-1],
        y=corridors["p75"] + corridors["p25"][::-1],
        fill="toself", fillcolor="rgba(37,99,235,0.22)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip", showlegend=True,
        name=t("sim_legend_50ci", lang=lang),
    ))
    # Mean trajectory
    fig.add_trace(go.Scatter(
        x=dates_list, y=corridors["mean"],
        mode="lines+markers",
        name=t("sim_legend_mean", lang=lang),
        line=dict(color="#1D4ED8", width=3), marker=dict(size=6),
    ))
    # Median trajectory
    fig.add_trace(go.Scatter(
        x=dates_list, y=corridors["p50"],
        mode="lines",
        name=t("sim_legend_median", lang=lang),
        line=dict(color="#10B981", width=2, dash="dot"),
    ))
    # Initial capital baseline
    fig.add_hline(
        y=user_capital, line_dash="dash", line_color="#94A3B8",
        annotation_text=t("sim_initial_baseline", lang=lang,
                           symbol=fiat_symbol, capital=user_capital),
        annotation_position="bottom right",
    )

    fig.update_layout(
        title=t("sim_chart_title", lang=lang, symbol=fiat_symbol,
                 capital=user_capital, ticker=full_ticker),
        xaxis_title=t("sim_chart_date_axis", lang=lang),
        yaxis_title=t("sim_chart_balance_axis", lang=lang, fiat=selected_fiat),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=420,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Day-by-day breakdown table ───────────────────────────────────────────
    st.markdown(t("sim_table_title", lang=lang))
    is_24_7 = sim.get("is_24_7", results.get("is_24_7", True))
    note_key = "sim_table_crypto_note" if is_24_7 else "sim_table_trading_note"
    st.markdown(
        f"<div style='font-size:0.88rem; color:#64748B; margin-bottom:8px;'>"
        f"{t(note_key, lang=lang)}</div>",
        unsafe_allow_html=True,
    )

    b_df = sim["breakdown_df"].copy()
    b_display = b_df.copy()

    b_display["Projected Capital"]     = b_display["Projected Capital"].apply(lambda v: f"{fiat_symbol}{v:,.2f}")
    b_display["Lower Bound (10th)"]    = b_display["Lower Bound (10th)"].apply(lambda v: f"{fiat_symbol}{v:,.2f}")
    b_display["Upper Bound (90th)"]    = b_display["Upper Bound (90th)"].apply(lambda v: f"{fiat_symbol}{v:,.2f}")
    b_display["Cumulative P&L"]        = b_display["Cumulative P&L"].apply(lambda v: f"{fiat_symbol}{v:+,.2f}")
    b_display["Exp. Daily Return (%)"] = b_display["Exp. Daily Return (%)"].apply(lambda v: f"{v:+.2f}%")
    b_display["Cumulative Return (%)"] = b_display["Cumulative Return (%)"].apply(lambda v: f"{v:+.2f}%")
    b_display["Confidence (%)"]        = b_display["Confidence (%)"].apply(lambda v: f"{v:.1f}%")
    b_display["Predicted_Regime"]      = b_display["Predicted_Regime"].apply(lambda r: translate_regime(r, lang=lang))

    b_display = b_display.rename(columns={
        "Day":                   t("col_day",        lang=lang),
        "Date":                  t("col_date",       lang=lang),
        "Predicted_Regime":      t("col_pred_regime",lang=lang),
        "Confidence (%)":        t("col_confidence", lang=lang),
        "Exp. Daily Return (%)": t("col_daily_ret",  lang=lang),
        "Projected Capital":     t("col_proj_cap",   lang=lang),
        "Lower Bound (10th)":    t("col_lower_10",   lang=lang),
        "Upper Bound (90th)":    t("col_upper_90",   lang=lang),
        "Cumulative P&L":        t("col_cum_pnl",    lang=lang),
        "Cumulative Return (%)": t("col_cum_ret",    lang=lang),
    })
    st.dataframe(b_display, use_container_width=True, hide_index=True)

    # CSV download
    st.download_button(
        label=t("sim_download_button", lang=lang, fiat=selected_fiat),
        data=b_df.to_csv(index=False).encode("utf-8"),
        file_name=f"{full_ticker.lower()}_7day_simulation_{selected_fiat.lower()}.csv",
        mime="text/csv",
        type="secondary",
    )
