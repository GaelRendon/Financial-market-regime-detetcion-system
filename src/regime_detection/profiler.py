"""
Regime profiling module to interpret clusters and map them to financial regimes.
"""

import os
from typing import Dict, Optional
import pandas as pd


class RegimeProfiler:
    """Profiles clusters by statistical properties and maps them to descriptive regime names."""

    DEFAULT_REGIME_NAMES: Dict[int, str] = {
        0: "Moderate-Volatility Bullish",
        1: "Low-Volatility Neutral",
        2: "High-Volatility Transition",
        3: "High-Volatility Bearish"
    }

    def __init__(
        self,
        cluster_mapping: Optional[Dict[int, str]] = None,
        processed_data_path: str = "../data/processed"
    ):
        self.cluster_mapping = cluster_mapping or self.DEFAULT_REGIME_NAMES
        self.processed_data_path = processed_data_path

    def compute_cluster_profile(
        self,
        features_df: pd.DataFrame,
        clusters: pd.Series
    ) -> pd.DataFrame:
        """
        Compute mean and standard deviation of engineered features across clusters.
        """
        combined = features_df.copy()
        combined["Cluster"] = clusters

        profile_mean = combined.groupby("Cluster").mean()
        profile_std = combined.groupby("Cluster").std()

        profile = profile_mean.join(profile_std, lsuffix="_Mean", rsuffix="_Std")
        profile["Count"] = combined.groupby("Cluster").size()
        profile["Percentage"] = (profile["Count"] / len(combined)) * 100
        return profile

    def assign_regime_names(
        self,
        features_df: pd.DataFrame,
        clusters: pd.Series
    ) -> pd.DataFrame:
        """
        Create a comprehensive market regime dataset with cluster ids and descriptive regime names.
        """
        regime_df = features_df.copy()
        regime_df["Cluster"] = clusters
        regime_df["Market_Regime"] = regime_df["Cluster"].map(self.cluster_mapping)
        return regime_df

    def save_regime_dataset(self, regime_df: pd.DataFrame, ticker: str) -> str:
        """Save labeled market regime dataset to disk."""
        os.makedirs(self.processed_data_path, exist_ok=True)
        sanitized = ticker.lower().replace("-", "_")
        path = os.path.join(self.processed_data_path, f"{sanitized}_market_regime.csv")
        regime_df.to_csv(path, index=True)
        print(f"Saved market regime dataset ({len(regime_df)} rows) to: {path}")
        return path
