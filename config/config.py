# ==========================================
# DATA COLLECTION CONFIGURATION
# ==========================================
ASSETS = [
    "BTC-USD", 
]

# The start and end dates for the data collection. These can be adjusted based on the desired time frame for analysis.
START_DATE = "2018-01-01"
END_DATE = None

# The interval for the data collection. This can be adjusted based on the desired granularity of the data (e.g., "1d" for daily, "1h" for hourly).
INTERVAL = "1d"

# ==========================================
# FEATURE ENGINEERING CONFIGURATION
# ==========================================
ENGINEERED_FEATURES = [
    "returns",
    "volatility",
    "momentum"
]

# The window size for calculating volatility and momentum features. This is a hyperparameter that can be tuned.
VOLATILITY_WINDOW = 30

# The window size for calculating momentum features. This is a hyperparameter that can be tuned.
MOMENTUM_WINDOW = 14

# ==========================================
# PCA CONFIGURATION
# ==========================================

# Keep enough components to explain 95% of the variance
PCA_VARIANCE_THRESHOLD = 0.95

# ==========================================
# CLUSTERING CONFIGURATION
# ==========================================

# Clustering algorithm used throughout the project.
CLUSTERING_ALGORITHM = "kmeans"

# Range of candidate clusters evaluated during model selection.
MIN_CLUSTERS = 2
MAX_CLUSTERS = 10

# Final number of clusters selected after the
# Elbow Method and Silhouette Score analyses.
OPTIMAL_N_CLUSTERS = None


# This is used to ensure consistency of the results
RANDOM_SEED = 42

# ==========================================
# OUTPUT CONFIGURATION
# ==========================================

RAW_DATA_PATH = "../data/raw"
PROCESSED_DATA_PATH = "../data/processed"
FIGURES_PATH = "../outputs/figures"
REPORTS_PATH = "../outputs/reports"
MODELS_PATH = "../outputs/models"