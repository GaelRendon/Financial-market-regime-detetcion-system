"""
Regime-based trading strategy and portfolio position generation module
with transaction costs, slippage modeling, and continuous confidence/Kelly position sizing.
"""

from typing import Dict, Optional
import pandas as pd

from .position_sizer import PositionSizer, SizingMethod


class RegimeStrategy:
    """Translates market regime predictions into portfolio weights with lagged causal execution and transaction friction."""

    DEFAULT_POSITION_MAPPING: Dict[str, float] = {
        "Moderate-Volatility Bullish": 1.0,   # Full exposure
        "Low-Volatility Neutral": 1.0,        # Full exposure
        "High-Volatility Transition": 0.5,    # Half exposure
        "High-Volatility Bearish": 0.0        # Cash / flat
    }

    def __init__(
        self,
        position_mapping: Optional[Dict[str, float]] = None,
        position_sizer: Optional[PositionSizer] = None,
        transaction_fee_bps: float = 10.0,
        slippage_bps: float = 5.0
    ):
        self.position_mapping = position_mapping or self.DEFAULT_POSITION_MAPPING
        self.position_sizer = position_sizer or PositionSizer(
            method=SizingMethod.DISCRETE,
            base_weights=self.position_mapping
        )
        self.transaction_fee_rate = transaction_fee_bps / 10000.0  # e.g., 10 bps = 0.0010
        self.slippage_rate = slippage_bps / 10000.0                # e.g., 5 bps = 0.0005
        self.total_cost_rate = self.transaction_fee_rate + self.slippage_rate

    def generate_signals(
        self,
        regime_series: pd.Series,
        probability_df: Optional[pd.DataFrame] = None,
        regime_means: Optional[Dict[str, float]] = None,
        regime_stds: Optional[Dict[str, float]] = None
    ) -> pd.Series:
        """Generate instantaneous portfolio exposure targets using the configured sizing method."""
        if self.position_sizer.method == SizingMethod.DISCRETE or probability_df is None:
            raw_weights = self.position_sizer.size_discrete(regime_series)
        elif self.position_sizer.method == SizingMethod.CONFIDENCE_WEIGHTED:
            raw_weights = self.position_sizer.size_confidence_weighted(probability_df)
        elif self.position_sizer.method == SizingMethod.FRACTIONAL_KELLY:
            if regime_means and regime_stds:
                raw_weights = self.position_sizer.size_fractional_kelly(
                    probability_df, regime_means, regime_stds
                )
            else:
                raw_weights = self.position_sizer.size_confidence_weighted(probability_df)
        else:
            raw_weights = self.position_sizer.size_discrete(regime_series)

        # Apply exponential turnover damping filter
        smoothed_weights = self.position_sizer.apply_smoothing(raw_weights)
        return smoothed_weights.rename("Signal")

    def run_backtest(
        self,
        raw_price_df: pd.DataFrame,
        regime_df: pd.DataFrame,
        price_col: str = "Close",
        regime_col: str = "Market_Regime",
        probability_df: Optional[pd.DataFrame] = None,
        regime_means: Optional[Dict[str, float]] = None,
        regime_stds: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """
        Merge raw market prices with regime signals, apply 1-period lag to prevent look-ahead bias,
        calculate turnover, apply trading friction (fees + slippage), and calculate net returns.
        """
        backtest_df = raw_price_df[[price_col]].join(
            regime_df[[regime_col]],
            how="inner"
        )

        # Generate instantaneous signal (discrete or continuous)
        backtest_df["Signal"] = self.generate_signals(
            regime_series=backtest_df[regime_col],
            probability_df=probability_df,
            regime_means=regime_means,
            regime_stds=regime_stds
        )

        # Lag position by 1 day to ensure strictly causal execution
        backtest_df["Position"] = backtest_df["Signal"].shift(1)

        # Compute market returns
        backtest_df["Market_Return"] = backtest_df[price_col].pct_change()

        # Gross strategy returns
        backtest_df["Gross_Strategy_Return"] = backtest_df["Market_Return"] * backtest_df["Position"]

        # Calculate position turnover (change in exposure)
        # Position change happens at rebalance moments: delta_w = |w_t - w_{t-1}|
        backtest_df["Turnover"] = (backtest_df["Position"] - backtest_df["Position"].shift(1)).abs().fillna(0.0)

        # Friction cost deduction: Cost = Turnover * (Fee_rate + Slippage_rate)
        backtest_df["Friction_Cost"] = backtest_df["Turnover"] * self.total_cost_rate

        # Net strategy return after trading friction
        backtest_df["Strategy_Return"] = backtest_df["Gross_Strategy_Return"] - backtest_df["Friction_Cost"]

        # Drop initial NaN rows created by shift and pct_change
        clean_backtest = backtest_df.dropna().copy()
        return clean_backtest
