"""
Feature generation module calculating returns, rolling volatility, and momentum.
"""

import os
import pandas as pd


class FeatureGenerator:
    """Calculates stationary engineered features from raw market prices."""

    def __init__(
        self,
        volatility_window: int = 30,
        momentum_window: int = 14,
        processed_data_path: str = "../data/processed"
    ):
        self.volatility_window = volatility_window
        self.momentum_window = momentum_window
        self.processed_data_path = processed_data_path

    def compute_returns(self, df: pd.DataFrame, price_col: str = "Close") -> pd.Series:
        """
        Compute daily simple returns: r_t = (P_t - P_{t-1}) / P_{t-1}
        """
        return df[price_col].pct_change()

    def compute_volatility(self, returns: pd.Series) -> pd.Series:
        """
        Compute rolling sample standard deviation over the volatility window.
        """
        return returns.rolling(window=self.volatility_window).std()

    def compute_momentum(self, df: pd.DataFrame, price_col: str = "Close") -> pd.Series:
        """
        Compute rate of change momentum: M_t = P_t / P_{t - window} - 1
        """
        return (df[price_col] / df[price_col].shift(self.momentum_window)) - 1

    def generate_features(self, df: pd.DataFrame, price_col: str = "Close") -> pd.DataFrame:
        """
        Compute all engineered features and drop initial NaN values caused by rolling windows.
        """
        features_df = pd.DataFrame(index=df.index)
        features_df["Returns"] = self.compute_returns(df, price_col)
        features_df["Volatility"] = self.compute_volatility(features_df["Returns"])
        features_df["Momentum"] = self.compute_momentum(df, price_col)

        # Drop initial NaN rows due to lookback windows
        clean_features = features_df.dropna().copy()
        return clean_features

    def save_features(self, df_features: pd.DataFrame, ticker: str) -> str:
        """Save clean features to processed data directory."""
        os.makedirs(self.processed_data_path, exist_ok=True)
        sanitized = ticker.lower().replace("-", "_")
        filename = f"{sanitized}_features.csv"
        path = os.path.join(self.processed_data_path, filename)
        df_features.to_csv(path, index=True)
        print(f"Saved engineered features ({len(df_features)} rows) to: {path}")
        return path
