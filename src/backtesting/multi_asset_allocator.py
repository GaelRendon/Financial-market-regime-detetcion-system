"""
Multi-asset cross-sectional portfolio allocation module based on market regimes.
Enables dynamic capital rotation, risk parity, and regime-filtered momentum across multiple crypto assets.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

from .metrics import PerformanceMetrics
from .position_sizer import SizingMethod


class MultiAssetStrategy(str, Enum):
    """Supported multi-asset allocation strategy types."""
    EQUAL_WEIGHT = "equal_weight"
    REGIME_PROPORTIONAL = "regime_proportional"
    TOP_K_MOMENTUM_REGIME = "top_k_momentum_regime"
    RISK_PARITY_REGIME = "risk_parity_regime"
    CONFIDENCE_WEIGHTED_MULTI = "confidence_weighted_multi"


class MultiAssetAllocator:
    """
    Cross-sectional multi-asset capital allocator that dynamically rotates capital
    across a universe of cryptocurrency assets conditioned on predicted market regimes.
    """

    DEFAULT_REGIME_WEIGHTS: Dict[str, float] = {
        "Moderate-Volatility Bullish": 1.0,
        "Low-Volatility Neutral": 0.8,
        "High-Volatility Transition": 0.3,
        "High-Volatility Bearish": 0.0
    }

    def __init__(
        self,
        assets: Optional[List[str]] = None,
        transaction_fee_bps: float = 10.0,
        slippage_bps: float = 5.0,
        top_k: int = 2,
        momentum_lookback: int = 14,
        volatility_window: int = 30,
        initial_capital: float = 1000.0,
        risk_free_rate: float = 0.0,
        trading_days_per_year: int = 365
    ):
        self.assets = assets or ["BTC", "ETH", "SOL"]
        self.transaction_fee_rate = transaction_fee_bps / 10000.0
        self.slippage_rate = slippage_bps / 10000.0
        self.total_cost_rate = self.transaction_fee_rate + self.slippage_rate
        self.top_k = top_k
        self.momentum_lookback = momentum_lookback
        self.volatility_window = volatility_window
        self.metrics_engine = PerformanceMetrics(
            initial_capital=initial_capital,
            risk_free_rate=risk_free_rate,
            trading_days_per_year=trading_days_per_year
        )

    def allocate_equal_weight(self, returns_df: pd.DataFrame) -> pd.DataFrame:
        """
        Passive benchmark: 1/N equal capital weighting across all assets.
        w_{i,t} = 1 / N
        """
        n_assets = len(returns_df.columns)
        w = 1.0 / n_assets if n_assets > 0 else 0.0
        weights_df = pd.DataFrame(w, index=returns_df.index, columns=returns_df.columns)
        weights_df["Cash"] = 0.0
        return weights_df

    def allocate_regime_proportional(
        self,
        returns_df: pd.DataFrame,
        regimes_df: pd.DataFrame,
        base_weights: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """
        Regime-proportional allocation:
        Each asset receives target exposure based on its current regime.
        Total exposure is normalized to <= 1.0. If all assets are bearish, 100% Cash is held.
        """
        mapping = base_weights or self.DEFAULT_REGIME_WEIGHTS
        raw_weights = pd.DataFrame(index=returns_df.index)

        for col in returns_df.columns:
            if col in regimes_df.columns:
                raw_weights[col] = regimes_df[col].map(mapping).fillna(0.0)
            else:
                raw_weights[col] = 0.0

        # Normalization across assets: if sum > 1.0, scale down. Remainder goes to Cash.
        row_sums = raw_weights.sum(axis=1)
        scale_factors = row_sums.apply(lambda s: 1.0 / s if s > 1.0 else 1.0)
        norm_weights = raw_weights.multiply(scale_factors, axis=0)
        norm_weights["Cash"] = (1.0 - norm_weights.sum(axis=1)).clip(lower=0.0)

        return norm_weights

    def allocate_top_k_momentum(
        self,
        returns_df: pd.DataFrame,
        regimes_df: pd.DataFrame,
        k: Optional[int] = None,
        lookback: Optional[int] = None,
        excluded_regimes: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Cross-sectional momentum with regime gatekeeping:
        1. Rank assets daily by trailing cumulative return over lookback window.
        2. Filter out assets in Bearish regime (uninvestable gate).
        3. Allocate equal share (1/K) to the top K non-bearish assets.
        4. If fewer than K assets qualify, unallocated share remains in Cash.
        """
        k_val = k or self.top_k
        lb = lookback or self.momentum_lookback
        bad_regimes = excluded_regimes or ["High-Volatility Bearish"]

        # Trailing momentum (compounded return over lookback)
        cum_returns = (1.0 + returns_df).rolling(window=lb).apply(np.prod, raw=True) - 1.0

        weights = pd.DataFrame(0.0, index=returns_df.index, columns=returns_df.columns)

        for t in returns_df.index:
            mom_t = cum_returns.loc[t]
            reg_t = regimes_df.loc[t] if t in regimes_df.index else None

            # Filter valid assets (not bearish and not NaN)
            valid_assets = []
            for col in returns_df.columns:
                if reg_t is not None and col in reg_t and reg_t[col] in bad_regimes:
                    continue
                if pd.notna(mom_t[col]):
                    valid_assets.append((col, mom_t[col]))

            if not valid_assets:
                continue

            # Sort descending by trailing momentum
            valid_assets.sort(key=lambda x: x[1], reverse=True)
            selected = valid_assets[:k_val]

            # Each selected gets 1/k_val weight
            per_asset_weight = 1.0 / k_val
            for col, _ in selected:
                weights.loc[t, col] = per_asset_weight

        weights["Cash"] = (1.0 - weights[returns_df.columns].sum(axis=1)).clip(lower=0.0)
        return weights

    def allocate_risk_parity(
        self,
        returns_df: pd.DataFrame,
        regimes_df: pd.DataFrame,
        vol_window: Optional[int] = None,
        excluded_regimes: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Regime-conditioned inverse-volatility risk parity:
        w_{i,t}^* = (1 / sigma_{i,t}) * 1_{S_{i,t} not in Excluded}
        w_{i,t} = w_{i,t}^* / sum_j w_{j,t}^*
        Assets with lower volatility receive proportionally larger weight,
        while bearish assets receive zero allocation.
        """
        vw = vol_window or self.volatility_window
        bad_regimes = excluded_regimes or ["High-Volatility Bearish"]

        rolling_vols = returns_df.rolling(window=vw).std()
        raw_inv_vols = pd.DataFrame(0.0, index=returns_df.index, columns=returns_df.columns)

        for col in returns_df.columns:
            is_investable = ~regimes_df[col].isin(bad_regimes) if col in regimes_df.columns else True
            inv_vol = 1.0 / rolling_vols[col].replace(0.0, np.nan)
            raw_inv_vols[col] = (inv_vol * is_investable).fillna(0.0)

        # Normalize across valid assets
        total_inv = raw_inv_vols.sum(axis=1)
        weights = raw_inv_vols.divide(total_inv.replace(0.0, np.nan), axis=0).fillna(0.0)
        weights["Cash"] = (1.0 - weights[returns_df.columns].sum(axis=1)).clip(lower=0.0)

        return weights

    def allocate_confidence_weighted(
        self,
        returns_df: pd.DataFrame,
        probs_dict: Dict[str, pd.DataFrame],
        base_weights: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """
        Continuous confidence-weighted cross-sectional allocation:
        Uses full posterior probability vectors across assets:
        s_{i,t} = sum_k ( P(S_{i,t} = k) * base_weight_k )
        Weights are normalized so sum w_i <= 1.0.
        """
        mapping = base_weights or self.DEFAULT_REGIME_WEIGHTS
        raw_scores = pd.DataFrame(0.0, index=returns_df.index, columns=returns_df.columns)

        for col in returns_df.columns:
            if col in probs_dict:
                prob_df = probs_dict[col].reindex(returns_df.index).ffill().bfill()
                asset_score = pd.Series(0.0, index=returns_df.index)
                for reg, w_val in mapping.items():
                    if reg in prob_df.columns:
                        asset_score += prob_df[reg] * w_val
                raw_scores[col] = asset_score

        # Normalize
        row_sums = raw_scores.sum(axis=1)
        scale_factors = row_sums.apply(lambda s: 1.0 / s if s > 1.0 else 1.0)
        norm_weights = raw_scores.multiply(scale_factors, axis=0)
        norm_weights["Cash"] = (1.0 - norm_weights.sum(axis=1)).clip(lower=0.0)

        return norm_weights

    def run_backtest(
        self,
        returns_df: pd.DataFrame,
        target_weights_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Executes backtest with causal lag (w_{t+1}^{exec} = w_{t}), multi-asset turnover
        calculation, transaction fees, and slippage deduction.
        """
        asset_cols = [c for c in returns_df.columns if c in target_weights_df.columns]
        aligned_returns = returns_df[asset_cols].copy()
        raw_target_weights = target_weights_df[asset_cols].reindex(aligned_returns.index).fillna(0.0)

        # Causal execution: weights determined at close t are applied to return at t+1
        executed_weights = raw_target_weights.shift(1).fillna(0.0)

        # Multi-asset portfolio gross return: sum_i ( w_{i,t}^{exec} * R_{i,t} )
        gross_strategy_returns = (executed_weights * aligned_returns).sum(axis=1)

        # Multi-asset turnover: sum_i | w_{i,t}^{exec} - w_{i,t-1}^{exec} |
        weight_changes = executed_weights.diff().abs()
        turnover = weight_changes.sum(axis=1).fillna(0.0)

        # Friction cost in basis points
        friction_cost = turnover * self.total_cost_rate

        # Net strategy return
        net_strategy_returns = gross_strategy_returns - friction_cost

        # Passive Equal-Weight Benchmark
        benchmark_returns = aligned_returns.mean(axis=1)

        backtest_df = pd.DataFrame({
            "Gross_Strategy_Return": gross_strategy_returns,
            "Strategy_Return": net_strategy_returns,
            "Market_Return": benchmark_returns,
            "Turnover": turnover,
            "Friction_Cost": friction_cost
        }, index=aligned_returns.index)

        # Equity curves and metrics
        equity_df = self.metrics_engine.compute_equity_curves(backtest_df)
        perf_summary = self.metrics_engine.evaluate_performance(backtest_df)

        return {
            "backtest_df": backtest_df,
            "equity_df": equity_df,
            "performance_summary": perf_summary,
            "executed_weights": executed_weights,
            "target_weights": raw_target_weights
        }

    def evaluate_all_strategies(
        self,
        returns_df: pd.DataFrame,
        regimes_df: pd.DataFrame,
        probs_dict: Optional[Dict[str, pd.DataFrame]] = None
    ) -> Dict[str, Any]:
        """
        Backtests and benchmarks all available multi-asset allocation strategies
        against passive equal weight.
        """
        results = {}

        # 1. Equal Weight (Benchmark)
        w_eq = self.allocate_equal_weight(returns_df)
        results[MultiAssetStrategy.EQUAL_WEIGHT.value] = self.run_backtest(returns_df, w_eq)

        # 2. Regime Proportional
        w_reg = self.allocate_regime_proportional(returns_df, regimes_df)
        results[MultiAssetStrategy.REGIME_PROPORTIONAL.value] = self.run_backtest(returns_df, w_reg)

        # 3. Top-K Momentum + Regime Gate
        w_topk = self.allocate_top_k_momentum(returns_df, regimes_df)
        results[MultiAssetStrategy.TOP_K_MOMENTUM_REGIME.value] = self.run_backtest(returns_df, w_topk)

        # 4. Risk Parity + Regime Gate
        w_rp = self.allocate_risk_parity(returns_df, regimes_df)
        results[MultiAssetStrategy.RISK_PARITY_REGIME.value] = self.run_backtest(returns_df, w_rp)

        # 5. Confidence-Weighted (if probabilities provided)
        if probs_dict:
            w_conf = self.allocate_confidence_weighted(returns_df, probs_dict)
            results[MultiAssetStrategy.CONFIDENCE_WEIGHTED_MULTI.value] = self.run_backtest(returns_df, w_conf)

        # Compile comparison table
        summary_rows = []
        for strat_name, res in results.items():
            metrics_table = res["performance_summary"]
            strat_col = metrics_table["Forecasting-Based Strategy"]
            metrics_dict = dict(zip(metrics_table["Metric"], strat_col))
            metrics_dict["Strategy"] = strat_name
            summary_rows.append(metrics_dict)

        comparison_matrix = pd.DataFrame(summary_rows)
        if "Strategy" in comparison_matrix.columns:
            cols = ["Strategy"] + [c for c in comparison_matrix.columns if c != "Strategy"]
            comparison_matrix = comparison_matrix[cols]

        return {
            "strategy_results": results,
            "comparison_matrix": comparison_matrix
        }
