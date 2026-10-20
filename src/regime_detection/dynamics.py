"""
Regime dynamics module for computing transition matrices, persistence, and ergodic distributions.
"""

from typing import Tuple
import numpy as np
import pandas as pd


class RegimeDynamics:
    """Analyzes temporal behavior, Markov transitions, and persistence of market regimes."""

    def __init__(self, regime_col: str = "Market_Regime"):
        self.regime_col = regime_col

    def compute_transition_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute empirical transition probability matrix P_ij = P(S_{t+1} = j | S_t = i).
        """
        current_state = df[self.regime_col]
        next_state = df[self.regime_col].shift(-1)

        transition_matrix = pd.crosstab(
            current_state,
            next_state,
            normalize="index"
        )
        return transition_matrix

    def compute_persistence_statistics(self, transition_matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Compute self-transition probability (P_ii) and expected duration E[T_i] = 1 / (1 - P_ii).
        """
        regimes = transition_matrix.index
        persistence_data = []

        for regime in regimes:
            if regime in transition_matrix.columns:
                p_ii = transition_matrix.loc[regime, regime]
                expected_days = 1.0 / (1.0 - p_ii) if p_ii < 1.0 else np.nan
            else:
                p_ii = 0.0
                expected_days = 1.0

            persistence_data.append({
                "Market_Regime": regime,
                "Self_Transition_Prob": p_ii,
                "Expected_Duration_Days": expected_days
            })

        return pd.DataFrame(persistence_data).set_index("Market_Regime")

    def compute_stationary_distribution(self, transition_matrix: pd.DataFrame) -> pd.Series:
        """
        Calculate unique ergodic stationary distribution pi such that pi * P = pi.
        """
        p_matrix = transition_matrix.values
        # Eigen decomposition of P^T
        evals, evecs = np.linalg.eig(p_matrix.T)
        # Find eigenvector corresponding to eigenvalue 1
        unit_eigen_idx = np.argmin(np.abs(evals - 1.0))
        stationary_vec = np.real(evecs[:, unit_eigen_idx])
        # Normalize so sum = 1
        stationary_vec = stationary_vec / np.sum(stationary_vec)
        return pd.Series(stationary_vec, index=transition_matrix.index, name="Stationary_Prob")
