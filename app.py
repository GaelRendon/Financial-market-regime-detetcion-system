"""
Streamlit Web Application: Financial Market Regime Detection System.
Interactive quantitative dashboard for live multi-asset & multi-currency regime forecasting
with an optional 7-Day Money Growth Simulator and Power BI export capabilities.
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

from src.inference import RegimeInferenceEngine

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
</style>
""", unsafe_allow_html=True)

# Currency symbol helper
CURRENCY_SYMBOLS = {
    "USD": "$",
    "MXN": "Mex$",
    "EUR": "€",
    "GBP": "£",
    "CAD": "CA$"
}

def format_crypto_price(value: float, symbol: str = "$") -> str:
    """Format crypto price with adaptive precision so sub-dollar and micro-cap coins don't display $0.00."""
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

# Sidebar inputs
st.sidebar.title("⚙️ Asset & Horizon")
st.sidebar.markdown("Configure target cryptocurrency and denomination fiat:")

popular_coins = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "Custom"]
selected_coin = st.sidebar.selectbox("Cryptocurrency", popular_coins, index=0)

if selected_coin == "Custom":
    coin_ticker = st.sidebar.text_input("Enter Coin Symbol (e.g. AVAX, LINK)", "AVAX").upper().strip()
else:
    coin_ticker = selected_coin

selected_fiat = st.sidebar.selectbox("Fiat Currency", ["USD", "MXN", "EUR", "GBP", "CAD"], index=0)
fiat_symbol = CURRENCY_SYMBOLS.get(selected_fiat, "$")

full_ticker = f"{coin_ticker}-{selected_fiat}"

horizon_options = {
    "1 Year": "1y",
    "2 Years": "2y",
    "3 Years": "3y",
    "5 Years": "5y",
    "Maximum Available": "max"
}
selected_horizon_label = st.sidebar.selectbox("Historical Lookback Window", list(horizon_options.keys()), index=2)
selected_period = horizon_options[selected_horizon_label]

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About the Model")
st.sidebar.caption(
    "This system applies **StandardScaler + PCA (95% variance)** to reduce Returns, 30d Volatility, "
    "and 14d Momentum into orthogonal components, partitions states with **K-Means (K=4)**, "
    "models transition persistence with **Markov Chains**, and forecasts the next regime with **Random Forest**."
)

run_button = st.sidebar.button("🚀 Run Live Analysis", type="primary", use_container_width=True)

# App Header
st.markdown("<div class='main-header'>📈 Financial Market Regime Detection System</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-header'>Live quantitative regime identification, probabilistic forecasting, and automated risk allocation for <b>{full_ticker}</b></div>", unsafe_allow_html=True)

# Run Inference Engine
if run_button or "inference_results" not in st.session_state or st.session_state.get("last_ticker") != full_ticker:
    with st.spinner(f"Fetching market data for {full_ticker} and executing quantitative pipeline..."):
        try:
            engine = RegimeInferenceEngine()
            results = engine.analyze_ticker(full_ticker, period=selected_period)
            st.session_state["inference_results"] = results
            st.session_state["last_ticker"] = full_ticker
        except Exception as e:
            st.error(f"Error analyzing {full_ticker}: {str(e)}")
            st.stop()

results = st.session_state.get("inference_results")

