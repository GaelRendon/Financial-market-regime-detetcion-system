# ==========================================
# DATA COLLECTION CONFIGURATION
# ==========================================
ASSETS = [
    "BTC-USD"
]

START_DATE = "2018-01-01"
END_DATE = None
INTERVAL = "1d"

# ==========================================
# FEATURE ENGINEERING CONFIGURATION
# ==========================================
ENGINEERED_FEATURES = [
    "returns",
    "volatility",
    "momentum"
]

VOLATILITY_WINDOW = 30

MOMENTUM_WINDOW = 14

# ==========================================
# PCA CONFIGURATION
# ==========================================

# Keep enough components to explain 95% of the variance
PCA_VARIANCE_THRESHOLD = 0.95

# ==========================================
# CLUSTERING CONFIGURATION
# ==========================================

CLUSTERING_ALGORITHM = "kmeans"

N_CLUSTERS = 4

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