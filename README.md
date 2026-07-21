# Financial Market Regime Detection System

End-to-end financial data science project that identifies and characterizes market regimes through feature engineering, statistical analysis, dimensionality reduction, unsupervised machine learning, and financial interpretation.

---

## Project Objective

The goal of this project is to identify and characterize financial market regimes using statistical features derived from historical price data.

Rather than predicting future prices directly, the project seeks to discover recurring market states such as bullish, bearish, high-volatility, and sideways conditions through unsupervised machine learning techniques.

---

## Key Features

- End-to-end financial data science pipeline.
- Automated feature engineering for financial time series.
- Configurable multi-asset architecture.
- PCA-based dimensionality reduction.
- K-Means market regime detection.
- Financial interpretation of identified regimes.
- Publication-quality visualizations.
- Modular and extensible project structure.

---

## Research Question

Can unsupervised machine learning identify meaningful market regimes in cryptocurrency price behavior using statistical and technical features?

---
## Research Questions by Notebook

The project is organized as a sequence of research notebooks, where each notebook addresses a specific analytical question while contributing to the overall objective of identifying and understanding financial market regimes.

### Notebook 1 – Data Collection

**Main Question**

> How can historical financial market data be collected in a reproducible and scalable manner?

Questions addressed:

- How is historical OHLCV data obtained from Yahoo Finance?
- How can data collection be configured for different financial assets?
- How should raw market data be organized for reproducible analysis?

---

### Notebook 2 – Exploratory Data Analysis

**Main Question**

> What are the statistical characteristics of the collected financial data?

Questions addressed:

- Is the dataset complete and reliable?
- What are the main statistical properties of the market?
- What initial patterns can be identified before feature engineering?

---

### Notebook 3 – Feature Engineering

**Main Question**

> Which engineered financial features best describe market behavior?

Questions addressed:

- How can returns, volatility, and momentum be quantified?
- Why are engineered features preferable to raw prices?
- How do these features represent different aspects of market dynamics?

---

### Notebook 4 – Principal Component Analysis

**Main Question**

> Can the feature space be simplified while preserving most of its information?

Questions addressed:

- How much variance is explained by the principal components?
- Does dimensionality reduction improve clustering?
- What information is retained after PCA?

---

### Notebook 5 – Market Regime Identification

**Main Question**

> Can unsupervised learning identify meaningful financial market regimes?

Questions addressed:

- How many market regimes exist?
- What statistical characteristics define each regime?
- How can clusters be interpreted as recognizable market conditions?

---

### Notebook 6 – Market Regime Dynamics

**Main Question**

> How do identified market regimes evolve over time?

Questions addressed:

- How do market regimes change throughout history?
- Which transitions occur most frequently?
- Which market regimes persist the longest?
- What do these temporal dynamics reveal about financial market behavior?

----

## Design Principles

The project is being developed with the following objectives:

- Asset-agnostic analysis pipeline.
- Configurable data collection parameters.
- Support for multiple financial assets.
- Reproducible preprocessing and feature engineering.
- Extensible architecture for future analytical modules.
- Clear separation between research notebooks and production code.

Although development currently focuses on BTC-USD, the architecture aims to support any asset available through Yahoo Finance.

---

## Current Scope

The analyses and examples presented throughout this project use Bitcoin (BTC-USD) as the initial asset for experimentation and validation.

However, the project architecture was designed to support multiple cryptocurrencies through a centralized configuration system. By modifying the `ASSETS` parameter in `config.py`, the same data collection, feature engineering, dimensionality reduction, clustering, and regime detection pipeline can be applied to additional assets such as Ethereum (ETH-USD), Binance Coin (BNB-USD), Solana (SOL-USD), and others.

### Current Experiments

- BTC-USD

### Supported Architecture

- BTC-USD
- ETH-USD
- BNB-USD
- SOL-USD
- Additional Yahoo Finance supported assets

---

## Methodology

The project follows a multi-stage data science workflow designed to transform raw market data into interpretable market regimes.

### 1. Data Collection

- Historical OHLCV data is collected from Yahoo Finance.
- Data acquisition is configurable through a centralized configuration file.
- Raw datasets are stored for reproducibility.

### 2. Exploratory Data Analysis (EDA)

- Dataset quality is assessed.
- Price dynamics and trading activity are explored.
- Return behavior and statistical properties are analyzed.
- Insights are documented before feature engineering begins.

### 3. Feature Engineering

Features are created to capture different aspects of market behavior:

- Returns
- Volatility
- Momentum
- Additional indicators (future extensions)

These features serve as the foundation for identifying market regimes.

### 4. Dimensionality Reduction

Principal Component Analysis (PCA) is applied to:

- Reduce redundancy between features.
- Compress information into a smaller feature space.
- Improve clustering efficiency.
- Facilitate visualization and interpretation.

### 5. Clustering

Unsupervised learning techniques are used to group observations with similar behavior.

The objective is to discover naturally occurring market states without predefined labels.

### 6. Market Regime Characterization

Clusters are analyzed and interpreted as meaningful market regimes such as:

- Bullish markets
- Bearish markets
- High-volatility periods
- Consolidation phases

The resulting framework provides a systematic view of market behavior through time.

---

## Repository Structure

```text
Financial-Market-Regime-Detection-System/
│
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_pca.ipynb
│   ├── 05_clustering.ipynb
│   └── 06_market_regime_detection.ipynb
│
├── src/
│   ├── data/
│   ├── features/
│   ├── preprocessing/
│   ├── clustering/
│   └── regime_detection/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── models/
│
├── reports/
│
├── figures/
│
├── config/
│   └── config.py
│
└── README.md
```

---

## Project Workflow

```text
Raw Market Data
        ↓
Data Collection
        ↓
Exploratory Data Analysis
        ↓
Feature Engineering
        ↓
PCA
        ↓
Clustering
        ↓
Market Regime Detection
        ↓
Interpretation & Visualization
```

---

## Development Philosophy

This project separates research and engineering responsibilities.

### Research Layer (`notebooks/`)

The notebooks document:

- Why specific techniques are selected.
- What insights are obtained from the data.
- How decisions are made throughout the project.
- Interpretation of results.

### Engineering Layer (`src/`)

The source code contains:

- Reusable implementations.
- Automated processing pipelines.
- Scalable multi-asset workflows.
- Production-oriented logic.

This separation improves reproducibility, maintainability, and scalability.

