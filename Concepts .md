# Concepts that you should know to understand this project:
## 1. What OHLCV Data Means?
The OHLCV refers to the standard fromat for financial price data. It help us track how a stock or crypto moved over a specific timeframe that we selected, and the letters stand for:
- O (Open): It's when the prices of the timeframes started.
- H (High): The highest price reached during the timeframe.
- L (Low): The lowest price reacheed during the timeframe.
- C (Close): It's the time when the timeframe ended or closed.
- V (Volume): The total numbers of shares or coins traded during that time.

**Why does this matter to us?**
If we look at a standard candlestick chart, each "candel" is built entirely from OHLCV data. The "body" shows the Open and Close, the "wicks" show the Highest and Lowest, and the Volume sits at the bottom of it.

## 2. Simple Returns vs Log. Returns
When we are calculating how much money an asset made or lost, quantitive traders use two different methods:
|Feature|Simple Returns|Log Returns|
|-|-|-|
|Formula|$\frac{Price_{today}-Price_{yesterday}}{Price{Yesterday}} $|$\ln(Price_{today})-\ln(Price_{yesterday})$|
|What it's good for|Explaining performance to humans(e.g., "My portfolio is up 5% today").|Doing heavy math and data analysis over time.|
|The big advantage|It's intuitive and easy to calculate.|Time-additivity: You can literally just add daily log returns together to get the total monthly return. Simple returns don't work that way.|

**Quick example of why Log Returns rule for coding:**
If a stock goes from \$100 up to \$110, that's a +10% simple return. If it drops from \$110 back to \$100, that's a -9.09% simple return. The math doesn't "cancel out" to zero, which breaks algorithms. Log returns do perfectly cancel out to zero.

## 3. Why Traders Care About Volatility
Volatility measures how violently a price bounces around. Think of it as the "speed limit" of risk.

Most of the traders care about ir for three major reasosn:
- **Risk Managment:** High volatility means you could make a lot of money fast-or lose your shirt just as quickly. Traders use it to decide how much money to risk on a single trade.
- **Pricing Options:** Financial derivatives (like options) become more expensive when volatility is high because there's higher chance the price will hit an extreme target.
- **Strategy Selection:** Some trading bots thrive on chaotuc, hig-volitality markets, while others prefer calm steady trends.

## 4. What Momentum Means
Momentum measures whether an asset has been moving consistently in one direction over a recent period.

The key idea is suprisingly simple what we look for is:
- Assets that have been going up recently often continue going up for a while.
- And assets that have been falling often continue falling. 

One common way to calculate momentum is:
- C = Current Price
- p = Price N Days Ago
$$
C - N 
$$

or another common one is:
- R = Current Return
- H = Historical Return
$$
R - H
$$

depending on the strategy.
**Why does this matter to us?**
Momentum is one of the three main features used in this project.
When we later perform clustering, momentum helps distinguish:
- Strong Uptrends
- Strong Downtrends
-  Neutral Markets

even when volatility remain similar.

## 5. What Feature Engineering Means
Feature Engineering is the process of creating meaningful variables from raw data.

Raw financial data usually contains:
- Open
- High
- Low
- Close
- Volume

However, machine learning algorithms often learn better from features that describe market behavior.

Examples include:
- Returns
- Volatility
- Momentum
- Moving Averages
- RSI
- MACD

**Why does this matter to us?**
Instead of feeding raw Bitcoin prices into our machine learning model, we transform the data into features that describe:
- Performance
- Risk
- Trend Strength

This makes it easier for algorithms to detect market regimes.

## 6. Why Scaling is Important
Machine learning algorithms are heavily influenced by the scale of variables.

Imagine two features:
- Returns: -0.05 to 0.05
- Volume: 0 to 50,000,000

Without scaling, the algorithm would pay much more attention to Volume simply because its numerical values are larger.

Scaling transforms variables so they have comparable ranges.

One common method is Standardization:
- Mean = 0 
- Standard Deviation = 1

**Why does this matter to us?**
Both PCA and K-Means depend on distance calcualtions.

It features are not scaled properly, the model may identify patterns based only on the largest numerical feature instead of the most important information.

## 7. What Principal Component Analysis (PCA) Does
Principal Component Analysis (PCA) is a dimensionality reduction technique.

Instead of analyzing several correlated variables separately, PCA creates new variables called Principal Components.

These components capture the most important information contained in the original features.

For this project:
- Returns
- Volatility 
- Momentum 

were transformed into:
- PC1
- PC2
- PC3

Each component represents a combination of the original features.

**Why does this matter to us?**
PCA helps:
- Reduce noise
- Remove redundancy 
- Simplify visualization
- Prepare data for clustering

while preserving as much information as possible.

## 8. What A Market Regime Is
A Market Regime is a period during which the market behaves in a relatively consistent manner.

Example include:
- Bull Market
- Bear Market
- Sideways Market
- High Volatility Market
- Low Volatility Market

Different regimes often require different trading strategies. 

A strategy that works well during a strong bull market may perform poorly during a highly volatile bear market.

**Why does this matter to us?**
The primary objective of this project is:

Automatically identify market regimes using machine learning.

Understanding regimes can help investors adapt their strategies to changing market conditions.

## 9. What Clustering Means
Clustering is an Unsupervised Machine Learning technique used to group similar observations together.

Unlike supervised learning, clustering does not require labeled data.

The algorithm looks for patterns and naturally separates observations into groups.

For example:
- Group A:
    - High Returns 
    - Low Volatility
- Group B:
    - Negative Returns 
    - High Volatility

The algorithm discovers these groups without being told what they represent.

**Why does it matter to us?**
Our project uses clustering to discover hidden market regimes in Bitcoin data.

The algorithm will analyze the PCA features and determine which observations behave similarly.