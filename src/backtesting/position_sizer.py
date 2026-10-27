"""
Position sizing module implementing Discrete, Confidence-Weighted, and Fractional Kelly sizing
with turnover damping filters to maximize risk-adjusted compounding.
"""

from enum import Enum
from typing import Dict, Optional, Union
import numpy as np
import pandas as pd


class SizingMethod(str, Enum):
    """Supported position sizing methodologies."""
    DISCRETE = "discrete"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    FRACTIONAL_KELLY = "fractional_kelly"


class PositionSizer:
    """Computes optimal portfolio exposure weights based on regime probabilities and risk targets."""

    DEFAULT_BASE_WEIGHTS: Dict[str, float] = {
        "Moderate-Volatility Bullish": 1.0,
        "Low-Volatility Neutral": 1.0,
        "High-Volatility Transition": 0.5,
        "High-Volatility Bearish": 0.0
    }

    def __init__(
        self,
        method: Union[str, SizingMethod] = SizingMethod.CONFIDENCE_WEIGHTED,
        base_weights: Optional[Dict[str, float]] = None,
        kelly_fraction: float = 0.5,         # Half-Kelly for robust variance control
        smoothing_alpha: float = 0.8,        # Exponential smoothing (1.0 = instant, 0.2 = slow)
        max_leverage: float = 1.0,          # Long-only spot cap
        min_exposure: float = 0.0            # No naked shorting
    ):
        self.method = SizingMethod(method)
        self.base_weights = base_weights or self.DEFAULT_BASE_WEIGHTS
        self.kelly_fraction = kelly_fraction
        self.smoothing_alpha = smoothing_alpha
        self.max_leverage = max_leverage
        self.min_exposure = min_exposure

    def size_discrete(self, regime_series: pd.Series) -> pd.Series:
        """Classic step-function discrete allocation."""
        return regime_series.map(self.base_weights).fillna(0.0)

    def size_confidence_weighted(self, prob_df: pd.DataFrame) -> pd.Series:
        """
        Calculates exposure as probability-weighted expectation:
        w_t = sum_k ( p_tk * base_weight_k )
        """
        weights = pd.Series(0.0, index=prob_df.index)
        for regime, base_w in self.base_weights.items():
            if regime in prob_df.columns:
                weights += prob_df[regime] * base_w

        return weights.clip(lower=self.min_exposure, upper=self.max_leverage)

    def size_fractional_kelly(
        self,
        prob_df: pd.DataFrame,
        regime_means: Dict[str, float],
        regime_stds: Dict[str, float],
        risk_free_rate: float = 0.0
    ) -> pd.Series:
        """
        Calculates Fractional Kelly exposure:
        f* = lambda * ( E[R] - Rf ) / Var(R)
        """
        expected_returns = pd.Series(0.0, index=prob_df.index)
        expected_variances = pd.Series(0.0, index=prob_df.index)

        for regime in prob_df.columns:
            if regime in regime_means and regime in regime_stds:
                p_k = prob_df[regime]
                mu_k = regime_means[regime]
                var_k = regime_stds[regime] ** 2

                expected_returns += p_k * mu_k
                expected_variances += p_k * (var_k + (mu_k - expected_returns) ** 2)

        # Fractional Kelly calculation with variance floor
        var_safe = expected_variances.clip(lower=1e-5)
        raw_kelly = self.kelly_fraction * (expected_returns - (risk_free_rate / 365.25)) / var_safe
        clipped_kelly = raw_kelly.clip(lower=self.min_exposure, upper=self.max_leverage)
        return clipped_kelly

    def apply_smoothing(self, target_weights: pd.Series) -> pd.Series:
        """
        Applies exponential moving average to position changes to dampen turnover and fee drag:
        w*_t = (1 - alpha) * w*_{t-1} + alpha * w_target
        """
        if self.smoothing_alpha >= 1.0:
            return target_weights

        smoothed = target_weights.ewm(alpha=self.smoothing_alpha, adjust=False).mean()
        return smoothed.clip(lower=self.min_exposure, upper=self.max_leverage)
