"""
Cluster evaluation module computing Inertia (Elbow Method) and Silhouette Scores.
"""

from typing import Dict, List, Tuple
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


class ClusterEvaluator:
    """Evaluates clustering quality across a range of cluster counts."""

    def __init__(
        self,
        min_clusters: int = 2,
        max_clusters: int = 10,
        random_seed: int = 42
    ):
        self.min_clusters = min_clusters
        self.max_clusters = max_clusters
        self.random_seed = random_seed

    def evaluate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Compute Inertia and Silhouette Score for K in [min_clusters, max_clusters].
        """
        k_values: List[int] = []
        inertia_scores: List[float] = []
        silhouette_scores: List[float] = []

        for k in range(self.min_clusters, self.max_clusters + 1):
            kmeans = KMeans(
                n_clusters=k,
                random_state=self.random_seed,
                n_init=10
            )
            labels = kmeans.fit_predict(data)

            k_values.append(k)
            inertia_scores.append(float(kmeans.inertia_))
            silhouette_scores.append(float(silhouette_score(data, labels)))

        evaluation_df = pd.DataFrame({
            "K": k_values,
            "Inertia": inertia_scores,
            "Silhouette Score": silhouette_scores
        })
        return evaluation_df
