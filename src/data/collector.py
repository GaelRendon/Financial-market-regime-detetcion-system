"""
Data collection module for fetching financial market data via Yahoo Finance.
Supports asset-specific start dates, robust path resolution, and zero-price filtering.
"""

import os
import sys
from typing import List, Optional, Dict, Union
import pandas as pd
import yfinance as yf

# Resolve project paths dynamically
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from config.config import RAW_DATA_PATH, START_DATE, ASSET_START_DATES


class DataCollector:
    """Collects historical market data for designated assets with per-coin start date handling."""

    def __init__(
        self,
        assets: Optional[List[str]] = None,
        start_date: Optional[Union[str, Dict[str, str]]] = None,
        end_date: Optional[str] = None,
        interval: str = "1d",
        raw_data_path: Optional[str] = None
    ):
        self.assets = assets or ["BTC-USD"]
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        
        # Robust absolute path resolution
        if raw_data_path is None:
            self.raw_data_path = RAW_DATA_PATH
        elif os.path.isabs(raw_data_path):
            self.raw_data_path = raw_data_path
        else:
            # Resolve relative path against project root
            self.raw_data_path = os.path.abspath(os.path.join(PROJECT_ROOT, raw_data_path))

    def _get_start_date_for_asset(self, ticker: str) -> Optional[str]:
        """Determine individual start date for a specific asset to avoid downloading artificial zeros."""
        if isinstance(self.start_date, dict):
            return self.start_date.get(ticker) or ASSET_START_DATES.get(ticker, START_DATE)
        elif isinstance(self.start_date, str):
            # If a global start date was provided, still verify if the asset existed then
            coin_inception = ASSET_START_DATES.get(ticker)
            if coin_inception and coin_inception > self.start_date:
                return coin_inception
            return self.start_date
        else:
            return ASSET_START_DATES.get(ticker, START_DATE)

    def download_asset(self, ticker: str) -> pd.DataFrame:
        """
        Download historical OHLCV data for a single asset with sanitized inception dates.
        """
        effective_start = self._get_start_date_for_asset(ticker)
        print(f"Downloading historical data for {ticker} from {effective_start} to {self.end_date or 'today'}...")
        
        download_kwargs = {
            "tickers": ticker,
            "interval": self.interval,
            "progress": False
        }
        if effective_start:
            download_kwargs["start"] = effective_start
        else:
            download_kwargs["period"] = "max"

        if self.end_date:
            download_kwargs["end"] = self.end_date

        df = yf.download(**download_kwargs)

        if df.empty:
            raise ValueError(f"No data returned for ticker '{ticker}'. Please verify ticker and date range.")

        # Handle multi-level column indexing from recent yfinance versions
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Sanitize data: filter out non-trading zero or negative prices and NaNs
        if "Close" in df.columns:
            df = df[df["Close"] > 0].copy()
            df = df.dropna(subset=["Close"]).copy()

        if df.empty:
            raise ValueError(f"Ticker '{ticker}' returned zero valid price rows after filtering non-trading days.")

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
