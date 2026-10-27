"""
Soft regime identification module supporting Gaussian Mixture Models (GMM)
and pure-NumPy Gaussian Hidden Markov Models (HMM) for probabilistic state estimation.
"""

import os
import pickle
from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.stats import multivariate_normal
from sklearn.mixture import GaussianMixture


class GMMClusterer:
    """Gaussian Mixture Model for soft, probabilistic regime clustering."""

    def __init__(
        self,
        n_clusters: int = 4,
        covariance_type: str = "full",
        random_seed: int = 42,
        models_path: str = "../outputs/models"
    ):
        self.n_clusters = n_clusters
        self.covariance_type = covariance_type
        self.random_seed = random_seed
        self.models_path = models_path
        self.model: Optional[GaussianMixture] = None

    def fit_predict_proba(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
        """
        Fit GMM and return both the most likely regime and the full posterior probability matrix.
        """
        self.model = GaussianMixture(
            n_components=self.n_clusters,
            covariance_type=self.covariance_type,
            random_state=self.random_seed,
            n_init=10
        )
        posteriors = self.model.fit_predict(data)
        proba_matrix = self.model.predict_proba(data)

        prob_cols = [f"Regime_{k}_Prob" for k in range(self.n_clusters)]
        prob_df = pd.DataFrame(proba_matrix, index=data.index, columns=prob_cols)
        regime_series = pd.Series(posteriors, index=data.index, name="Soft_Cluster")

        return regime_series, prob_df

    def compute_information_criteria(self, data: pd.DataFrame, max_k: int = 8) -> pd.DataFrame:
        """Evaluate optimal number of regimes using AIC and BIC."""
        records = []
        for k in range(2, max_k + 1):
            gmm = GaussianMixture(
                n_components=k,
                covariance_type=self.covariance_type,
                random_state=self.random_seed,
                n_init=5
            )
            gmm.fit(data)
            records.append({
                "K": k,
                "AIC": gmm.aic(data),
                "BIC": gmm.bic(data),
                "Log_Likelihood": gmm.score(data) * len(data)
            })
        return pd.DataFrame(records)

    def save_model(self, ticker: str) -> str:
        """Save fitted GMM model."""
        if self.model is None:
            raise ValueError("GMM model has not been fitted.")
        os.makedirs(self.models_path, exist_ok=True)
        sanitized = ticker.lower().replace("-", "_")
        path = os.path.join(self.models_path, f"{sanitized}_gmm.pkl")
        with open(path, "wb") as f:
            pickle.dump(self.model, f)
        return path


class GaussianHMM:
    """
    Pure NumPy/SciPy First-Order Gaussian Hidden Markov Model.
    Computes emission distributions, Baum-Welch expectation, and Viterbi path.
    Zero C++ dependencies required.
    """

    def __init__(
        self,
        n_states: int = 4,
        n_iter: int = 50,
        tol: float = 1e-4,
        random_seed: int = 42
    ):
        self.n_states = n_states
        self.n_iter = n_iter
        self.tol = tol
        self.random_seed = random_seed

        # Model parameters
        self.startprob_: Optional[np.ndarray] = None
        self.transmat_: Optional[np.ndarray] = None
        self.means_: Optional[np.ndarray] = None
        self.covars_: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray) -> "GaussianHMM":
        """
        Fit Gaussian HMM via Expectation-Maximization (Baum-Welch algorithm).
        """
        np.random.seed(self.random_seed)
        N, D = X.shape
        K = self.n_states

        # 1. Initialize parameters
        # Uniform initial probabilities
        self.startprob_ = np.ones(K) / K

        # Transition matrix with diagonal persistence bias
        diag_val = 0.85
        off_diag = (1.0 - diag_val) / (K - 1)
        self.transmat_ = np.full((K, K), off_diag)
        np.fill_diagonal(self.transmat_, diag_val)

        # Quantile-based centroid initialization
        quantiles = np.linspace(0.1, 0.9, K)
        self.means_ = np.quantile(X, quantiles, axis=0)

        # Diagonal covariance matrices with small regularization
        var_total = np.var(X, axis=0) + 1e-4
        self.covars_ = np.array([np.diag(var_total) for _ in range(K)])

        # EM Iterations
        prev_log_lik = -np.inf

        for it in range(self.n_iter):
            # Compute emissions: B[t, k] = N(X_t | mu_k, Sigma_k)
            B = np.zeros((N, K))
            for k in range(K):
                cov = self.covars_[k] + np.eye(D) * 1e-4
                rv = multivariate_normal(mean=self.means_[k], cov=cov, allow_singular=True)
                B[:, k] = np.maximum(rv.pdf(X), 1e-300)

            # Forward pass (scaled to prevent numerical underflow)
            alpha = np.zeros((N, K))
            c = np.zeros(N)

            alpha[0] = self.startprob_ * B[0]
            c[0] = np.sum(alpha[0])
            alpha[0] /= c[0]

            for t in range(1, N):
                alpha[t] = np.dot(alpha[t - 1], self.transmat_) * B[t]
                c[t] = np.sum(alpha[t]) + 1e-300
                alpha[t] /= c[t]

            log_lik = np.sum(np.log(c))

            # Backward pass
            beta = np.zeros((N, K))
            beta[-1] = 1.0

            for t in range(N - 2, -1, -1):
                beta[t] = np.dot(self.transmat_, B[t + 1] * beta[t + 1])
                beta[t] /= c[t + 1]

            # Posteriors (gamma) and transition posteriors (xi)
            gamma = alpha * beta
            gamma /= np.sum(gamma, axis=1, keepdims=True)

            xi = np.zeros((N - 1, K, K))
            for t in range(N - 1):
                numerator = (
                    alpha[t][:, np.newaxis]
                    * self.transmat_
                    * B[t + 1][np.newaxis, :]
                    * beta[t + 1][np.newaxis, :]
                )
                xi[t] = numerator / (np.sum(numerator) + 1e-300)

            # M-Step: Update parameters
            self.startprob_ = gamma[0]
            self.transmat_ = np.sum(xi, axis=0) / (np.sum(gamma[:-1], axis=0)[:, np.newaxis] + 1e-300)

            for k in range(K):
                gamma_k = gamma[:, k][:, np.newaxis]
                sum_gamma_k = np.sum(gamma_k) + 1e-300
                self.means_[k] = np.sum(gamma_k * X, axis=0) / sum_gamma_k
                diff = X - self.means_[k]
                cov_k = np.dot((gamma_k * diff).T, diff) / sum_gamma_k
                self.covars_[k] = cov_k + np.eye(D) * 1e-4

            if abs(log_lik - prev_log_lik) < self.tol:
                break
            prev_log_lik = log_lik

        return self

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Viterbi decoding for maximum a posteriori state sequence and smoothed probabilities.
        """
        N, D = X.shape
        K = self.n_states

        B = np.zeros((N, K))
        for k in range(K):
            cov = self.covars_[k] + np.eye(D) * 1e-4
            rv = multivariate_normal(mean=self.means_[k], cov=cov, allow_singular=True)
            B[:, k] = np.maximum(rv.pdf(X), 1e-300)

        # Viterbi DP
        viterbi = np.zeros((N, K))
        backpointer = np.zeros((N, K), dtype=int)

        viterbi[0] = np.log(self.startprob_ + 1e-300) + np.log(B[0])

        log_A = np.log(self.transmat_ + 1e-300)

        for t in range(1, N):
            for k in range(K):
                candidates = viterbi[t - 1] + log_A[:, k]
                best_prev = np.argmax(candidates)
                viterbi[t, k] = candidates[best_prev] + np.log(B[t, k])
                backpointer[t, k] = best_prev

        # Backtrack best path
        best_path = np.zeros(N, dtype=int)
        best_path[-1] = np.argmax(viterbi[-1])

        for t in range(N - 2, -1, -1):
            best_path[t] = backpointer[t + 1, best_path[t + 1]]

        # Posterior smoothed probabilities
        log_B = np.log(B)
        smoothed = np.exp(viterbi - np.max(viterbi, axis=1, keepdims=True))
        smoothed /= np.sum(smoothed, axis=1, keepdims=True)

        return best_path, smoothed
