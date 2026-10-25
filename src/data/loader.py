"""
Data loader module for reading and parsing raw and processed datasets.
"""

import os
import pandas as pd


class DataLoader:
    """Loads and validates historical raw and processed time-series datasets."""

    def __init__(
        self,
        raw_data_path: str = "../data/raw",
        processed_data_path: str = "../data/processed"
    ):
        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path

    def load_raw_data(self, ticker: str, interval: str = "1d") -> pd.DataFrame:
        """
        Load raw market data CSV for an asset and set DateTime index.
        """
        sanitized = ticker.lower().replace("-", "_")
        filename = f"{sanitized}_{interval}_raw.csv"
        path = os.path.join(self.raw_data_path, filename)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Raw data file not found: {path}")

        df = pd.read_csv(path)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            df.set_index("Date", inplace=True)

        return df

    def load_processed_data(self, ticker: str, dataset_type: str = "features") -> pd.DataFrame:
        """
        Load processed CSV (e.g. features, pca, market_regime).
        """
        sanitized = ticker.lower().replace("-", "_")
        filename = f"{sanitized}_{dataset_type}.csv"
        path = os.path.join(self.processed_data_path, filename)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Processed dataset not found: {path}")

        df = pd.read_csv(path)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            df.set_index("Date", inplace=True)

        return df
