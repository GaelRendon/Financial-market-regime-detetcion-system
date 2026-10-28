"""
Online inference and live scoring engine for Market Regime Detection.
Supports any cryptocurrency and fiat currency pair on demand with automatic FX conversion.
"""

import os
import sys
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from config.config import RANDOM_SEED


class RegimeInferenceEngine:
    """Live inference engine for dynamic asset regime detection and forecasting."""

    ACTION_POLICIES = {
        "Moderate-Volatility Bullish": {
            "action": "BUY / OVERWEIGHT",
            "position": 1.0,
            "badge_color": "green",
            "risk_level": "Moderate Risk / High Upside",
            "rationale": "Market displays strong positive momentum with controlled volatility. Historical data supports full market exposure to capture appreciation."
        },
        "Low-Volatility Neutral": {
            "action": "HOLD / ACCUMULATE",
            "position": 1.0,
            "badge_color": "blue",
            "risk_level": "Low Risk / Stable",
            "rationale": "Market is in an orderly consolidation or low-volatility phase. Downside variance is subdued; maintaining full market position is recommended."
        },
        "High-Volatility Transition": {
            "action": "REDUCE EXPOSURE / DEFENSIVE",
            "position": 0.5,
            "badge_color": "orange",
            "risk_level": "Elevated Risk / Regime Shift",
            "rationale": "Volatility is surging with unstable momentum. Downside tail-risk is elevated. De-risking to 50% exposure and 50% cash preserves capital."
        },
        "High-Volatility Bearish": {
            "action": "SELL / CASH (FLAT)",
            "position": 0.0,
            "badge_color": "red",
            "risk_level": "Severe Capital Destruction Risk",
            "rationale": "Severe downward momentum coupled with extreme volatility. The model strongly advises moving 100% to cash to protect capital against severe drawdowns."
        }
    }

    def __init__(self, volatility_window: int = 30, momentum_window: int = 14, n_clusters: int = 4):
        self.volatility_window = volatility_window
        self.momentum_window = momentum_window
        self.n_clusters = n_clusters

    def fetch_live_data(self, coin: str, fiat: str, period: str = "3y") -> pd.DataFrame:
        """
        Download historical price data. Automatically falls back to FX rate conversion
        if direct pair is unavailable on Yahoo Finance.
        """
        direct_ticker = f"{coin}-{fiat}"
        data = yf.download(direct_ticker, period=period, interval="1d", progress=False)

        if not data.empty and len(data) > 60:
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            data.index.name = "Date"
            return data

        # Fallback via USD conversion
        usd_ticker = f"{coin}-USD"
        data_usd = yf.download(usd_ticker, period=period, interval="1d", progress=False)
        if data_usd.empty:
            raise ValueError(f"Could not fetch crypto data for '{coin}'. Please verify the symbol.")

        if isinstance(data_usd.columns, pd.MultiIndex):
            data_usd.columns = data_usd.columns.get_level_values(0)

        if fiat.upper() == "USD":
            data_usd.index.name = "Date"
            return data_usd

        # Fetch FX rate (USD to Target Fiat)
        fx_ticker = f"{fiat}=X" if fiat.upper() == "MXN" else f"USD{fiat}=X"
        fx_data = yf.download(fx_ticker, period=period, interval="1d", progress=False)

        if fx_data.empty:
            fx_ticker_alt = f"{fiat}USD=X"
            fx_data = yf.download(fx_ticker_alt, period=period, interval="1d", progress=False)
            if fx_data.empty:
                raise ValueError(f"Direct ticker '{direct_ticker}' and FX rate for '{fiat}' not found.")
            fx_rate = 1.0 / fx_data["Close"]
        else:
            if isinstance(fx_data.columns, pd.MultiIndex):
                fx_data.columns = fx_data.columns.get_level_values(0)
            fx_rate = fx_data["Close"]

        # Align Dates
        joined = data_usd.join(fx_rate.rename("FX_Rate"), how="inner").ffill().bfill()
        converted = pd.DataFrame(index=joined.index)
        for col in ["Open", "High", "Low", "Close", "Adj Close"]:
            if col in joined.columns:
                converted[col] = joined[col] * joined["FX_Rate"]
        if "Volume" in joined.columns:
            converted["Volume"] = joined["Volume"]

        converted.index.name = "Date"
        return converted

    def _characterize_clusters(self, features_df: pd.DataFrame, cluster_labels: np.ndarray) -> Dict[int, str]:
        """Dynamically assign financial labels to cluster IDs based on return, volatility, and momentum."""
        df_temp = features_df.copy()
        df_temp["Cluster"] = cluster_labels
        grouped = df_temp.groupby("Cluster").mean()

        bearish_id = grouped["Returns"].idxmin()
        remaining = [c for c in grouped.index if c != bearish_id]
        bullish_id = grouped.loc[remaining, "Returns"].idxmax()
        remaining = [c for c in remaining if c != bullish_id]
        neutral_id = grouped.loc[remaining, "Volatility"].idxmin()
        remaining = [c for c in remaining if c != neutral_id]
        transition_id = remaining[0] if remaining else 0

        mapping = {
            bullish_id: "Moderate-Volatility Bullish",
            neutral_id: "Low-Volatility Neutral",
            transition_id: "High-Volatility Transition",
            bearish_id: "High-Volatility Bearish"
        }
        return mapping

    def analyze_ticker(self, ticker: str, period: str = "3y") -> Dict[str, Any]:
        """
        Execute full inference pipeline for any ticker (e.g. BTC-USD, BTC-MXN, ETH-EUR).
        """
        parts = ticker.split("-")
        coin = parts[0].strip().upper()
        fiat = parts[1].strip().upper() if len(parts) > 1 else "USD"

        # 1. Fetch data
        raw_df = self.fetch_live_data(coin=coin, fiat=fiat, period=period)

        # 2. Compute features
        features_df = pd.DataFrame(index=raw_df.index)
        features_df["Returns"] = raw_df["Close"].pct_change()
        features_df["Volatility"] = features_df["Returns"].rolling(self.volatility_window).std()
        features_df["Momentum"] = (raw_df["Close"] / raw_df["Close"].shift(self.momentum_window)) - 1.0

        clean_data = raw_df.join(features_df, how="inner").dropna()
        if len(clean_data) < 80:
            raise ValueError(f"Not enough observations ({len(clean_data)}) to build models for {ticker}.")

        # 3. Standardize & PCA
        feat_cols = ["Returns", "Volatility", "Momentum"]
        scaler = StandardScaler()
        scaled = scaler.fit_transform(clean_data[feat_cols])

        pca = PCA(n_components=min(3, len(feat_cols)))
        pca_proj = pca.fit_transform(scaled)

        # 4. K-Means
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=RANDOM_SEED, n_init=10)
        clusters = kmeans.fit_predict(pca_proj)

        cluster_map = self._characterize_clusters(clean_data[feat_cols], clusters)
        clean_data["Cluster"] = clusters
        clean_data["Market_Regime"] = clean_data["Cluster"].map(cluster_map)

        # 5. Markov Transition Matrix & Persistence
        current_regime_series = clean_data["Market_Regime"]
        next_regime_series = clean_data["Market_Regime"].shift(-1)
        trans_mat = pd.crosstab(current_regime_series, next_regime_series, normalize="index")

        persistence_stats = {}
        for r in trans_mat.index:
            p_ii = trans_mat.loc[r, r] if r in trans_mat.columns else 0.0
            expected_days = 1.0 / (1.0 - p_ii) if p_ii < 1.0 else 999.0
            persistence_stats[r] = {
                "self_transition_prob": round(float(p_ii) * 100, 2),
                "expected_duration_days": round(float(expected_days), 1)
            }

        # 6. Forecasting Model Training & Next-Day Prediction
        train_df = clean_data.copy()
        train_df["Target"] = train_df["Market_Regime"].shift(-1)
        train_df = train_df.dropna(subset=["Target"]).copy()

        le_regime = LabelEncoder()
        train_df["Regime_Enc"] = le_regime.fit_transform(train_df["Market_Regime"])
        train_df["Target_Enc"] = le_regime.transform(train_df["Target"])

        x_cols = ["Returns", "Volatility", "Momentum", "Regime_Enc"]
        clf = RandomForestClassifier(n_estimators=100, random_state=RANDOM_SEED)
        clf.fit(train_df[x_cols], train_df["Target_Enc"])

        latest_row = clean_data.iloc[-1]
        latest_regime_enc = le_regime.transform([latest_row["Market_Regime"]])[0]
        latest_x = pd.DataFrame([{
            "Returns": latest_row["Returns"],
            "Volatility": latest_row["Volatility"],
            "Momentum": latest_row["Momentum"],
            "Regime_Enc": latest_regime_enc
        }])

        next_pred_enc = clf.predict(latest_x)[0]
        next_probs = clf.predict_proba(latest_x)[0]

        next_regime_name = le_regime.inverse_transform([next_pred_enc])[0]
        prob_dict = {
            le_regime.inverse_transform([i])[0]: float(next_probs[i])
            for i in range(len(next_probs))
        }

        policy = self.ACTION_POLICIES.get(next_regime_name, {
            "action": "HOLD",
            "position": 1.0,
            "badge_color": "blue",
            "risk_level": "Moderate",
            "rationale": "Maintain defensive alignment."
        })

        streak = 1
        regimes_rev = clean_data["Market_Regime"].values[::-1]
        for i in range(1, len(regimes_rev)):
            if regimes_rev[i] == regimes_rev[0]:
                streak += 1
            else:
                break

        latest_close = float(clean_data["Close"].iloc[-1])
        prev_close = float(clean_data["Close"].iloc[-2])
        change_24h = ((latest_close - prev_close) / prev_close) * 100.0

        return {
            "ticker": ticker,
            "coin": coin,
            "fiat": fiat,
            "latest_date": str(clean_data.index[-1].date()),
            "latest_close": latest_close,
            "change_24h_pct": change_24h,
            "current_regime": latest_row["Market_Regime"],
            "regime_streak_days": streak,
            "current_volatility_pct": float(latest_row["Volatility"]) * 100.0,
            "current_momentum_pct": float(latest_row["Momentum"]) * 100.0,
            "forecast_regime": next_regime_name,
            "forecast_probabilities": prob_dict,
            "recommendation": policy,
            "transition_matrix": trans_mat,
            "persistence_stats": persistence_stats,
            "df_history": clean_data
        }

    def simulate_forward_trajectory(
        self,
        analysis_result: Dict[str, Any],
        initial_capital: float = 1000.0,
        horizon_days: int = 7,
        n_simulations: int = 1000
    ) -> Dict[str, Any]:
        """
        Simulate multi-step forward money growth over horizon_days (e.g. 7 days)
        using Markov chain transition propagation and Monte Carlo empirical sampling.
        """
        df_hist = analysis_result["df_history"]
        trans_mat = analysis_result["transition_matrix"]
        forecast_probs = analysis_result["forecast_probabilities"]
        latest_date_str = analysis_result["latest_date"]
        start_date = pd.to_datetime(latest_date_str)

        # 1. Historical empirical return distribution per regime
        regime_stats = {}
        for reg in df_hist["Market_Regime"].unique():
            reg_rets = df_hist.loc[df_hist["Market_Regime"] == reg, "Returns"].dropna()
            regime_stats[reg] = {
                "mean": float(reg_rets.mean()) if len(reg_rets) > 0 else 0.0,
                "std": float(reg_rets.std()) if len(reg_rets) > 1 else 0.02
            }

        # Align regimes list
        regimes = list(trans_mat.index)
        n_regimes = len(regimes)
        reg_to_idx = {r: i for i, r in enumerate(regimes)}

        # Transition matrix as numpy array
        P = np.zeros((n_regimes, n_regimes))
        for r_from in regimes:
            i = reg_to_idx[r_from]
            for r_to in regimes:
                j = reg_to_idx[r_to]
                if r_to in trans_mat.columns:
                    P[i, j] = trans_mat.loc[r_from, r_to]
            if P[i].sum() > 0:
                P[i] = P[i] / P[i].sum()
            else:
                P[i, i] = 1.0

        # Initial Day 1 probability vector from model forecast
        p1 = np.zeros(n_regimes)
        for r, prob in forecast_probs.items():
            if r in reg_to_idx:
                p1[reg_to_idx[r]] = prob
        if p1.sum() > 0:
            p1 = p1 / p1.sum()
        else:
            p1 = np.ones(n_regimes) / n_regimes

        # 2. Multi-step analytical Markov propagation
        daily_probs = [p1]
        current_p = p1.copy()
        for d in range(1, horizon_days):
            current_p = np.dot(current_p, P)
            daily_probs.append(current_p)

        # 3. Monte Carlo Simulation for path distributions
        rng = np.random.RandomState(RANDOM_SEED)
        sim_paths = np.zeros((n_simulations, horizon_days + 1))
        sim_paths[:, 0] = initial_capital

        means = np.array([regime_stats.get(r, {}).get("mean", 0.0) for r in regimes])
        stds = np.array([regime_stats.get(r, {}).get("std", 0.02) for r in regimes])

        for s in range(n_simulations):
            state_idx = rng.choice(n_regimes, p=p1)
            for d in range(horizon_days):
                daily_ret = rng.normal(loc=means[state_idx], scale=stds[state_idx])
                daily_ret = np.clip(daily_ret, -0.30, 0.50)
                sim_paths[s, d + 1] = sim_paths[s, d] * (1.0 + daily_ret)
                state_idx = rng.choice(n_regimes, p=P[state_idx])

        # Percentile corridors
        pct_10 = np.percentile(sim_paths, 10, axis=0)
        pct_25 = np.percentile(sim_paths, 25, axis=0)
        pct_50 = np.percentile(sim_paths, 50, axis=0)
        pct_75 = np.percentile(sim_paths, 75, axis=0)
        pct_90 = np.percentile(sim_paths, 90, axis=0)
        pct_mean = np.mean(sim_paths, axis=0)

        # 4. Construct Day-by-Day Breakdown Table
        breakdown = []
        for d in range(horizon_days):
            day_num = d + 1
            day_date = (start_date + pd.Timedelta(days=day_num)).strftime("%Y-%m-%d")
            p_vector = daily_probs[d]
            best_idx = int(np.argmax(p_vector))
            best_regime = regimes[best_idx]
            confidence = float(p_vector[best_idx]) * 100.0

            expected_ret = float(np.sum(p_vector * means))
            expected_cap = float(pct_mean[day_num])
            pnl = expected_cap - initial_capital

            breakdown.append({
                "Day": f"Day {day_num}",
                "Date": day_date,
                "Predicted_Regime": best_regime,
                "Confidence (%)": round(confidence, 1),
                "Exp. Daily Return (%)": round(expected_ret * 100.0, 2),
                "Projected Capital": round(expected_cap, 2),
                "Lower Bound (10th)": round(float(pct_10[day_num]), 2),
                "Upper Bound (90th)": round(float(pct_90[day_num]), 2),
                "Cumulative P&L": round(pnl, 2),
                "Cumulative Return (%)": round(((expected_cap / initial_capital) - 1.0) * 100.0, 2)
            })

        breakdown_df = pd.DataFrame(breakdown)

        final_exp_cap = float(pct_mean[-1])
        final_pnl = final_exp_cap - initial_capital
        final_pct = ((final_exp_cap / initial_capital) - 1.0) * 100.0

        return {
            "initial_capital": float(initial_capital),
            "final_expected_capital": round(final_exp_cap, 2),
            "final_net_profit": round(final_pnl, 2),
            "final_pct_return": round(final_pct, 2),
            "lower_bound_10th": round(float(pct_10[-1]), 2),
            "upper_bound_90th": round(float(pct_90[-1]), 2),
            "breakdown_df": breakdown_df,
            "dates": [(start_date + pd.Timedelta(days=i)).strftime("%Y-%m-%d") for i in range(horizon_days + 1)],
            "corridors": {
                "mean": pct_mean.tolist(),
                "p10": pct_10.tolist(),
                "p25": pct_25.tolist(),
                "p50": pct_50.tolist(),
                "p75": pct_75.tolist(),
                "p90": pct_90.tolist()
            }
        }
