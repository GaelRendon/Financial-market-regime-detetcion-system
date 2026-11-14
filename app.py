"""
Streamlit Web Application: Financial Market Regime Detection System.
Interactive quantitative dashboard for live multi-asset & multi-currency regime forecasting
with an optional 7-Day Money Growth Simulator, Power BI export capabilities, and multi-language (i18n) support.
"""

import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

import importlib
import src.inference
import src.utils.translations
import src.utils.assets
importlib.reload(src.inference)
importlib.reload(src.utils.translations)
importlib.reload(src.utils.assets)

from src.inference import RegimeInferenceEngine
from src.utils.translations import (
    t,
    translate_regime,
    translate_action,
    translate_risk_level,
    translate_rationale,
    SUPPORTED_LANGUAGES
)
from src.utils.assets import (
    get_search_options,
    extract_symbol_from_choice,
    get_directory_dataframe
)

# Page configuration
st.set_page_config(
    page_title="Market Regime Detection System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        color: #1E293B;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .action-box {
        border-radius: 12px;
        padding: 22px;
        margin-top: 10px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .action-box-green {
        background-color: #ECFDF5;
        border-left: 8px solid #10B981;
    }
    .action-box-blue {
        background-color: #EFF6FF;
        border-left: 8px solid #3B82F6;
    }
    .action-box-orange {
        background-color: #FFFBEB;
        border-left: 8px solid #F59E0B;
    }
    .action-box-red {
        background-color: #FEF2F2;
        border-left: 8px solid #EF4444;
    }
    .action-title {
        font-size: 1.4rem;
        font-weight: 800;
        margin-bottom: 6px;
    }
    /* Metric Card Enhancements & Anti-Truncation Pop-out */
    div[data-testid="stMetric"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 14px;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.08);
        border-color: #CBD5E1;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.30rem !important;
        white-space: normal !important;
        word-break: normal !important;
        line-height: 1.25 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
    }
    /* Top-Right Language Popover Pill Styling */
    div[data-testid="stPopover"] button {
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #F8FAFC !important;
        color: #1E293B !important;
        font-size: 0.90rem !important;
        padding: 5px 12px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stPopover"] button:hover {
        border-color: #3B82F6 !important;
        color: #1D4ED8 !important;
        background-color: #EFF6FF !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Currency symbol helper
CURRENCY_SYMBOLS = {
    "USD": "$",
    "MXN": "$",
    "EUR": "€",
    "GBP": "£",
    "CAD": "$"
}

def format_crypto_price(value: float, symbol: str = "$") -> str:
    """Format asset price with adaptive precision so sub-dollar and micro-cap coins don't display $0.00."""
    abs_val = abs(value)
    if abs_val >= 1.0:
        return f"{symbol}{value:,.2f}"
    elif abs_val >= 0.01:
        return f"{symbol}{value:,.4f}"
    elif abs_val >= 0.0001:
        return f"{symbol}{value:,.6f}"
    elif abs_val > 0:
        return f"{symbol}{value:,.8f}"
    else:
        return f"{symbol}0.00"

# Initialize Language in session state
if "app_language" not in st.session_state:
    st.session_state["app_language"] = "en"
lang = st.session_state["app_language"]

# ==========================================
# SIDEBAR: ASSET CONFIGURATION
# ==========================================
st.sidebar.title(t("sidebar_title", lang=lang))
st.sidebar.markdown(t("sidebar_subtitle", lang=lang))

# Intelligent Typeahead Search Selector (Phase 2)
search_options = get_search_options(lang=lang)
selected_search_choice = st.sidebar.selectbox(
    t("search_asset_label", lang=lang),
    search_options,
    index=0,
    help=t("search_asset_help", lang=lang)
)

extracted_sym = extract_symbol_from_choice(selected_search_choice)
if extracted_sym is None:
    # Custom Ticker mode
    coin_ticker = st.sidebar.text_input(
        t("custom_ticker_prompt", lang=lang),
        value=st.session_state.get("custom_ticker_val", "NVDA")
    ).upper().strip()
    st.session_state["custom_ticker_val"] = coin_ticker
else:
    coin_ticker = extracted_sym

# Collapsible Directory & Cheat Sheet (Phase 2)
with st.sidebar.expander(t("directory_expander_title", lang=lang), expanded=False):
    st.caption(t("directory_caption", lang=lang))
    dir_df = get_directory_dataframe(lang=lang)
    st.dataframe(dir_df, use_container_width=True, hide_index=True)

selected_fiat = st.sidebar.selectbox(t("fiat_currency_label", lang=lang), ["USD", "MXN", "EUR", "GBP", "CAD"], index=0)
fiat_symbol = CURRENCY_SYMBOLS.get(selected_fiat, "$")

full_ticker = f"{coin_ticker}-{selected_fiat}"

horizon_map = {
    t("horizon_1y", lang=lang): "1y",
    t("horizon_2y", lang=lang): "2y",
    t("horizon_3y", lang=lang): "3y",
    t("horizon_5y", lang=lang): "5y",
    t("horizon_max", lang=lang): "max"
}

horizon_labels = list(horizon_map.keys())
selected_horizon_label = st.sidebar.selectbox(t("lookback_window_label", lang=lang), horizon_labels, index=2)
selected_period = horizon_map[selected_horizon_label]

st.sidebar.markdown("---")
st.sidebar.markdown(f"### {t('about_model_title', lang=lang)}")
st.sidebar.caption(t("about_model_caption", lang=lang))

run_button = st.sidebar.button(t("run_button", lang=lang), type="primary", use_container_width=True)

# Top Header Bar: Title on Left, Language Popover Pill on Top-Right
col_header, col_lang = st.columns([0.88, 0.12])
with col_header:
    st.markdown(f"<div class='main-header'>{t('main_header', lang=lang)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-header'>{t('sub_header', lang=lang, ticker=full_ticker)}</div>", unsafe_allow_html=True)

with col_lang:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    with st.popover(f"🌐 {lang.upper()}", use_container_width=True):
        st.caption(f"**{t('sidebar_language', lang=lang)}**")
        current_option = SUPPORTED_LANGUAGES.get(lang, "EN (English)")
        lang_options = list(SUPPORTED_LANGUAGES.values())
        
        selected_option = st.radio(
            "Select language:",
            lang_options,
            index=lang_options.index(current_option) if current_option in lang_options else 0,
            label_visibility="collapsed"
        )
        
        new_lang = "en" if selected_option.startswith("EN") else "es"
        if new_lang != lang:
            st.session_state["app_language"] = new_lang
            st.rerun()

# Run Inference Engine
if (
    run_button 
    or "inference_results" not in st.session_state 
    or st.session_state.get("last_ticker") != full_ticker
    or st.session_state.get("last_period") != selected_period
):
    with st.spinner(t("spinner_fetching", lang=lang, ticker=full_ticker)):
        try:
            engine = RegimeInferenceEngine()
            results = engine.analyze_ticker(full_ticker, period=selected_period, force_refresh=run_button)
            st.session_state["inference_results"] = results
            st.session_state["last_ticker"] = full_ticker
            st.session_state["last_period"] = selected_period
        except Exception as e:
            st.error(t("ticker_error_friendly", lang=lang, ticker=full_ticker))
            st.caption(f"Technical detail: {str(e)}")
            st.stop()

results = st.session_state.get("inference_results")

if results:
    # Top-Level Tabs: Analysis & Optional 7-Day Money Growth Simulator
    tab_analysis, tab_simulator = st.tabs([
        t("tab_analysis", lang=lang),
        t("tab_simulator", lang=lang)
    ])

    with tab_analysis:
        # 1. Top Metrics Banner
        m1, m2, m3, m4, m5 = st.columns([1.3, 1.5, 1.1, 0.9, 0.9])
        translated_curr_regime = translate_regime(results["current_regime"], lang=lang)

        with m1:
            st.metric(
                label=t("metric_current_price", lang=lang, fiat=selected_fiat),
                value=format_crypto_price(results['latest_close'], fiat_symbol),
                delta=f"{results['change_24h_pct']:+.2f}% (24h)",
                help=t("metric_current_price_help", lang=lang, fiat=selected_fiat)
            )
        with m2:
            st.metric(
                label=t("metric_current_regime", lang=lang),
                value=translated_curr_regime,
                help=t("metric_current_regime_help", lang=lang, regime=translated_curr_regime)
            )
        with m3:
            st.metric(
                label=t("metric_persistence", lang=lang),
                value=f"{results['regime_streak_days']} {t('days_suffix', lang=lang)}",
                help=t("metric_persistence_help", lang=lang)
            )
        with m4:
            st.metric(
                label=t("metric_volatility", lang=lang),
                value=f"{results['current_volatility_pct']:.2f}%"
            )
        with m5:
            st.metric(
                label=t("metric_momentum", lang=lang),
                value=f"{results['current_momentum_pct']:+.2f}%"
            )

        st.markdown("---")

        # 2. Hero Recommendation Banner & Forecast Probabilities
        rec = results["recommendation"]
        badge_color = rec["badge_color"]
        css_class = f"action-box action-box-{badge_color}"

        translated_forecast_regime = translate_regime(results["forecast_regime"], lang=lang)
        translated_action = translate_action(rec["action"], lang=lang)
        translated_risk_level = translate_risk_level(rec["risk_level"], lang=lang)
        translated_rationale = translate_rationale(results["forecast_regime"], lang=lang, default_text=rec["rationale"])

        col_action, col_prob = st.columns([1.2, 1.0])

        with col_action:
            action_color = "#047857" if badge_color=="green" else "#1D4ED8" if badge_color=="blue" else "#B45309" if badge_color=="orange" else "#B91C1C"
            exposure_text = t("exposure_suffix", lang=lang, pct=int(rec['position']*100))
            
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
            # Translate regime names in the probability chart
            prob_records = [
                {"Regime": translate_regime(r, lang=lang), "RawRegime": r, "Probability": p}
                for r, p in probs.items()
            ]
            prob_df = pd.DataFrame(prob_records).sort_values(by="Probability", ascending=True)

            fig_prob = go.Figure()
            colors = {
                "Moderate-Volatility Bullish": "#10B981",
                "Low-Volatility Neutral": "#3B82F6",
                "High-Volatility Transition": "#F59E0B",
                "High-Volatility Bearish": "#EF4444"
            }
            bar_colors = [colors.get(r, "#64748B") for r in prob_df["RawRegime"]]

            fig_prob.add_trace(go.Bar(
                y=prob_df["Regime"],
                x=prob_df["Probability"] * 100,
                orientation="h",
                marker=dict(color=bar_colors),
                text=[f"{p*100:.1f}%" for p in prob_df["Probability"]],
                textposition="auto"
            ))
            fig_prob.update_layout(
                title=t("chart_forecast_confidence_title", lang=lang, ticker=full_ticker),
                xaxis_title=t("chart_probability_axis", lang=lang),
                yaxis_title="",
                margin=dict(l=10, r=10, t=40, b=10),
                height=260
            )
            st.plotly_chart(fig_prob, use_container_width=True)

        # 3. Interactive Historical Regime Chart
        st.markdown(t("timeline_section_title", lang=lang))
        hist_df = results["df_history"]

        fig_price = go.Figure()

        regime_colors = {
            "Moderate-Volatility Bullish": "#10B981",
            "Low-Volatility Neutral": "#3B82F6",
            "High-Volatility Transition": "#F59E0B",
            "High-Volatility Bearish": "#EF4444"
        }

        for r_name, r_color in regime_colors.items():
            mask = hist_df["Market_Regime"] == r_name
            if mask.any():
                fig_price.add_trace(go.Scatter(
                    x=hist_df.index[mask],
                    y=hist_df["Close"][mask],
                    mode="markers",
                    name=translate_regime(r_name, lang=lang),
                    marker=dict(size=4, color=r_color)
                ))

        fig_price.add_trace(go.Scatter(
            x=hist_df.index,
            y=hist_df["Close"],
            mode="lines",
            name=t("timeline_close_price", lang=lang),
            line=dict(color="#94A3B8", width=1),
            opacity=0.7
        ))

        fig_price.update_layout(
            title=t("timeline_chart_title", lang=lang, ticker=full_ticker),
            xaxis_title=t("timeline_chart_date", lang=lang),
            yaxis_title=t("timeline_chart_price", lang=lang, fiat=selected_fiat),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=450,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_price, use_container_width=True)

        # 4. Feature Decomposition Tabs
        st.markdown(t("features_section_title", lang=lang))
        f_tab1, f_tab2, f_tab3 = st.tabs([
            t("features_tab_returns", lang=lang),
            t("features_tab_volatility", lang=lang),
            t("features_tab_momentum", lang=lang)
        ])

        with f_tab1:
            fig_ret = go.Figure()
            fig_ret.add_trace(go.Scatter(
                x=hist_df.index,
                y=hist_df["Returns"] * 100,
                mode="lines",
                name=t("features_chart_return_axis", lang=lang),
                line=dict(color="#6366F1", width=1)
            ))
            fig_ret.add_hline(y=0, line_dash="dash", line_color="gray")
            fig_ret.update_layout(height=300, yaxis_title=t("features_chart_return_axis", lang=lang), margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_ret, use_container_width=True)

        with f_tab2:
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Scatter(
                x=hist_df.index,
                y=hist_df["Volatility"] * 100,
                mode="lines",
                name=t("features_chart_vol_axis", lang=lang),
                line=dict(color="#EC4899", width=1.5)
            ))
            fig_vol.update_layout(height=300, yaxis_title=t("features_chart_vol_axis", lang=lang), margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_vol, use_container_width=True)

        with f_tab3:
            fig_mom = go.Figure()
            fig_mom.add_trace(go.Scatter(
                x=hist_df.index,
                y=hist_df["Momentum"] * 100,
                mode="lines",
                name=t("features_chart_mom_axis", lang=lang),
                line=dict(color="#14B8A6", width=1.5)
            ))
            fig_mom.add_hline(y=0, line_dash="dash", line_color="gray")
            fig_mom.update_layout(height=300, yaxis_title=t("features_chart_mom_axis", lang=lang), margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_mom, use_container_width=True)

        # 5. Markov Transition Analysis
        st.markdown("---")
        st.markdown(t("markov_section_title", lang=lang))
        col_mat, col_pers = st.columns([1.2, 1.0])

        with col_mat:
            tm = results["transition_matrix"]
            translated_cols = [translate_regime(c, lang=lang) for c in tm.columns]
            translated_index = [translate_regime(i, lang=lang) for i in tm.index]

            fig_tm = go.Figure(data=go.Heatmap(
                z=tm.values * 100,
                x=translated_cols,
                y=translated_index,
                colorscale="Blues",
                text=[[f"{val*100:.1f}%" for val in row] for row in tm.values],
                texttemplate="%{text}",
                hoverongaps=False
            ))
            fig_tm.update_layout(
                title=t("markov_heatmap_title", lang=lang),
                xaxis_title=t("markov_next_day_axis", lang=lang),
                yaxis_title=t("markov_current_day_axis", lang=lang),
                height=320,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_tm, use_container_width=True)

        with col_pers:
            st.markdown(t("markov_persistence_title", lang=lang))
            pers = results["persistence_stats"]
            pers_rows = []
            for reg, vals in pers.items():
                pers_rows.append({
                    t("table_col_regime", lang=lang): translate_regime(reg, lang=lang),
                    t("table_col_self_prob", lang=lang): f"{vals['self_transition_prob']}%",
                    t("table_col_exp_duration", lang=lang): f"{vals['expected_duration_days']} {t('days_suffix', lang=lang)}"
                })
            pers_table = pd.DataFrame(pers_rows)
            st.markdown(t("markov_expected_holding", lang=lang), unsafe_allow_html=True)
            st.dataframe(pers_table, use_container_width=True, hide_index=True)
            st.caption(t("markov_caption", lang=lang))

        # 6. Power BI & Excel Export
        st.markdown("---")
        st.markdown(t("export_section_title", lang=lang))
        st.markdown(t("export_description", lang=lang))

        export_df = hist_df.copy().reset_index()
        export_df["Asset"] = coin_ticker
        export_df["Currency"] = selected_fiat
        export_df["Suggested_Position"] = export_df["Market_Regime"].map({
            "Moderate-Volatility Bullish": 1.0,
            "Low-Volatility Neutral": 1.0,
            "High-Volatility Transition": 0.5,
            "High-Volatility Bearish": 0.0
        })

        csv_data = export_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label=t("export_button", lang=lang, ticker=full_ticker),
            data=csv_data,
            file_name=f"{full_ticker.lower()}_regime_analysis_powerbi.csv",
            mime="text/csv",
            type="secondary"
        )

    # ==========================================
    # TAB 2: OPTIONAL 7-DAY MONEY GROWTH SIMULATOR
    # ==========================================
    with tab_simulator:
        st.markdown(t("sim_title", lang=lang))
        st.markdown(t("sim_description", lang=lang, coin=coin_ticker, fiat=selected_fiat))

        # Prominent Mandatory Disclaimer Banner
        st.markdown(f"""
        <div style="background-color: #FEF3C7; border-left: 6px solid #D97706; padding: 18px 22px; border-radius: 8px; margin-top: 10px; margin-bottom: 25px;">
            <div style="font-size: 1.15rem; font-weight: 800; color: #92400E; margin-bottom: 6px;">
                {t('sim_disclaimer_title', lang=lang)}
            </div>
            <div style="font-size: 0.95rem; color: #78350F; line-height: 1.5;">
                {t('sim_disclaimer_body', lang=lang)}
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_input1, col_input2 = st.columns([1.5, 1.0])
        with col_input1:
            default_capital = 10000.0 if selected_fiat == "MXN" else 1000.0
            user_capital = st.number_input(
                t("sim_input_capital", lang=lang, fiat=selected_fiat, symbol=fiat_symbol),
                min_value=1.0,
                max_value=100000000.0,
                value=default_capital,
                step=100.0,
                format="%.2f"
            )

        with col_input2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            run_sim = st.button(t("sim_button", lang=lang), type="primary", use_container_width=True)

        # Simulation execution
        if run_sim or "sim_result" not in st.session_state or st.session_state.get("sim_ticker") != full_ticker or st.session_state.get("sim_capital") != user_capital:
            engine = RegimeInferenceEngine()
            sim_res = engine.simulate_forward_trajectory(
                analysis_result=results,
                initial_capital=user_capital,
                horizon_days=7,
                n_simulations=1000
            )
            st.session_state["sim_result"] = sim_res
            st.session_state["sim_ticker"] = full_ticker
            st.session_state["sim_capital"] = user_capital

        sim = st.session_state.get("sim_result")

        if sim:
            st.markdown("---")
            # 1. High-level Summary Metrics
            s1, s2, s3, s4 = st.columns(4)
            with s1:
                st.metric(
                    label=t("sim_starting_capital", lang=lang),
                    value=f"{fiat_symbol}{sim['initial_capital']:,.2f}"
                )
            with s2:
                st.metric(
                    label=t("sim_expected_capital", lang=lang),
                    value=f"{fiat_symbol}{sim['final_expected_capital']:,.2f}",
                    delta=f"{sim['final_pct_return']:+.2f}%"
                )
            with s3:
                st.metric(
                    label=t("sim_projected_pnl", lang=lang),
                    value=f"{fiat_symbol}{sim['final_net_profit']:+,.2f}",
                    delta=f"{sim['final_pct_return']:+.2f}%"
                )
            with s4:
                st.metric(
                    label=t("sim_confidence_corridor", lang=lang),
                    value=f"{fiat_symbol}{sim['lower_bound_10th']:,.0f} - {fiat_symbol}{sim['upper_bound_90th']:,.0f}",
                    help=t("sim_confidence_corridor_help", lang=lang)
                )

            # 2. 7-Day Forward Trajectory Chart
            st.markdown(f"#### 📈 {t('sim_title', lang=lang).replace('### 🔮 ', '')}")
            dates_list = sim["dates"]
            corridors = sim["corridors"]

            fig_sim = go.Figure()

            # Shaded 10th to 90th percentile corridor
            fig_sim.add_trace(go.Scatter(
                x=dates_list + dates_list[::-1],
                y=corridors["p90"] + corridors["p10"][::-1],
                fill="toself",
                fillcolor="rgba(37, 99, 235, 0.12)",
                line=dict(color="rgba(255, 255, 255, 0)"),
                hoverinfo="skip",
                showlegend=True,
                name=t("sim_legend_80ci", lang=lang)
            ))

            # Shaded 25th to 75th percentile corridor (interquartile range)
            fig_sim.add_trace(go.Scatter(
                x=dates_list + dates_list[::-1],
                y=corridors["p75"] + corridors["p25"][::-1],
                fill="toself",
                fillcolor="rgba(37, 99, 235, 0.22)",
                line=dict(color="rgba(255, 255, 255, 0)"),
                hoverinfo="skip",
                showlegend=True,
                name=t("sim_legend_50ci", lang=lang)
            ))

            # Expected (Mean) Trajectory
            fig_sim.add_trace(go.Scatter(
                x=dates_list,
                y=corridors["mean"],
                mode="lines+markers",
                name=t("sim_legend_mean", lang=lang),
                line=dict(color="#1D4ED8", width=3),
                marker=dict(size=6)
            ))

            # Median Trajectory
            fig_sim.add_trace(go.Scatter(
                x=dates_list,
                y=corridors["p50"],
                mode="lines",
                name=t("sim_legend_median", lang=lang),
                line=dict(color="#10B981", width=2, dash="dot")
            ))

            # Initial Capital Baseline
            fig_sim.add_hline(
                y=user_capital,
                line_dash="dash",
                line_color="#94A3B8",
                annotation_text=f"{t('sim_initial_baseline', lang=lang, symbol=fiat_symbol, capital=user_capital)}",
                annotation_position="bottom right"
            )

            fig_sim.update_layout(
                title=t("sim_chart_title", lang=lang, symbol=fiat_symbol, capital=user_capital, ticker=full_ticker),
                xaxis_title=t("sim_chart_date_axis", lang=lang),
                yaxis_title=t("sim_chart_balance_axis", lang=lang, fiat=selected_fiat),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=420,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_sim, use_container_width=True)

            # 3. Day-by-Day Forecast Breakdown Table
            st.markdown(t("sim_table_title", lang=lang))
            b_df = sim["breakdown_df"].copy()
            
            b_display = b_df.copy()
            b_display["Projected Capital"] = b_display["Projected Capital"].apply(lambda v: f"{fiat_symbol}{v:,.2f}")
            b_display["Lower Bound (10th)"] = b_display["Lower Bound (10th)"].apply(lambda v: f"{fiat_symbol}{v:,.2f}")
            b_display["Upper Bound (90th)"] = b_display["Upper Bound (90th)"].apply(lambda v: f"{fiat_symbol}{v:,.2f}")
            b_display["Cumulative P&L"] = b_display["Cumulative P&L"].apply(lambda v: f"{fiat_symbol}{v:+,.2f}")
            b_display["Exp. Daily Return (%)"] = b_display["Exp. Daily Return (%)"].apply(lambda v: f"{v:+.2f}%")
            b_display["Cumulative Return (%)"] = b_display["Cumulative Return (%)"].apply(lambda v: f"{v:+.2f}%")
            b_display["Confidence (%)"] = b_display["Confidence (%)"].apply(lambda v: f"{v:.1f}%")
            b_display["Predicted_Regime"] = b_display["Predicted_Regime"].apply(lambda r: translate_regime(r, lang=lang))

            # Translate table headers
            b_display = b_display.rename(columns={
                "Day": t("col_day", lang=lang),
                "Date": t("col_date", lang=lang),
                "Predicted_Regime": t("col_pred_regime", lang=lang),
                "Confidence (%)": t("col_confidence", lang=lang),
                "Exp. Daily Return (%)": t("col_daily_ret", lang=lang),
                "Projected Capital": t("col_proj_cap", lang=lang),
                "Lower Bound (10th)": t("col_lower_10", lang=lang),
                "Upper Bound (90th)": t("col_upper_90", lang=lang),
                "Cumulative P&L": t("col_cum_pnl", lang=lang),
                "Cumulative Return (%)": t("col_cum_ret", lang=lang)
            })

            st.dataframe(b_display, use_container_width=True, hide_index=True)

            # 4. CSV Download for Simulation
            sim_csv = b_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=t("sim_download_button", lang=lang, fiat=selected_fiat),
                data=sim_csv,
                file_name=f"{full_ticker.lower()}_7day_simulation_{selected_fiat.lower()}.csv",
                mime="text/csv",
                type="secondary"
            )
