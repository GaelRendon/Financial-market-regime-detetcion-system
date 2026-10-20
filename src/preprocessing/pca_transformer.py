"""
Principal Component Analysis (PCA) transformer module.
"""

import os
import pickle
from typing import Optional, Tuple
import pandas as pd
from sklearn.decomposition import PCA


class PCATransformer:
    """Performs dimensionality reduction via PCA based on explained variance threshold."""

    def __init__(
        self,
        variance_threshold: float = 0.95,
        models_path: str = "../outputs/models",
        processed_data_path: str = "../data/processed"
    ):
        self.variance_threshold = variance_threshold
        self.models_path = models_path
        self.processed_data_path = processed_data_path
        self.pca: Optional[PCA] = None

    def fit_transform(self, df_scaled: pd.DataFrame) -> Tuple[pd.DataFrame, PCA]:
        """
        Fit PCA model to explain at least `variance_threshold` of variance and transform data.
        """
        self.pca = PCA(n_components=self.variance_threshold)
        transformed_array = self.pca.fit_transform(df_scaled)
        
        n_components = self.pca.n_components_
        col_names = [f"PC{i+1}" for i in range(n_components)]

        pca_df = pd.DataFrame(
            transformed_array,
            index=df_scaled.index,
            columns=col_names
        )
        return pca_df, self.pca

    def get_loadings(self, feature_names: list) -> pd.DataFrame:
        """Extract PCA component factor loadings (eigenvector weights)."""
        if self.pca is None:
            raise ValueError("PCA model has not been fitted.")
        col_names = [f"PC{i+1}" for i in range(self.pca.n_components_)]
        loadings_df = pd.DataFrame(
            self.pca.components_.T,
            index=feature_names,
            columns=col_names
        )
        return loadings_df

    def save_pca(self, ticker: str) -> str:
        """Persist fitted PCA model to disk."""
        if self.pca is None:
            raise ValueError("No fitted PCA model to save.")
        os.makedirs(self.models_path, exist_ok=True)
        sanitized = ticker.lower().replace("-", "_")
        path = os.path.join(self.models_path, f"{sanitized}_pca.pkl")
        with open(path, "wb") as f:
            pickle.dump(self.pca, f)
        print(f"Saved PCA model to: {path}")
        return path

    def save_transformed_data(self, pca_df: pd.DataFrame, ticker: str) -> str:
        """Save PCA projection dataset to disk."""
        os.makedirs(self.processed_data_path, exist_ok=True)
        sanitized = ticker.lower().replace("-", "_")
        path = os.path.join(self.processed_data_path, f"{sanitized}_pca.csv")
        pca_df.to_csv(path, index=True)
        print(f"Saved PCA data ({len(pca_df)} rows) to: {path}")
        return path
