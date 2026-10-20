"""
K-Means clusterer for market regime identification.
"""

import os
import pickle
from typing import Optional
import pandas as pd
from sklearn.cluster import KMeans


class KMeansClusterer:
    """Partitions observations into K market regimes via K-Means."""

    def __init__(
        self,
        n_clusters: int = 4,
        random_seed: int = 42,
        models_path: str = "../outputs/models"
    ):
        self.n_clusters = n_clusters
        self.random_seed = random_seed
        self.models_path = models_path
        self.model: Optional[KMeans] = None

    def fit_predict(self, data: pd.DataFrame) -> pd.Series:
        """Fit K-Means model and return cluster assignments as a Series."""
        self.model = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_seed,
            n_init=10
        )
        labels = self.model.fit_predict(data)
        return pd.Series(labels, index=data.index, name="Cluster")

    def save_model(self, ticker: str) -> str:
        """Persist fitted K-Means model to disk."""
        if self.model is None:
            raise ValueError("K-Means model has not been fitted.")
        os.makedirs(self.models_path, exist_ok=True)
        sanitized = ticker.lower().replace("-", "_")
        path = os.path.join(self.models_path, f"{sanitized}_kmeans.pkl")
        with open(path, "wb") as f:
            pickle.dump(self.model, f)
        print(f"Saved KMeans model to: {path}")
        return path

    def load_model(self, ticker: str) -> KMeans:
        """Load pre-fitted K-Means model from disk."""
        sanitized = ticker.lower().replace("-", "_")
        path = os.path.join(self.models_path, f"{sanitized}_kmeans.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found at: {path}")
        with open(path, "rb") as f:
            self.model = pickle.load(f)
        return self.model
