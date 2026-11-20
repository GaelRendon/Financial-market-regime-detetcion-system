"""
UI styles, CSS injection, and shared formatting helpers.
"""

import streamlit as st

CURRENCY_SYMBOLS: dict = {
    "USD": "$",
    "MXN": "$",
    "EUR": "€",
    "GBP": "£",
    "CAD": "$",
}

REGIME_COLORS: dict = {
    "Moderate-Volatility Bullish": "#10B981",
    "Low-Volatility Neutral":      "#3B82F6",
    "High-Volatility Transition":  "#F59E0B",
    "High-Volatility Bearish":     "#EF4444",
}


def inject_css() -> None:
    """Inject global custom CSS into the Streamlit page."""
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
    .action-box-green  { background-color: #ECFDF5; border-left: 8px solid #10B981; }
    .action-box-blue   { background-color: #EFF6FF; border-left: 8px solid #3B82F6; }
    .action-box-orange { background-color: #FFFBEB; border-left: 8px solid #F59E0B; }
    .action-box-red    { background-color: #FEF2F2; border-left: 8px solid #EF4444; }
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
        padding: 14px 16px;
        overflow: visible !important;
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


def format_asset_price(value: float, symbol: str = "$") -> str:
    """
    Format any asset price with adaptive decimal precision.
    Handles everything from BTC (~$65k) down to micro-cap tokens (<$0.0001).
    """
    abs_val = abs(value)
    if abs_val >= 1.0:
        return f"{symbol}{value:,.2f}"
    elif abs_val >= 0.01:
        return f"{symbol}{value:,.4f}"
    elif abs_val >= 0.0001:
        return f"{symbol}{value:,.6f}"
    elif abs_val > 0:
        return f"{symbol}{value:,.8f}"
    return f"{symbol}0.00"


# Backward-compatible alias kept for any legacy reference
format_crypto_price = format_asset_price
