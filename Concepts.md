# Concepts that you should know to understand this project:

## 1. What Does OHLCV Data Mean?
OHLCV refers to the standard format for financial price data. It helps us track how a stock or crypto asset moved over a specific timeframe, and the letters stand for:

- O (Open): The price at the start of the timeframe.
- H (High): The highest price reached during the timeframe.
- L (Low): The lowest price reached during the timeframe.
- C (Close): The price at the end of the timeframe.
- V (Volume): The total number of shares or coins traded during that time.

**Why does this matter to us?**  
If we look at a standard candlestick chart, each "candle" is built entirely from OHLCV data. The body shows the Open and Close, the wicks show the High and Low, and the Volume is often displayed separately below the chart.

---

## 2. Simple Returns vs Log Returns
When calculating how much money an asset gained or lost, quantitative traders use two main methods:

| Feature | Simple Returns | Log Returns |
|--------|----------------|-------------|
| Formula | $\frac{Price_{today} - Price_{yesterday}}{Price_{yesterday}}$ | $\ln(Price_{today}) - \ln(Price_{yesterday})$ |
| Interpretation | Intuitive percentage change (e.g., “+5% today”) | Continuous return used for modeling |
| Advantage | Easy to understand | Time-additive (can be summed over time periods) |

**Why log returns are useful for coding:**  
If a price goes from 100 → 110 (+10%), then back from 110 → 100 (-9.09%), simple returns do not cancel out symmetrically. Log returns, however, properly accumulate over time and behave consistently in mathematical models.

---

## 3. Why Traders Care About Volatility
Volatility measures how much and how quickly an asset’s price fluctuates. Think of it as the “speed of risk.”

Traders care about it for three main reasons:

- **Risk Management:** Higher volatility means higher potential gains but also higher potential losses.
- **Options Pricing:** Financial derivatives become more expensive when volatility increases.
- **Strategy Selection:** Some strategies perform better in high-volatility markets, while others prefer stable conditions.

---

## 4. What Momentum Means
Momentum measures the strength and direction of a price trend over a given period.

The main idea is:

- Assets that have been rising tend to continue rising.
- Assets that have been falling tend to continue falling.

A common way to calculate momentum is:

\[
Momentum = Price_t - Price_{t-n}
\]

or in normalized form:

\[
Momentum = \frac{Price_t}{Price_{t-n}} - 1
\]

**Why this matters to us:**  
Momentum is one of the main features in this project. It helps distinguish:
- Strong uptrends
- Strong downtrends
- Neutral markets

even when volatility is similar.

---

## 5. What Feature Engineering Means
Feature engineering is the process of creating meaningful variables from raw data.

Raw financial data usually contains:
- Open
- High
- Low
- Close
- Volume

However, machine learning models perform better when we transform this raw data into descriptive features such as:
- Returns
- Volatility
- Momentum
- Moving averages
- RSI
- MACD

**Why this matters to us:**  
Instead of feeding raw prices into the model, we create features that describe:
- Performance
- Risk
- Trend strength

This improves the ability of algorithms to detect market behavior.

---

## 6. Why Scaling is Important
Machine learning algorithms are sensitive to the scale of variables.

For example:
- Returns: -0.05 to 0.05
- Volume: 0 to 50,000,000

Without scaling, the model will overweight larger numerical values like volume.

A common method is standardization:
- Mean = 0
- Standard deviation = 1

**Why this matters to us:**  
Both PCA (indirectly) and K-Means depend on distance-based relationships. If features are not scaled properly, the model may detect patterns based only on magnitude rather than meaningful structure.

---

## 7. What Principal Component Analysis (PCA) Does
Principal Component Analysis (PCA) is a dimensionality reduction technique.

Instead of analyzing multiple correlated variables separately, PCA creates new variables called principal components that capture the most important variation in the data.

For this project:
- Returns
- Volatility
- Momentum

are transformed into:
- PC1
- PC2
- PC3

Each component represents a combination of the original features.

**Why this matters to us:**  
PCA helps:
- Reduce noise
- Remove redundancy
- Simplify visualization
- Improve clustering performance

while preserving most of the important information.

---

## 8. What a Market Regime Is
A market regime is a period during which the market behaves in a relatively consistent way.

Examples include:
- Bull market
- Bear market
- Sideways market
- High volatility market
- Low volatility market

Different regimes often require different trading strategies. A strategy that works well in a bull market may fail in a volatile or bearish environment.

**Why this matters to us:**  
The main objective of this project is to automatically identify market regimes using machine learning.

---

## 9. What Clustering Means
Clustering is an unsupervised machine learning technique used to group similar observations together without labeled data.

Instead of being told what to look for, the algorithm finds patterns in the data and groups similar points.

