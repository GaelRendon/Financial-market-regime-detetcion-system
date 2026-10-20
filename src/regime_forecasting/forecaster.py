"""
Regime forecasting model trainer, evaluator, and inference engine.
"""

import os
import pickle
from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


class RegimeForecaster:
    """Trains Random Forest classifier to predict next-period market regimes."""

    def __init__(
        self,
        n_estimators: int = 100,
        random_seed: int = 42,
        models_path: str = "../outputs/models"
    ):
        self.n_estimators = n_estimators
        self.random_seed = random_seed
        self.models_path = models_path
        self.model: Optional[RandomForestClassifier] = None

    def fit(self, x_train: pd.DataFrame, y_train: pd.Series) -> RandomForestClassifier:
        """Fit Random Forest classifier on training data."""
        self.model = RandomForestClassifier(
            n_estimators=self.n_estimators,
            random_state=self.random_seed
        )
        self.model.fit(x_train, y_train)
        return self.model

    def evaluate(self, x_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, object]:
        """
        Evaluate model on out-of-sample test set.
        """
        if self.model is None:
            raise ValueError("Model is not fitted yet.")

        y_pred = self.model.predict(x_test)
        acc = float(accuracy_score(y_test, y_pred))
        report = classification_report(y_test, y_pred, output_dict=True)
        conf_mat = confusion_matrix(y_test, y_pred)

        return {
            "accuracy": acc,
            "classification_report": report,
            "confusion_matrix": conf_mat,
            "predictions": y_pred
        }

    def predict_next(self, current_features: pd.DataFrame) -> Tuple[int, np.ndarray]:
        """
        Predict the next regime and class probabilities for the most recent observation.
        """
        if self.model is None:
            raise ValueError("Model is not fitted yet.")

        pred = int(self.model.predict(current_features)[-1])
        probs = self.model.predict_proba(current_features)[-1]
        return pred, probs

    def save_model(self, ticker: str) -> str:
        """Persist fitted forecasting model to disk."""
        if self.model is None:
            raise ValueError("No model fitted to save.")
        os.makedirs(self.models_path, exist_ok=True)
        sanitized = ticker.lower().replace("-", "_")
        path = os.path.join(self.models_path, f"{sanitized}_forecaster.pkl")
        with open(path, "wb") as f:
            pickle.dump(self.model, f)
        print(f"Saved forecasting model to: {path}")
        return path
