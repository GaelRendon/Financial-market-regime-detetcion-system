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