For example:
- Group A: High returns, low volatility
- Group B: Negative returns, high volatility

**Why this matters to us:**  
We use clustering to discover hidden market regimes in financial data based on engineered features.

---

## 10. What K-Means Clustering Does
K-Means is one of the most popular clustering algorithms.

It works by:
- Initializing K cluster centers (centroids)
- Assigning each point to the nearest centroid
- Updating centroids based on assigned points
- Repeating until convergence

The goal is to minimize the distance between points and their assigned cluster center.

**Why this matters to us:**  
K-Means will be used to identify market regimes. Once clusters are formed, we will analyze their behavior to interpret whether they represent:
- Bull markets
- Bear markets
- Sideways markets
- Other market behaviors

## 11. Why Dimensionality Reduction Is Needed

Financial features often contain overlapping information. For example, returns and momentum are both related to price movement, while volatility may partially reflect recent market behavior.

When several variables describe similar information, machine learning algorithms can become less efficient and more sensitive to noise.

Dimensionality reduction aims to summarize the information contained in multiple correlated features using a smaller set of variables while preserving most of the original variation.

**Why this matters to us:**
PCA allows us to simplify the feature space before clustering, reducing redundancy while retaining the information needed to identify market regimes.

## 12. What the Elbow Method Does
The Elbow Method helps estimate the appropriate number of clusters for K-Means. 

It measures the Within-Clusters Sum of Squares (WCSS) for different values of K. As K increases, WCSS decreases because observations are grouped more precisely.

The optimal number of clusters is often identified at the point where adding additional clusters provides only a small improvement, producing an "elbow" in the curve.

**Why this matters to us:**
Rather than selecting the number of clusters arbitrarily, we use the Elbow Method as one piece of evidence for determining an appropriate clustering solution.

## 13. What the Silhouette Score Measures

The Silhouette Score evaluates how well observations fit within their assigned cluster.

The score ranges from -1 to 1:

- Close to 1: Well-separated clusters
- Around 0: Overlapping clusters
- Below 0: Possible misclassification

Unlike the Elbow Method, which focuses on compactness, the Silhouette Score also considers how distinct clusters are from one another.

**Why this matters to us:**
We combine the Silhouette Score with the Elbow Method to select a clustering solution that balances compactness and separation.


---

## 14. What a Transition Matrix Represents

A transition matrix captures the probability of moving from one market regime to another over consecutive time steps.

Each row represents the current regime, and each column represents the next regime. The values indicate the likelihood of transitioning between states:

| From \ To | Bull | Bear | High Volatility | Consolidation |
|-----------|------|------|-----------------|---------------|
| Bull | 0.85 | 0.05 | 0.05 | 0.05 |
| Bear | 0.10 | 0.70 | 0.15 | 0.05 |
| ... | ... | ... | ... | ... |

This concept is closely related to Markov Chains, where the next state depends only on the current state, not on the history of previous states.

**Why this matters to us:**
Transition matrices allow us to quantify how likely it is for the market to shift between regimes, providing insights into market stability and regime persistence.

---

## 15. What Regime Persistence Means

Regime persistence refers to the tendency of a market regime to remain active over multiple consecutive time periods before transitioning to a different regime.

A highly persistent regime (e.g., a bull market lasting several months) suggests stable market conditions, while low persistence (frequent switching between regimes) may indicate market uncertainty or structural transitions.

Key metrics include:
- **Average duration:** How many consecutive days a regime typically lasts.
- **Self-transition probability:** The diagonal values in a transition matrix, representing the probability that a regime continues into the next period.

**Why this matters to us:**
Understanding persistence helps us evaluate the reliability of regime-based trading strategies. Strategies perform better when regimes are stable and persist long enough for actionable decisions.

---

## 16. What Time-Series Cross-Validation Is

In traditional machine learning, data is randomly split into training and test sets. However, financial data is ordered in time, and random splits would allow the model to "see the future" during training.

Time-series cross-validation respects the temporal order of the data:
- Training data always comes before test data.
- The training window expands (or slides) forward in time.
- Each fold evaluates the model on a future time period it has never seen.

**Why this matters to us:**
When we train classification models to forecast market regimes, we must use time-series cross-validation to avoid data leakage and obtain realistic performance estimates.

---

## 17. What Classification Models Do in This Context

Classification models predict which category (class) a new observation belongs to. In this project, the classes are the market regimes identified by clustering.

Common models used include:
- **Random Forest:** An ensemble of decision trees that votes on the most likely regime.
- **Gradient Boosting:** Sequentially builds decision trees that correct the errors of previous ones.
- **Logistic Regression:** A linear model that estimates regime probabilities.

**Why this matters to us:**
Instead of relying solely on clustering (which labels historical data), classification models allow us to forecast which regime the market is likely to enter next based on the most recent features.

