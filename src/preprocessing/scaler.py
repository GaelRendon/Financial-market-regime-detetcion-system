"""
Feature scaling module using StandardScaler.
"""

import os
import pickle
from typing import Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class DataScaler:
    """Standardizes feature matrices to zero mean and unit variance via global or rolling normalization."""

    def __init__(self, models_path: str = "../outputs/models"):
        self.models_path = models_path
        self.scaler: Optional[StandardScaler] = None

    def fit_transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, StandardScaler]:
        """Fit scaler on feature dataframe and return standardized DataFrame."""
        self.scaler = StandardScaler()
        scaled_array = self.scaler.fit_transform(df)
        scaled_df = pd.DataFrame(
            scaled_array,
            index=df.index,
            columns=df.columns
        )
        return scaled_df, self.scaler

    def rolling_transform(
        self,
        df: pd.DataFrame,
        window: int = 252,
        min_periods: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Standardize features using causal rolling z-scores over the specified window (default: 252 days).
        Ensures local variance adaptation and eliminates historical regime dominance bias.
        """
        if min_periods is None:
            min_periods = max(30, window // 4)

        roll_mean = df.rolling(window=window, min_periods=min_periods).mean()
        roll_std = df.rolling(window=window, min_periods=min_periods).std()
        roll_std = roll_std.replace(0, np.nan).fillna(1e-8)

        scaled_df = (df - roll_mean) / roll_std
        return scaled_df.dropna()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform new data using the pre-fitted scaler."""
        if self.scaler is None:
            raise ValueError("Scaler has not been fitted or loaded yet.")
        scaled_array = self.scaler.transform(df)
        return pd.DataFrame(
            scaled_array,
            index=df.index,
            columns=df.columns
        )

    def save_scaler(self, ticker: str) -> str:
        """Persist fitted scaler to disk."""
        if self.scaler is None:
            raise ValueError("No fitted scaler to save.")
        os.makedirs(self.models_path, exist_ok=True)
        sanitized = ticker.lower().replace("-", "_")
        path = os.path.join(self.models_path, f"{sanitized}_scaler.pkl")
        with open(path, "wb") as f:
            pickle.dump(self.scaler, f)
        print(f"Saved scaler to: {path}")
        return path

    def load_scaler(self, ticker: str) -> StandardScaler:
        """Load pre-fitted scaler from disk."""
        sanitized = ticker.lower().replace("-", "_")
        path = os.path.join(self.models_path, f"{sanitized}_scaler.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Scaler not found at: {path}")
        with open(path, "rb") as f:
            self.scaler = pickle.load(f)
        return self.scaler
