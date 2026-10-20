"""
End-to-End Pipeline Orchestrator for Financial Market Regime Detection System.
Executes the full quantitative workflow:
1. Data collection
2. Feature engineering
3. Standardization & PCA
4. K-Means clustering
5. Regime dynamics & persistence
6. Supervised regime forecasting
7. Causal backtesting & performance evaluation
"""

import os
import sys

# Ensure root directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from config.config import *
from src.data.collector import DataCollector
from src.data.loader import DataLoader
from src.features.feature_generator import FeatureGenerator
from src.preprocessing.scaler import DataScaler
from src.preprocessing.pca_transformer import PCATransformer
from src.clustering.kmeans_clusterer import KMeansClusterer
from src.clustering.evaluator import ClusterEvaluator
from src.regime_detection.profiler import RegimeProfiler
from src.regime_detection.dynamics import RegimeDynamics
from src.regime_forecasting.dataset_builder import ForecastingDatasetBuilder
from src.regime_forecasting.forecaster import RegimeForecaster
from src.backtesting.strategy import RegimeStrategy
from src.backtesting.metrics import PerformanceMetrics


def _resolve_project_path(rel_path: str) -> str:
    """Resolve paths whether called from notebooks/ or project root."""
    normalized = rel_path.replace("\\", "/")
    if normalized.startswith("../"):
        normalized = normalized[3:]
    return os.path.abspath(os.path.join(PROJECT_ROOT, normalized))


class RegimeDetectionPipeline:
    """Executes the complete pipeline end-to-end."""

    def __init__(self, ticker: str = "BTC-USD"):
        self.ticker = ticker
        self.sanitized_ticker = ticker.lower().replace("-", "_")

        # Resolve paths relative to project root
        self.raw_data_path = _resolve_project_path(RAW_DATA_PATH)
        self.processed_data_path = _resolve_project_path(PROCESSED_DATA_PATH)
        self.models_path = _resolve_project_path(MODELS_PATH)
        self.figures_path = _resolve_project_path(FIGURES_PATH)
        self.reports_path = _resolve_project_path(REPORTS_PATH)

    def run(self, download_fresh: bool = False):
        print("=" * 70)
        print(f"RUNNING REGIME DETECTION PIPELINE FOR {self.ticker}")
        print("=" * 70)

        # 1. Data Collection & Loading
        loader = DataLoader(
            raw_data_path=self.raw_data_path,
            processed_data_path=self.processed_data_path
        )
        if download_fresh:
            collector = DataCollector(
                assets=[self.ticker],
                start_date=START_DATE,
                end_date=END_DATE,
                interval=INTERVAL,
                raw_data_path=self.raw_data_path
            )
            collector.collect_all()

        raw_df = loader.load_raw_data(self.ticker, interval=INTERVAL)
        print(f"[1/7] Data Loaded: {raw_df.shape}")

        # 2. Feature Engineering
        fg = FeatureGenerator(
            volatility_window=VOLATILITY_WINDOW,
            momentum_window=MOMENTUM_WINDOW,
            processed_data_path=self.processed_data_path
        )
        features_df = fg.generate_features(raw_df)
        fg.save_features(features_df, self.ticker)
        print(f"[2/7] Features Generated: {features_df.shape}")

        # 3. Scaling & PCA
        scaler = DataScaler(models_path=self.models_path)
        scaled_df, _ = scaler.fit_transform(features_df)
        scaler.save_scaler(self.ticker)

        pca_tr = PCATransformer(
            variance_threshold=PCA_VARIANCE_THRESHOLD,
            models_path=self.models_path,
            processed_data_path=self.processed_data_path
        )
        pca_df, _ = pca_tr.fit_transform(scaled_df)
        pca_tr.save_pca(self.ticker)
        pca_tr.save_transformed_data(pca_df, self.ticker)
        print(f"[3/7] PCA Complete ({pca_df.shape[1]} components retained)")

        # 4. Clustering
        k = OPTIMAL_N_CLUSTERS or 4
        clusterer = KMeansClusterer(
            n_clusters=k,
            random_seed=RANDOM_SEED,
            models_path=self.models_path
        )
        clusters = clusterer.fit_predict(pca_df)
        clusterer.save_model(self.ticker)
        print(f"[4/7] K-Means Clustering Complete (K={k})")

        # 5. Regime Profiling & Dynamics
        profiler = RegimeProfiler(processed_data_path=self.processed_data_path)
        regime_df = profiler.assign_regime_names(features_df, clusters)
        profiler.save_regime_dataset(regime_df, self.ticker)

        dynamics = RegimeDynamics()
        trans_mat = dynamics.compute_transition_matrix(regime_df)
        persistence = dynamics.compute_persistence_statistics(trans_mat)
        print("[5/7] Regime Dynamics & Persistence computed")

        # 6. Forecasting
        builder = ForecastingDatasetBuilder(test_size=TEST_SIZE)
        fc_data = builder.build_dataset(regime_df)
        x_tr, x_te, y_tr, y_te = builder.chronological_train_test_split(fc_data)

        forecaster = RegimeForecaster(
            random_seed=RANDOM_SEED,
            models_path=self.models_path
        )
        forecaster.fit(x_tr, y_tr)
        eval_metrics = forecaster.evaluate(x_te, y_te)
        forecaster.save_model(self.ticker)
        print(f"[6/7] Forecasting Model Accuracy: {eval_metrics['accuracy']:.4f}")

        # 7. Backtesting
        strategy = RegimeStrategy()
        backtest_df = strategy.run_backtest(raw_df, regime_df)

        metrics = PerformanceMetrics(
            initial_capital=INITIAL_CAPITAL,
            risk_free_rate=RISK_FREE_RATE,
            trading_days_per_year=TRADING_DAYS_PER_YEAR
        )
        perf_summary = metrics.evaluate_performance(backtest_df)
        print("[7/7] Backtest Evaluation Complete:\n")
        print(perf_summary.to_string(index=False))

        print("\n" + "=" * 70)
        print("PIPELINE EXECUTION FINISHED SUCCESSFULLY")
        print("=" * 70)
        return perf_summary


if __name__ == "__main__":
    pipeline = RegimeDetectionPipeline(ticker="BTC-USD")
    pipeline.run(download_fresh=False)
