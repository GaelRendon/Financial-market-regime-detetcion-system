import os

# ==========================================
# ROOT DIRECTORY PATH RESOLUTION
# ==========================================
# Compute absolute paths relative to project root regardless of where scripts are executed
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CONFIG_DIR, ".."))

# ==========================================
# DATA COLLECTION CONFIGURATION
# ==========================================
ASSETS = [
    "BTC-USD", 
]

# The default baseline start date for assets with deep history
START_DATE = "2018-01-01"
END_DATE = None

# Individual asset inception dates on Yahoo Finance.
# Newer assets (e.g. Solana, Avalanche, Polkadot) did not trade in 2018;
# defining their true launch dates avoids downloading artificial zero-price rows.
ASSET_START_DATES = {
    "BTC-USD": "2018-01-01",
    "ETH-USD": "2018-01-01",
    "BNB-USD": "2018-01-01",
    "SOL-USD": "2020-04-10",
    "ADA-USD": "2018-01-01",
    "DOGE-USD": "2018-01-01",
    "XRP-USD": "2018-01-01",
    "AVAX-USD": "2020-09-22",
    "DOT-USD": "2020-08-20",
    "LINK-USD": "2018-01-01",
    "MATIC-USD": "2019-04-28",
    "POL-USD": "2019-04-28"
}

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
# This value is set programmatically in notebook 05.
OPTIMAL_N_CLUSTERS = 4


# This is used to ensure consistency of the results
RANDOM_SEED = 42

# ==========================================
# FORECASTING CONFIGURATION
# ==========================================

# Train-test split ratio for the forecasting model.
TEST_SIZE = 0.2

# ==========================================
# BACKTESTING CONFIGURATION
# ==========================================

# Initial hypothetical capital for backtesting.
INITIAL_CAPITAL = 1000

# Annual risk-free rate used for Sharpe Ratio calculation.
RISK_FREE_RATE = 0.0

# Approximate number of trading days per year (crypto trades 365 days).
TRADING_DAYS_PER_YEAR = 365

# Transaction fees in basis points (1 bps = 0.01% = 0.0001).
# 10 bps is standard spot taker fee on major exchanges (Binance, Coinbase, Kraken).
TRANSACTION_FEE_BPS = 10.0

# Estimated execution slippage in basis points.
SLIPPAGE_BPS = 5.0

# ==========================================
# MULTI-ASSET PORTFOLIO ALLOCATION CONFIGURATION
# ==========================================

# Cross-sectional asset universe for multi-coin portfolio allocation
MULTI_ASSET_UNIVERSE = ["BTC-USD", "ETH-USD", "SOL-USD"]

# Default multi-asset allocation strategy:
# "equal_weight", "regime_proportional", "top_k_momentum_regime", "risk_parity_regime"
DEFAULT_MULTI_ASSET_STRATEGY = "regime_proportional"

# Number of top assets to select in Top-K Cross-Sectional Momentum
MULTI_ASSET_TOP_K = 2

# Trailing momentum window (in days) for cross-sectional ranking
MULTI_ASSET_MOMENTUM_LOOKBACK = 14

# ==========================================
# OUTPUT CONFIGURATION
# ==========================================

# Standardized absolute directories anchored to project root
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed")
FIGURES_PATH = os.path.join(PROJECT_ROOT, "outputs", "figures")
REPORTS_PATH = os.path.join(PROJECT_ROOT, "outputs", "reports")
MODELS_PATH = os.path.join(PROJECT_ROOT, "outputs", "models")
