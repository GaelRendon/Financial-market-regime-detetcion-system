"""
Performance and risk-adjusted metrics module for strategy evaluation
with transaction cost breakdown and turnover metrics.
"""

from typing import Dict
import numpy as np
import pandas as pd


class PerformanceMetrics:
    """Computes cumulative equity, annualized returns, volatility, Sharpe ratio, drawdown, and trading costs."""

    def __init__(
        self,
        initial_capital: float = 1000.0,
        risk_free_rate: float = 0.0,
        trading_days_per_year: int = 365
    ):
        self.initial_capital = initial_capital
        self.risk_free_rate = risk_free_rate
        self.trading_days_per_year = trading_days_per_year

    def compute_equity_curves(self, backtest_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate compounded equity trajectories for Strategy and Buy & Hold."""
        df = backtest_df.copy()
        df["Strategy_Portfolio"] = (
            self.initial_capital * (1.0 + df["Strategy_Return"]).cumprod()
        )
        if "Gross_Strategy_Return" in df.columns:
            df["Gross_Strategy_Portfolio"] = (
                self.initial_capital * (1.0 + df["Gross_Strategy_Return"]).cumprod()
            )
        df["Buy_Hold_Portfolio"] = (
            self.initial_capital * (1.0 + df["Market_Return"]).cumprod()
        )
        return df

    def evaluate_performance(self, backtest_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate full performance comparison summary table including friction metrics.
        """
        df = self.compute_equity_curves(backtest_df)

        # Elapsed time in years
        days_elapsed = (df.index[-1] - df.index[0]).days
        years = days_elapsed / 365.25

        # 1. Total Returns
        strat_total_return = (df["Strategy_Portfolio"].iloc[-1] / self.initial_capital - 1.0) * 100.0
        bh_total_return = (df["Buy_Hold_Portfolio"].iloc[-1] / self.initial_capital - 1.0) * 100.0

        # 2. Annualized Return (CAGR)
        strat_cagr = ((df["Strategy_Portfolio"].iloc[-1] / self.initial_capital) ** (1.0 / years) - 1.0) * 100.0
        bh_cagr = ((df["Buy_Hold_Portfolio"].iloc[-1] / self.initial_capital) ** (1.0 / years) - 1.0) * 100.0

        # 3. Annualized Volatility
        strat_ann_vol = (df["Strategy_Return"].std() * np.sqrt(self.trading_days_per_year)) * 100.0
        bh_ann_vol = (df["Market_Return"].std() * np.sqrt(self.trading_days_per_year)) * 100.0

        # 4. Sharpe Ratio
        strat_sharpe = ((strat_cagr / 100.0) - self.risk_free_rate) / (strat_ann_vol / 100.0) if strat_ann_vol > 0 else np.nan
        bh_sharpe = ((bh_cagr / 100.0) - self.risk_free_rate) / (bh_ann_vol / 100.0) if bh_ann_vol > 0 else np.nan

        # 5. Maximum Drawdown
        strat_peak = df["Strategy_Portfolio"].cummax()
        bh_peak = df["Buy_Hold_Portfolio"].cummax()

        strat_dd = ((df["Strategy_Portfolio"] / strat_peak) - 1.0) * 100.0
        bh_dd = ((df["Buy_Hold_Portfolio"] / bh_peak) - 1.0) * 100.0

        strat_max_dd = strat_dd.min()
        bh_max_dd = bh_dd.min()

        # 6. Cumulative Friction Impact
        total_turnover = float(df["Turnover"].sum()) if "Turnover" in df.columns else 0.0
        cumulative_friction_cost_pct = (float(df["Friction_Cost"].sum()) * 100.0) if "Friction_Cost" in df.columns else 0.0

        comparison_df = pd.DataFrame({
            "Metric": [
                "Initial Capital ($)",
                "Final Portfolio Value ($)",
                "Total Return (Net) (%)",
                "Annualized Return (Net CAGR) (%)",
                "Annualized Volatility (%)",
                "Sharpe Ratio (Net)",
                "Maximum Drawdown (%)",
                "Cumulative Turnover (Shares/Units)",
                "Total Friction Cost Drag (%)"
            ],
            "Forecasting-Based Strategy": [
                self.initial_capital,
                df["Strategy_Portfolio"].iloc[-1],
                strat_total_return,
                strat_cagr,
                strat_ann_vol,
                strat_sharpe,
                strat_max_dd,
                total_turnover,
                cumulative_friction_cost_pct
            ],
            "Buy & Hold": [
                self.initial_capital,
                df["Buy_Hold_Portfolio"].iloc[-1],
                bh_total_return,
                bh_cagr,
                bh_ann_vol,
                bh_sharpe,
                bh_max_dd,
                0.0,
                0.0
            ]
        })

        comparison_df["Difference (Strategy - Buy & Hold)"] = (
            comparison_df["Forecasting-Based Strategy"] - comparison_df["Buy & Hold"]
        )

        return comparison_df
