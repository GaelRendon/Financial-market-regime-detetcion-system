"""
Dataset builder for preparing supervised forecasting data without look-ahead bias.
"""

from typing import List, Tuple
import pandas as pd
from sklearn.preprocessing import LabelEncoder


class ForecastingDatasetBuilder:
    """Prepares supervised target variable, encodes categories, and performs temporal split."""

    def __init__(
        self,
        feature_columns: List[str] = None,
        test_size: float = 0.20
    ):
        self.feature_columns = feature_columns or ["Returns", "Volatility", "Momentum", "Market_Regime_Encoded"]
        self.test_size = test_size
        self.regime_encoder = LabelEncoder()
        self.target_encoder = LabelEncoder()

    def build_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create next-day target, encode categorical regimes, and return clean supervised dataset.
        """
        data = df.copy()
        data["Next_Market_Regime"] = data["Market_Regime"].shift(-1)
        data = data.dropna(subset=["Next_Market_Regime"]).copy()

        # Label encoding
        data["Market_Regime_Encoded"] = self.regime_encoder.fit_transform(data["Market_Regime"])
        data["Next_Market_Regime_Encoded"] = self.target_encoder.fit_transform(data["Next_Market_Regime"])
        return data

    def chronological_train_test_split(
        self,
        data: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Perform chronological non-shuffled train/test split.
        """
        x = data[self.feature_columns]
        y = data["Next_Market_Regime_Encoded"]

        split_idx = int(len(data) * (1 - self.test_size))

        x_train = x.iloc[:split_idx]
        x_test = x.iloc[split_idx:]
        y_train = y.iloc[:split_idx]
        y_test = y.iloc[split_idx:]

        return x_train, x_test, y_train, y_test