if results:
    # Top-Level Tabs: Analysis & Optional 7-Day Money Growth Simulator
    tab_analysis, tab_simulator = st.tabs([
        "📊 Live Market Regime Analysis",
        "🔮 7-Day Money Growth Simulator (Optional)"
    ])

    with tab_analysis:
        # 1. Top Metrics Banner
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric(
                label=f"Current Price ({selected_fiat})",
                value=format_crypto_price(results['latest_close'], fiat_symbol),
                delta=f"{results['change_24h_pct']:+.2f}% (24h)"
            )
        with m2:
            st.metric(
                label="Current Regime",
                value=results["current_regime"]
            )
        with m3:
            st.metric(
                label="Regime Persistence",
                value=f"{results['regime_streak_days']} days active"
            )
        with m4:
            st.metric(
                label="30-Day Volatility",
                value=f"{results['current_volatility_pct']:.2f}%"
            )
        with m5:
            st.metric(
                label="14-Day Momentum",
                value=f"{results['current_momentum_pct']:+.2f}%"
            )

        st.markdown("---")

        # 2. Hero Recommendation Banner & Forecast Probabilities
        rec = results["recommendation"]
        badge_color = rec["badge_color"]
        css_class = f"action-box action-box-{badge_color}"

        col_action, col_prob = st.columns([1.2, 1.0])

        with col_action:
            st.markdown(f"""
            <div class='{css_class}'>
                <div style='font-size: 0.95rem; font-weight: 600; text-transform: uppercase; color: #475569;'>
                    Tomorrow's Forecasted Regime: <span style='font-weight: 800;'>{results['forecast_regime']}</span>
                </div>
                <div class='action-title' style='color: {"#047857" if badge_color=="green" else "#1D4ED8" if badge_color=="blue" else "#B45309" if badge_color=="orange" else "#B91C1C"};'>
                    🎯 SUGGESTION: {rec['action']} ({int(rec['position']*100)}% Exposure)
                </div>
                <div style='margin-bottom: 8px;'>
                    <b>Risk Level:</b> {rec['risk_level']}
                </div>
                <div style='font-size: 0.95rem; line-height: 1.5; color: #334155;'>
                    {rec['rationale']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_prob:
            probs = results["forecast_probabilities"]
            prob_df = pd.DataFrame(list(probs.items()), columns=["Regime", "Probability"]).sort_values(by="Probability", ascending=True)

            fig_prob = go.Figure()
            colors = {
                "Moderate-Volatility Bullish": "#10B981",
                "Low-Volatility Neutral": "#3B82F6",
                "High-Volatility Transition": "#F59E0B",
                "High-Volatility Bearish": "#EF4444"
            }
            bar_colors = [colors.get(r, "#64748B") for r in prob_df["Regime"]]

            fig_prob.add_trace(go.Bar(
                y=prob_df["Regime"],
                x=prob_df["Probability"] * 100,
                orientation="h",
                marker=dict(color=bar_colors),
                text=[f"{p*100:.1f}%" for p in prob_df["Probability"]],
                textposition="auto"
            ))
            fig_prob.update_layout(
                title=f"Forecast Confidence Distribution ({full_ticker})",
                xaxis_title="Probability (%)",
                yaxis_title="",
                margin=dict(l=10, r=10, t=40, b=10),
                height=260
            )
            st.plotly_chart(fig_prob, use_container_width=True)

        # 3. Interactive Historical Regime Chart
        st.markdown("### 📊 Historical Market Regime Timeline")
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
                    name=r_name,
                    marker=dict(size=4, color=r_color)
                ))

        fig_price.add_trace(go.Scatter(
            x=hist_df.index,
            y=hist_df["Close"],
            mode="lines",
            name="Close Price",
            line=dict(color="#94A3B8", width=1),
            opacity=0.7
        ))

        fig_price.update_layout(
            title=f"{full_ticker} Daily Price History with Detected Regimes",
            xaxis_title="Date",
            yaxis_title=f"Price ({selected_fiat})",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=450,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_price, use_container_width=True)

        # 4. Feature Decomposition Tabs
        st.markdown("### 🔍 Engineered Feature Dynamics")
        f_tab1, f_tab2, f_tab3 = st.tabs(["Daily Returns", "30-Day Volatility", "14-Day Momentum"])

        with f_tab1:
            fig_ret = go.Figure()
            fig_ret.add_trace(go.Scatter(
                x=hist_df.index,
                y=hist_df["Returns"] * 100,
                mode="lines",
                name="Daily Return (%)",
                line=dict(color="#6366F1", width=1)
            ))
            fig_ret.add_hline(y=0, line_dash="dash", line_color="gray")
            fig_ret.update_layout(height=300, yaxis_title="Daily Return (%)", margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_ret, use_container_width=True)

        with f_tab2:
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Scatter(
                x=hist_df.index,
                y=hist_df["Volatility"] * 100,
                mode="lines",
                name="30d Rolling Volatility (%)",
                line=dict(color="#EC4899", width=1.5)
            ))
            fig_vol.update_layout(height=300, yaxis_title="Volatility (%)", margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_vol, use_container_width=True)

        with f_tab3:
            fig_mom = go.Figure()
            fig_mom.add_trace(go.Scatter(
                x=hist_df.index,
                y=hist_df["Momentum"] * 100,
                mode="lines",
                name="14d Price Momentum (%)",
                line=dict(color="#14B8A6", width=1.5)
            ))
            fig_mom.add_hline(y=0, line_dash="dash", line_color="gray")
            fig_mom.update_layout(height=300, yaxis_title="Momentum (%)", margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_mom, use_container_width=True)

        # 5. Markov Transition Analysis
        st.markdown("---")
        st.markdown("### 🔄 Markov Regime Transition Dynamics")
        col_mat, col_pers = st.columns([1.2, 1.0])

        with col_mat:
            tm = results["transition_matrix"]
            fig_tm = go.Figure(data=go.Heatmap(
                z=tm.values * 100,
                x=tm.columns,
                y=tm.index,
                colorscale="Blues",
                text=[[f"{val*100:.1f}%" for val in row] for row in tm.values],
                texttemplate="%{text}",
                hoverongaps=False
            ))
            fig_tm.update_layout(
                title="Historical 1-Day Transition Probabilities (%)",
                xaxis_title="Next Day Regime (t+1)",
                yaxis_title="Current Regime (t)",
                height=320,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_tm, use_container_width=True)

        with col_pers:
            st.markdown("#### Regime Persistence")
            pers = results["persistence_stats"]
            pers_rows = []
            for reg, vals in pers.items():
                pers_rows.append({
                    "Regime": reg,
                    "Self-Transition Prob": f"{vals['self_transition_prob']}%",
                    "Expected Duration": f"{vals['expected_duration_days']} days"
                })
            pers_table = pd.DataFrame(pers_rows)
            st.markdown("<b>Expected Holding Duration:</b>", unsafe_allow_html=True)
            st.dataframe(pers_table, use_container_width=True, hide_index=True)
            st.caption("Expected duration indicates how many consecutive days the market typically remains inside that state before shifting.")

        # 6. Power BI & Excel Export
        st.markdown("---")
        st.markdown("### 📥 Export Dataset for Power BI / Excel")
        st.markdown(
            "You can export this analyzed dataset directly into a standardized CSV file ready to connect into "
            "**Power BI**, **Excel**, or SQL databases:"
        )

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
            label=f"💾 Download {full_ticker} Regime Dataset (CSV for Power BI)",
            data=csv_data,
            file_name=f"{full_ticker.lower()}_regime_analysis_powerbi.csv",
            mime="text/csv",
            type="secondary"
        )

    # ==========================================
    # TAB 2: OPTIONAL 7-DAY MONEY GROWTH SIMULATOR
    # ==========================================
    with tab_simulator:
        st.markdown("### 🔮 7-Day Forward Capital Growth Simulator")
        st.markdown(
            f"This optional simulator projects how an investment in **{coin_ticker}** (denominated in **{selected_fiat}**) "
            f"could behave over the next 7 days based on our machine learning regime forecast, empirical Markov chain transitions, "
            f"and 1,000 Monte Carlo statistical simulation paths."
        )

        # Prominent Mandatory Disclaimer Banner
        st.markdown("""
        <div style="background-color: #FEF3C7; border-left: 6px solid #D97706; padding: 18px 22px; border-radius: 8px; margin-top: 10px; margin-bottom: 25px;">
            <div style="font-size: 1.15rem; font-weight: 800; color: #92400E; margin-bottom: 6px;">
                ⚠️ IMPORTANT DISCLAIMER: It's a prediction, not a statement — take your own risk.
            </div>
            <div style="font-size: 0.95rem; color: #78350F; line-height: 1.5;">
                Cryptocurrency and financial markets are inherently volatile, speculative, and subject to unexpected external macroeconomic events. 
                This simulation represents a <b>probabilistic statistical model</b> conditioned on historical regime dynamics. 
                <b>It does NOT represent a factual statement, guaranteed performance, or professional financial advice.</b> 
                Any capital you invest carries risk of partial or total loss. Always exercise independent diligence and strictly manage your downside risk.
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_input1, col_input2 = st.columns([1.5, 1.0])
        with col_input1:
            default_capital = 10000.0 if selected_fiat == "MXN" else 1000.0
            user_capital = st.number_input(
                f"Enter hypothetical investment amount in {selected_fiat} ({fiat_symbol}):",
                min_value=1.0,
                max_value=100000000.0,
                value=default_capital,
                step=100.0,
                format="%.2f"
            )

        with col_input2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            run_sim = st.button("🚀 Calculate 7-Day Money Projection", type="primary", use_container_width=True)

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
                    label="Starting Capital",
                    value=f"{fiat_symbol}{sim['initial_capital']:,.2f}"
                )
            with s2:
                st.metric(
                    label="Expected Capital (Day 7)",
                    value=f"{fiat_symbol}{sim['final_expected_capital']:,.2f}",
                    delta=f"{sim['final_pct_return']:+.2f}%"
                )
            with s3:
                st.metric(
                    label="Projected Net P&L",
                    value=f"{fiat_symbol}{sim['final_net_profit']:+,.2f}",
                    delta=f"{sim['final_pct_return']:+.2f}%"
                )
            with s4:
                st.metric(
                    label="90% Confidence Corridor",
                    value=f"{fiat_symbol}{sim['lower_bound_10th']:,.0f} - {fiat_symbol}{sim['upper_bound_90th']:,.0f}",
                    help="Range spanning the 10th percentile (defensive adverse scenario) to 90th percentile (optimistic bullish scenario)."
                )

            # 2. 7-Day Forward Trajectory Chart
            st.markdown("#### 📈 7-Day Projected Capital Trajectory")
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
                name="80% Confidence Interval (10th–90th Pct)"
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
                name="50% Core Interquartile Range (25th–75th Pct)"
            ))

            # Expected (Mean) Trajectory
            fig_sim.add_trace(go.Scatter(
                x=dates_list,
                y=corridors["mean"],
                mode="lines+markers",
                name="Expected Balance (Mean)",
                line=dict(color="#1D4ED8", width=3),
                marker=dict(size=6)
            ))

            # Median Trajectory
            fig_sim.add_trace(go.Scatter(
                x=dates_list,
                y=corridors["p50"],
                mode="lines",
                name="Median Balance (50th Pct)",
                line=dict(color="#10B981", width=2, dash="dot")
            ))

            # Initial Capital Baseline
            fig_sim.add_hline(
                y=user_capital,
                line_dash="dash",
                line_color="#94A3B8",
                annotation_text=f"Initial Capital ({fiat_symbol}{user_capital:,.2f})",
                annotation_position="bottom right"
            )

            fig_sim.update_layout(
                title=f"7-Day Forward Money Growth Simulation for {fiat_symbol}{user_capital:,.2f} in {full_ticker}",
                xaxis_title="Forecast Horizon Date",
                yaxis_title=f"Projected Balance ({selected_fiat})",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=420,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_sim, use_container_width=True)

            # 3. Day-by-Day Forecast Breakdown Table
            st.markdown("#### 📅 Day-by-Day Forecast Summary Table")
            b_df = sim["breakdown_df"].copy()
            
            b_display = b_df.copy()
            b_display["Projected Capital"] = b_display["Projected Capital"].apply(lambda v: f"{fiat_symbol}{v:,.2f}")
            b_display["Lower Bound (10th)"] = b_display["Lower Bound (10th)"].apply(lambda v: f"{fiat_symbol}{v:,.2f}")
            b_display["Upper Bound (90th)"] = b_display["Upper Bound (90th)"].apply(lambda v: f"{fiat_symbol}{v:,.2f}")
            b_display["Cumulative P&L"] = b_display["Cumulative P&L"].apply(lambda v: f"{fiat_symbol}{v:+,.2f}")
            b_display["Exp. Daily Return (%)"] = b_display["Exp. Daily Return (%)"].apply(lambda v: f"{v:+.2f}%")
            b_display["Cumulative Return (%)"] = b_display["Cumulative Return (%)"].apply(lambda v: f"{v:+.2f}%")
            b_display["Confidence (%)"] = b_display["Confidence (%)"].apply(lambda v: f"{v:.1f}%")

            st.dataframe(b_display, use_container_width=True, hide_index=True)

            # 4. CSV Download for Simulation
            sim_csv = b_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=f"💾 Download 7-Day Projection Report ({selected_fiat})",
                data=sim_csv,
                file_name=f"{full_ticker.lower()}_7day_simulation_{selected_fiat.lower()}.csv",
                mime="text/csv",
                type="secondary"
            )