---

## 18. What the Sharpe Ratio Measures

The Sharpe Ratio is a risk-adjusted performance metric that evaluates how much excess return an investment generates per unit of risk taken.

$$
\text{Sharpe Ratio} = \frac{R_p - R_f}{\sigma_p}
$$

Where:
- $R_p$ = Portfolio return
- $R_f$ = Risk-free rate (e.g., Treasury bond yield)
- $\sigma_p$ = Standard deviation of portfolio returns

A higher Sharpe Ratio indicates better risk-adjusted performance. A ratio above 1.0 is generally considered good, and above 2.0 is very good.

**Why this matters to us:**
When evaluating our regime-based trading strategy, the Sharpe Ratio tells us whether the strategy's returns are worth the risk taken, and allows comparison against a simple buy-and-hold approach.

---

## 19. What Maximum Drawdown Means

Maximum Drawdown measures the largest peak-to-trough decline in the value of a portfolio before a new peak is achieved.

$$
\text{Max Drawdown} = \frac{\text{Trough Value} - \text{Peak Value}}{\text{Peak Value}}
$$

It represents the worst-case loss an investor would have experienced during the investment period.

**Why this matters to us:**
Even a strategy with high returns may be undesirable if it experiences extreme drawdowns. Maximum drawdown helps us assess the downside risk of our regime-based strategy compared to buy-and-hold.

---

## 20. What Cumulative Returns Represent

Cumulative returns show the total percentage gain or loss of a portfolio over time, starting from the initial investment.

They are calculated by compounding individual period returns:

$$
\text{Cumulative Return}_t = \prod_{i=1}^{t}(1 + r_i) - 1
$$

A cumulative return chart visually tracks the growth of an investment over the entire analysis period.

**Why this matters to us:**
We use cumulative return plots to compare the total performance of our regime-based trading strategy against a passive buy-and-hold approach over the same time period.


---

## 21. What Transaction Costs and Slippage Mean in Quantitative Backtesting

In theoretical models, buying or selling assets is often assumed to be instantaneous and cost-free. In real-world quantitative trading, every portfolio adjustment incurs execution friction:

1. **Brokerage/Exchange Commission Fees ($c_{\text{fee}}$):** The fee paid to the venue for executing a trade (typically 10 basis points, or 0.10%, for spot crypto takers).
2. **Bid-Ask Spread Slippage ($c_{\text{slip}}$):** The difference between the quoted mid-price and the actual executed market price due to order book depth.
3. **Portfolio Turnover ($\Delta w_t$):** The fraction of total portfolio value reallocated across time:
   $$
   \Delta w_t = |w_t - w_{t-1}|
   $$

The net strategy return after subtracting friction drag is:
$$
R_t^{\text{net}} = w_t \cdot R_t^{\text{mkt}} - \Delta w_t \cdot (c_{\text{fee}} + c_{\text{slip}})
$$

**Why this matters to us:**
Accounting for turnover and trading costs prevents the model from generating false positive performance or trading excessively on minor noise, ensuring that reported returns reflect achievable live performance.


---

## 22. Hard Clustering vs. Soft Clustering (GMM & Hidden Markov Models)

In traditional clustering (such as K-Means), each observation is assigned to exactly one cluster with 100% certainty ("hard clustering"). In financial markets, conditions often blend together gradually rather than switching instantly.

### 1. Gaussian Mixture Models (GMM)
GMM provides "soft clustering" by assuming the data is generated from a combination of several bell curves (Gaussian distributions). Instead of saying *"the market is 100% in Regime 1"*, GMM outputs probabilities:
- 65% Low-Volatility Neutral
- 25% Bullish
- 10% High-Volatility Transition

### 2. Hidden Markov Models (HMM)
A Hidden Markov Model goes one step further: it connects these soft probabilities across consecutive trading days. It understands that yesterday's state directly influences today's state through transition probabilities $A_{ij} = \mathbb{P}(S_t = j \mid S_{t-1} = i)$. Using the Viterbi algorithm, it finds the single most likely path of market regimes over the entire history of the asset.

**Why this matters to us:**
Soft clustering allows our trading models to measure regime uncertainty and avoid making aggressive, binary bets when the market is hovering near a boundary between two states.


---

## 23. Position Sizing: Discrete vs. Confidence-Weighted vs. The Kelly Criterion

A trading system consists of two parts: **direction** (what to trade) and **sizing** (how much capital to risk).

### 1. Discrete Fixed Sizing (The Baseline)
Allocates fixed capital chunks based solely on the winning label:
- 100% in Bullish or Neutral
- 50% in Transition
- 0% in Bearish

*Flaw:* If the model is 51% Bullish and 49% Bearish, it still risks 100% of the portfolio.

