"""
Regime-based trading strategy and portfolio position generation module.
"""

from typing import Dict, Optional
import pandas as pd


class RegimeStrategy:
    """Translates market regime predictions into portfolio weights with lagged causal execution."""

    DEFAULT_POSITION_MAPPING: Dict[str, float] = {
        "Moderate-Volatility Bullish": 1.0,   # Full exposure
        "Low-Volatility Neutral": 1.0,        # Full exposure
        "High-Volatility Transition": 0.5,    # Half exposure
        "High-Volatility Bearish": 0.0        # Cash / flat
    }

    def __init__(self, position_mapping: Optional[Dict[str, float]] = None):
        self.position_mapping = position_mapping or self.DEFAULT_POSITION_MAPPING

    def generate_signals(self, regime_series: pd.Series) -> pd.Series:
        """Map regime names to target portfolio positions."""
        return regime_series.map(self.position_mapping).rename("Signal")

    def run_backtest(
        self,
        raw_price_df: pd.DataFrame,
        regime_df: pd.DataFrame,
        price_col: str = "Close",
        regime_col: str = "Market_Regime"
    ) -> pd.DataFrame:
        """
        Merge raw market prices with regime signals, apply 1-period lag to prevent look-ahead bias,
        and calculate daily strategy returns.
        """
        backtest_df = raw_price_df[[price_col]].join(
            regime_df[[regime_col]],
            how="inner"
        )

        # Generate instantaneous signal
        backtest_df["Signal"] = self.generate_signals(backtest_df[regime_col])

        # Lag position by 1 day to ensure strictly causal execution
        backtest_df["Position"] = backtest_df["Signal"].shift(1)

        # Compute market returns
        backtest_df["Market_Return"] = backtest_df[price_col].pct_change()

        # Compute strategy returns
        backtest_df["Strategy_Return"] = backtest_df["Market_Return"] * backtest_df["Position"]

        # Drop initial NaN rows created by shift and pct_change
        clean_backtest = backtest_df.dropna().copy()
        return clean_backtest
