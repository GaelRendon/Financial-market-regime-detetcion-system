"""
Streamlit Web Application: Financial Market Regime Detection System.
Interactive quantitative dashboard for live multi-asset & multi-currency regime forecasting.
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
st.markdown(f"<div class='main-header'>📈 Financial Market Regime Detection System</div>", unsafe_allow_html=True)
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
    # 1. Top Metrics Banner
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric(
            label=f"Current Price ({selected_fiat})",
            value=f"{fiat_symbol}{results['latest_close']:,.2f}",
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
            title=dict(text="<b>Forecast Confidence Distribution</b>", font=dict(size=14)),
            xaxis=dict(title="Probability (%)", range=[0, 100]),
            yaxis=dict(title=""),
            height=205,
            margin=dict(l=10, r=20, t=35, b=25)
        )
        st.plotly_chart(fig_prob, use_container_width=True)

    # 3. Interactive Historical Regime Timeline Chart
    st.markdown("### 📊 Historical Price & Detected Market Regimes")
    hist_df = results["df_history"]

    regime_colors = {
        "Moderate-Volatility Bullish": "#10B981",
        "Low-Volatility Neutral": "#3B82F6",
        "High-Volatility Transition": "#F59E0B",
        "High-Volatility Bearish": "#EF4444"
    }

    fig_price = go.Figure()

    # Price Line
    fig_price.add_trace(go.Scatter(
        x=hist_df.index,
        y=hist_df["Close"],
        mode="lines",
        name=f"{full_ticker} Close",
        line=dict(color="#0F172A", width=2)
    ))

    # Scatter points colored by regime
    for regime_name, color in regime_colors.items():
        subset = hist_df[hist_df["Market_Regime"] == regime_name]
        if not subset.empty:
            fig_price.add_trace(go.Scatter(
                x=subset.index,
                y=subset["Close"],
                mode="markers",
                name=regime_name,
                marker=dict(color=color, size=4, opacity=0.8)
            ))

    fig_price.update_layout(
        title=dict(text=f"<b>{full_ticker} Historical Price by Market Regime</b>", font=dict(size=16)),
        xaxis=dict(title="Date", showgrid=True),
        yaxis=dict(title=f"Price ({selected_fiat})", type="linear", showgrid=True),
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    st.plotly_chart(fig_price, use_container_width=True)

    # 4. Feature Diagnostics & Dynamics
    st.markdown("### 🔍 Underlying Feature Dynamics")
    tab1, tab2, tab3 = st.tabs(["Daily Returns", "30-Day Rolling Volatility", "14-Day Momentum"])

    with tab1:
        fig_ret = go.Figure()
        fig_ret.add_trace(go.Scatter(
            x=hist_df.index,
            y=hist_df["Returns"] * 100,
            mode="lines",
            name="Daily Return %",
            line=dict(color="#6366F1", width=1.2)
        ))
        std_ret = hist_df["Returns"].std() * 100
        fig_ret.add_hline(y=2 * std_ret, line_dash="dash", line_color="#EF4444", annotation_text="+2σ Tail Bound")
        fig_ret.add_hline(y=-2 * std_ret, line_dash="dash", line_color="#EF4444", annotation_text="-2σ Tail Bound")
        fig_ret.update_layout(title="Daily Percentage Returns", yaxis_title="Return (%)", height=320, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_ret, use_container_width=True)

    with tab2:
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(
            x=hist_df.index,
            y=hist_df["Volatility"] * 100,
            mode="lines",
            name="30d Rolling Volatility %",
            line=dict(color="#F59E0B", width=1.8),
            fill="tozeroy"
        ))
        fig_vol.update_layout(title="30-Day Rolling Volatility", yaxis_title="Volatility (%)", height=320, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_vol, use_container_width=True)

    with tab3:
        fig_mom = go.Figure()
        fig_mom.add_trace(go.Scatter(
            x=hist_df.index,
            y=hist_df["Momentum"] * 100,
            mode="lines",
            name="14d Momentum %",
            line=dict(color="#10B981", width=1.5)
        ))
        fig_mom.add_hline(y=0.0, line_dash="dash", line_color="#94A3B8")
        fig_mom.update_layout(title="14-Day Rate of Change Momentum", yaxis_title="Momentum (%)", height=320, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_mom, use_container_width=True)

    # 5. Markov Transition Matrix & Persistence
    st.markdown("### 🎲 Markov Regime Transition & Persistence Analysis")
    col_tm, col_pers = st.columns([1.2, 1.0])

    with col_tm:
        trans_df = results["transition_matrix"] * 100
        fig_tm = go.Figure(data=go.Heatmap(
            z=trans_df.values,
            x=trans_df.columns,
            y=trans_df.index,
            colorscale="Blues",
            text=np.round(trans_df.values, 1),
            texttemplate="%{text}%",
            hoverongaps=False
        ))
        fig_tm.update_layout(
            title="<b>Transition Probability Matrix P(Next | Current)</b>",
            xaxis_title="Next Day Regime",
            yaxis_title="Current Day Regime",
            height=320,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_tm, use_container_width=True)

    with col_pers:
        pers_dict = results["persistence_stats"]
        pers_rows = []
        for r_name, vals in pers_dict.items():
            pers_rows.append({
                "Regime": r_name,
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