### 2. Confidence-Weighted Sizing
Multiplies the portfolio allocation by the exact probability of each regime:
$$
w_t = 1.0 \times P(\text{Bull}) + 1.0 \times P(\text{Neut}) + 0.5 \times P(\text{Trans}) + 0.0 \times P(\text{Bear})
$$
When confidence is high (90% Bullish), it invests heavily. When the model is uncertain (50% Bullish, 50% Bearish), it automatically dials down exposure to 50% to protect capital.

### 3. The Kelly Criterion
A mathematical formula from information theory (John Kelly, 1956) that calculates the exact fraction of wealth $f^*$ to invest in order to maximize the long-term compound growth rate of capital:
$$
f^* = \frac{\text{Expected Return} - R_f}{\text{Variance of Returns}}
$$
In volatile crypto markets, we use **Fractional Kelly (Half-Kelly)** to reduce volatility while harvesting compounding gains.

**Why this matters to us:**
Continuous sizing and smoothing dampen portfolio turnover, substantially reducing transaction fees and preventing whipsaws during regime transitions.


---

## 24. Multi-Asset Cross-Sectional Portfolio Allocation

In single-asset trading, the system makes a binary or fractional choice between holding that single cryptocurrency (e.g., BTC) or holding Cash. In the real world, investors trade a **portfolio of multiple digital assets** (e.g., Bitcoin, Ethereum, Solana).

Because different cryptocurrencies do not always change regimes at the exact same moment—Ethereum might enter an expansionary Bullish regime while Solana is in a High-Volatility Bearish correction—we can systematically rotate capital to the most favorable coins while protecting the overall portfolio.

### 1. Cross-Sectional Ranking & Momentum
Cross-sectional ranking compares all assets against each other at each time step $t$:
- **Regime Gatekeeping:** Any coin currently detected in a *"High-Volatility Bearish"* regime is strictly eliminated from the investable universe for that day.
- **Top-$K$ Selection:** Among the remaining healthy assets, the system selects the top $K$ coins exhibiting the highest trailing price momentum ($14$-day or $30$-day return).
- **Cash Preservation:** If only $m < K$ coins qualify (e.g., during a broad market panic), the remaining portfolio capital is preserved in 100% Cash.

### 2. Regime-Conditioned Risk Parity
In traditional equal weighting ($1/N$), higher-volatility coins dominate the portfolio's risk. Risk parity solves this by weighting each non-bearish asset inversely to its volatility:
$$
w_{i,t} \propto \frac{1}{\sigma_{i,t}}
$$
A stable coin with lower daily variance receives a higher capital weight, while a volatile coin receives a smaller weight, ensuring each position contributes equally to overall portfolio risk.

### 3. Multi-Asset Turnover & Rebalancing Friction
Rebalancing a multi-coin portfolio incurs trading costs across every asset whose weight changes:
$$
\Delta W_t = \sum_{i=1}^N |w_{i,t} - w_{i,t-1}|
$$
By combining regime persistence filtering with cross-sectional selection, the multi-asset allocator minimizes unnecessary rebalancing, keeping turnover and slippage under tight control.

**Why this matters to us:**
Multi-asset cross-sectional allocation delivers superior risk-adjusted compounding: it avoids catastrophic drawdowns by fleeing bearish coins into cash, while harvesting alpha by concentrating capital in the highest-momentum bullish assets.


---

## 25. Cloud Deployment & Public Accessibility (Streamlit Community Cloud)

While quantitative backtests and machine learning pipelines live in Python scripts and Jupyter notebooks, an institutional or retail user requires an accessible interface without having to clone a GitHub repository, configure a virtual environment, or install dependencies.

### 1. Streamlit Community Cloud Architecture
Streamlit Community Cloud connects directly to your GitHub repository:
- **Zero-Infrastructure Hosting:** Streamlit provisions a managed Linux container in the cloud, reads `requirements.txt`, installs dependencies, and runs `app.py`.
- **Global Public URL:** Assigns a live, permanent HTTPS domain (e.g., `https://[your-app-name].streamlit.app`) accessible from any browser, desktop, tablet, or smartphone worldwide.
- **Continuous Integration / Continuous Deployment (CI/CD):** Any push to the `main` branch automatically triggers an instant rebuild and redeployment on the cloud with zero downtime.
- **Configuration & Theming (`.streamlit/config.toml`):** Configures headless operation, disabling cross-origin restrictions and enabling security protection out-of-the-box.

**Why this matters to us:**
Deploying to Streamlit Community Cloud eliminates all technical barriers for end users: anyone can select a cryptocurrency, pick a fiat currency, and inspect the real-time regime prediction from their web browser without running a single line of terminal code.


