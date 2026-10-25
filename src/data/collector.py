"""
Data collection module for fetching financial market data via Yahoo Finance.
"""

import os
from typing import List, Optional
import pandas as pd
import yfinance as yf


class DataCollector:
    """Collects historical market data for designated assets."""

    def __init__(
        self,
        assets: Optional[List[str]] = None,
        start_date: str = "2018-01-01",
        end_date: Optional[str] = None,
        interval: str = "1d",
        raw_data_path: str = "../data/raw"
    ):
        self.assets = assets or ["BTC-USD"]
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.raw_data_path = raw_data_path

    def download_asset(self, ticker: str) -> pd.DataFrame:
        """
        Download historical OHLCV data for a single asset.
        """
        print(f"Downloading historical data for {ticker} from {self.start_date} to {self.end_date or 'today'}...")
        df = yf.download(
            tickers=ticker,
            start=self.start_date,
            end=self.end_date,
            interval=self.interval,
            progress=False
        )

        if df.empty:
            raise ValueError(f"No data returned for ticker '{ticker}'. Please verify ticker and date range.")

        # Handle multi-level column indexing from recent yfinance versions
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.index.name = "Date"
        df.reset_index(inplace=True)
        return df

    def save_raw_data(self, df: pd.DataFrame, ticker: str) -> str:
        """Save downloaded raw asset data to CSV."""
        os.makedirs(self.raw_data_path, exist_ok=True)
        sanitized_name = ticker.lower().replace("-", "_")
        filename = f"{sanitized_name}_{self.interval}_raw.csv"
        file_path = os.path.join(self.raw_data_path, filename)
        df.to_csv(file_path, index=False)
        print(f"Saved raw data for {ticker} ({len(df)} rows) to: {file_path}")
        return file_path

    def collect_all(self) -> List[str]:
        """Collect and save data for all configured assets."""
        saved_paths = []
        for asset in self.assets:
            df = self.download_asset(asset)
            path = self.save_raw_data(df, asset)
            saved_paths.append(path)
        return saved_paths
