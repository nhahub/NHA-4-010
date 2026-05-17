# 🛢️ Gold, Oil & Global Markets Prediction System
### DEPI Round 4 — MS Data Engineering & AI Track | Final Project

<p align="center">
  <img src="assets/cover.png" alt="Project Cover" width="100%"/>
</p>

> A full end-to-end machine learning system that ingests, cleans, and models global and local economic data to predict **Gold**, **Brent Crude Oil**, and **8 Global Stock Market** prices — built from scratch by a cross-functional team as part of the DEPI Round 4 Final Project.

---

## 👥 Team

| Name | GitHub |
|------|--------|
| Ahmed Bassiony | [@ahmedbasiony007](https://github.com/ahmedbasiony007) |
| Lamiaa Selim | [@lamiaaselim630](https://github.com/lamiaaselim630) |
| **Mohamed El-Naggar** | [@hpelnaggar](https://github.com/hpelnaggar) |
| Nourhan Habila | [@NourhanHabila](https://github.com/NourhanHabila) |
| Sara Seoudi | [@saraseoudy74](https://github.com/saraseoudy74) |

> We come from diverse professional backgrounds — engineering, biology, finance, science and dentistry. This project represents our collective first step into applied machine learning, built with curiosity, persistence, and a great deal of collaboration.

**Project Supervisor:** Mohamed Hamed | [@MohammedHameds](https://github.com/MohammedHameds)

---

## 📌 Project Overview

This project builds a **complete data-to-prediction pipeline** targeting two of the world's most strategically important commodities — **Gold (XAU/USD)** and **Brent Crude Oil (USD/barrel)** — extended with **8 global stock market indices** and a novel **cascade prediction architecture**.

The pipeline spans five integrated phases:

1. **Data Engineering** — automated collection from 10+ sources across APIs, web scraping, and manual downloads
2. **Data Cleaning & Harmonization** — standardizing heterogeneous datasets into a unified daily time series (2016–2026)
3. **Machine Learning Modeling** — five distinct model families with feature engineering, leakage prevention, and time-series cross-validation
4. **Power BI Visualization** — interactive dashboards analyzing commodity, energy, and equity data
5. **Streamlit Application** — interactive web app streaming model predictions and data exploration

### 🔄 End-to-End Data Flow

<p align="center">
  <img src="assets/Dataflow.jpg" alt="End-to-End Microsoft Fabric Data Flow" width="100%"/>
</p>

The full solution is implemented end-to-end within **Microsoft Fabric**, covering all seven stages: Data Sources → Data Engineering → Unified Master Table (Lakehouse) → Modeling Layer → Evaluation & Forecasts → Outputs & Visualization → Delivery & Actions (including a Telegram Bot for alerts).

---

## 🗂️ Repository Structure

```
├── collection_and_cleaning.ipynb                      # Phase 1 & 2: ETL, data gathering, and cleaning pipeline
├── standalone_gold_model.ipynb                        # Gold price prediction model (standalone)
├── oil_model.ipynb                                    # Oil price prediction model (standalone)
├── stock_markets_model.ipynb                          # 8 global stock markets standalone model
├── gold_oil_dependent_stock_markets_models.ipynb      # Stock models using predicted commodity prices
├── cascade_gold_model.ipynb                           # Cascade: Stock → Oil → Gold inference pipeline
├── streamlit_app/                                     # Streamlit interactive visualization application
├── powerbi/                                           # Power BI dashboard (.pbix files)
├── ai model/                                          # Serialized .pkl model files and prediction comparison images
├── raw data/                                          # Original files from APIs and scraping
└── cleaned data/
    ├── market data/                                   # High-frequency daily data (prices, FX rates)
    └── macroeconomic data/                            # Low-frequency indicators (CPI, GDP, interest rates)
```

---

## 🔧 Tech Stack

| Category | Tools & Libraries |
|---|---|
| Language | Python 3.x |
| Data & Wrangling | `pandas`, `numpy` |
| Web Scraping | `selenium`, `webdriver-manager` |
| Market Data APIs | `yfinance`, `requests` (IMF, FRED, ECB, Norges Bank, World Bank) |
| Machine Learning | `scikit-learn`, `xgboost`, `lightgbm` |
| Visualization (Python) | `matplotlib`, `seaborn` |
| Interactive App | `streamlit` |
| BI Dashboard | Power BI Desktop |
| Cloud Platform | Microsoft Fabric (Lakehouse, Data Factory, Notebooks) |
| Delivery | Telegram Bot (alerts & notifications) |
| Environment | Jupyter Notebook, VS Code |
| Serialization | `joblib`, `pickle` |

---

## 📡 Data Sources & Pipelines

### 1. Global Market Data (via `yfinance` & FRED API)

| Asset | Ticker | Source |
|---|---|---|
| Gold Futures | `GCF` | Yahoo Finance |
| Brent Crude | `BZF` | Yahoo Finance |
| WTI Crude | `CLF` | Yahoo Finance |
| OPEC Basket | `POILBREUSDM` | FRED (St. Louis Fed) |
| Oil Volatility Index | `OVXCLS` | FRED |
| Gold Volatility Index | `GVZCLS` | FRED |
| VIX (Fear Index) | `VIX` | Yahoo Finance |
| NASDAQ, Dow Jones, S&P 500 | `IXIC`, `DJI`, `GSPC` | Yahoo Finance |
| Shanghai, Tokyo, London, HK | Various | Yahoo Finance |
| Silver, Copper | `SIF`, `HGF` | Yahoo Finance |

### 2. Forex Rates (via `yfinance`)

Daily exchange rates of USD vs. EUR, CNY, JPY, GBP, RUB, CHF, and NOK — key currencies for commodity pricing dynamics and safe-haven capital flow analysis.

### 3. Egyptian Local Market Data (via Selenium + CBE)

Automated browser-based scraping of the **Central Bank of Egypt (CBE)** website to extract:
- **USD/EGP Exchange Rate** — daily historical data
- **Headline & Core Inflation** — CPI from CBE Excel reports
- **EGX30** — Egyptian stock index from the official EGX website

Local gold prices (XAU/EGP) were sourced from [investing.com](https://www.investing.com) and integrated manually.

### 4. Macroeconomic Indicators (Multi-Country)

| Region | Data Points | Source |
|---|---|---|
| Egypt | CPI, Interest Rate | IMF API, CBE |
| USA | Fed Funds Rate, Treasury Yields (1Y–30Y), CPI, GDP, Dollar Index | FRED API |
| Euro Zone | Interest Rate, CPI, GDP | ECB API |
| Norway | Interest Rate, CPI, GDP, 2Y/10Y Yields | Norges Bank API, SSB API |
| China | CPI, Interest Rate, GDP | FRED API |
| Japan | CPI, Interest Rate, GDP, 2Y/10Y Yields | FRED API |

### 5. Geopolitical Risk Indices

- **GPR Index** — measures adverse geopolitical events based on newspaper article tallies, capturing military conflicts, terror threats, and political crises
- **AI-GPR Index** — AI-enhanced version of the GPR daily index providing higher-frequency geopolitical signal

### 6. Global Energy Data (World Bank API)

Energy production and trade indicators for 11 countries (US, Egypt, Germany, Norway, China, Japan, Russia, Saudi Arabia, Kuwait, Qatar, UAE):
- Oil-based electricity production percentage
- Energy use per capita
- Fuel import/export as % of total trade
- Gas-based electricity production percentage

---

## 🧹 Data Cleaning Logic

All raw datasets — regardless of source — were processed through a **rigorous, standardized cleaning pipeline** implemented in a reusable `loading()` function:

- **Chronological Sorting** — all data sorted from 2016-01-01 to present
- **Continuous Daily Timeline** — `pd.date_range` ensures no date gaps; every calendar day is accounted for
- **Missing Value Strategy** — `bfill` applied to the first valid entry; `ffill` applied thereafter to handle weekends, market holidays, and reporting lags
- **Date Normalization** — mixed formats (US `MM/DD/YYYY`, international `DD/MM/YYYY`, quarterly `YYYY-Q1`) all standardized
- **Numeric Cleaning** — symbols like `%`, `$`, and `,` stripped and values cast to `float`
- **Schema Standardization** — every output CSV follows the schema: `id | region | ticker | date | value`
- **Duplicate Removal** — duplicate date entries detected and resolved (particularly in CBE exchange rate data)

### Master Table Construction

All cleaned market and macroeconomic DataFrames are merged using `functools.reduce` with `pd.merge` (outer join on date key) into a single `master_table.csv`, which forms the unified input to all modeling notebooks.

---

## 🤖 Machine Learning Models

Five model families were developed, each building on the previous in architectural complexity:

### Model 1 — Standalone Gold Model (`standalone_gold_model.ipynb`)

Predicts **XAU/USD** (gold price per troy ounce).

**Feature Engineering:**

| Feature | Formula | Economic Rationale |
|---|---|---|
| `gold_usd_index` | Gold × Dollar Index | Inverse correlation signal |
| `gold_sp500` | Gold × S&P 500 | Risk-on/risk-off indicator |
| `gold_vol_x_vix` | Gold VIX × VIX | Combined volatility/fear signal |
| `geo_risk_gold` | AI-GPR × gold sensitivity | Geopolitical premium |
| `silver_gold_ratio` | Silver / Gold | Precious metals spread |
| `gold_real_rate` | Gold × (1 − US real yield) | Real interest rate sensitivity |

**Results (Jan–Apr 2026 holdout):**

| Metric | Full Model | Top-15 Features Model |
|---|---|---|
| MAE (USD/oz) | 284.22 | **159.47** |
| Directional Accuracy | 79.0% | **82.4%** |

---

### Model 2 — Standalone Oil Model (`oil_model.ipynb`)

Predicts **Brent Crude Oil** price (USD/barrel).

**Feature Engineering:**

| Feature | Formula | Economic Rationale |
|---|---|---|
| `net_energy_imports` | Fuel imports − Fuel exports | Net energy dependency |
| `opec_pressure` | OPEC basket × Brent price | OPEC pricing power signal |
| `geo_risk_oil` | AI-GPR × oil sensitivity | Geopolitical supply risk |
| `oil_vol_x_vix` | Oil VIX × VIX | Combined fear/volatility |
| `oil_sp500` | Brent × S&P 500 | Risk-on demand signal |
| `oil_x_dxy` | Brent × Dollar Index | USD inverse correlation |
| `copper_oil_ratio` | Copper / Brent | Industrial demand proxy |
| `wti_brent_spread` | WTI − Brent | Arbitrage/quality spread |

**Results (Jan–Apr 2026 holdout):**

| Metric | Full Model | Top-20 Features Model |
|---|---|---|
| MAE (USD/barrel) | — | **5.41** |
| Directional Accuracy | — | **78.2%** |

The model also includes a **next-day price reconstruction** pipeline using cumulative log-return exponentiation.

---

### Model 3 — Standalone Stock Markets Model (`stock_markets_model.ipynb`)

Eight global stock market indices modeled independently as separate LightGBM regression tasks:

| Market | Target Column | Currency |
|---|---|---|
| Egypt EGX30 | `egx30_price_egp` | EGP |
| NASDAQ | `nasdaq_price_usd` | USD |
| S&P 500 | `sp500_price_usd` | USD |
| Dow Jones | `dowjones_price_usd` | USD |
| Shanghai | `chinashanghai_price_usd` | USD |
| Hong Kong | `hongkonghongkong_price_usd` | USD |
| London FTSE | `uklondon_price_usd` | USD |
| Tokyo Nikkei | `japantokyo_price_usd` | USD |

Each model applies extensive **macro + technical feature engineering** including: yield spreads, RSI, Bollinger Bands, momentum crossovers, rolling volatility, calendar features, and lagged macro signals. Strict leakage removal excludes all same-day OHLC data and cross-market price columns.

---

### Model 4 — Gold/Oil-Dependent Stock Market Model (`gold_oil_dependent_stock_markets_models.ipynb`)

An extended variant where **predicted** gold and oil prices (from Models 1 & 2) are injected into the stock market models during the test phase, replacing actual commodity prices. This reflects a realistic forward-looking deployment scenario.

**Commodity Prediction Injection — Recomputed Interaction Features:**

| Interaction Feature | Recomputed As |
|---|---|
| `gold_x_dxy` | predicted_gold × dollar_index |
| `gold_lag1` | predicted_gold (same-day value) |
| `gold_mom` | predicted_gold.pct_change() |
| `oil_x_dxy` | predicted_oil × dollar_index |
| `oil_lag1` | predicted_oil |
| `oil_mom` | predicted_oil.pct_change() |

- **Train set:** actual historical commodity prices (up to 2025-12-31)
- **Test set:** 2026-01-01 to 2026-04-30 with injected model predictions

---

### Model 5 — Cascade Model: Stock → Oil → Gold (`cascade_gold_model.ipynb`)

The most architecturally advanced pipeline, encoding a **three-stage sequential dependency chain** reflecting real-world causal relationships:

```
Stage 1: Stock Market Predictions (×7 USD-denominated indices)
          ↓
Stage 2: Oil (Brent) — fed by Stage 1 equity predictions
          ↓
Stage 3: Gold (XAU/USD) — fed by Stage 2 oil + Stage 1 equity predictions
```

**Why this chain?**
- *Equity → Oil:* Rising stock markets signal economic expansion and higher energy demand
- *Oil → Gold:* Oil price shocks fuel inflationary expectations and safe-haven demand for gold

The cascade is a **pure inference pipeline** — no re-training occurs. All three stages load pre-trained `.pkl` models and chain their outputs. Zero lookahead bias is guaranteed at every stage.

**Cascade Model Results (Jan–Apr 2026 holdout):**

| Stage | Metric | Full Model | Top Features Model |
|---|---|---|---|
| Oil (Stage 2) | MAE (USD/bbl) | 11.31 | **5.91** |
| Oil (Stage 2) | Directional Accuracy | — | **77.3%** |
| Gold (Stage 3) | MAE (USD/oz) | 235.07 | **170.03** |
| Gold (Stage 3) | Directional Accuracy | — | **82.4%** |

**Cascade vs. Standalone Gold Comparison:**

| Metric | Standalone Gold (Top 15) | Cascade Gold (Top 15) |
|---|---|---|
| MAE (USD/oz) | 159.47 | 170.03 |
| Directional Accuracy | **82.4%** | **82.4%** |
| MAE Difference | — | +10.56 (+6.6%) |

The cascade achieves **identical directional accuracy** to the standalone model at only +6.6% MAE overhead — validating the three-stage architecture as a deployable, zero-leakage forecasting system.

---

### Target Engineering (All Models)

The prediction target across all models is defined as the **5-day rolling mean of log returns**, shifted forward one day and clipped to ±4% (±3% for stock models):

```
log_price  = log(price)
return     = Δlog_price
target     = rolling(return, 5).mean().shift(-1), clipped to [-0.04, 0.04]
```

### Training Configuration

| Step | Detail |
|---|---|
| Train/Test Split | Chronological — train: up to 2025-12-31, test: 2026-01-01 to 2026-04-30 |
| Cross-Validation | `TimeSeriesSplit` (5 folds, no shuffling) |
| Base Model | `LGBMRegressor` — 3,000 estimators, learning rate 0.01 |
| Feature Selection | Top-15/20 features via LightGBM split importance |
| Evaluation Metrics | MAE, RMSE, R², MAPE, Directional Accuracy |
| Serialization | Models saved as `.pkl` files via `pickle` |

---

## 📊 Power BI Dashboard

The Power BI dashboard provides **descriptive and exploratory analysis** of the cleaned dataset, structured into three specialized modules:

### Dashboard Architecture

**1. General Dashboard**
High-level overview of global stock market performance and trends. Provides a cross-market perspective to contextualize the prediction outputs.

**2. Gold Analysis Page**
Focuses on gold's utility as a strategic safe-haven asset. Layers gold market movements against:
- USD valuation (Dollar Index)
- Real interest rates
- Geopolitical Risk Index (GPR & AI-GPR)
- Precious metals spread (silver/gold ratio)

**3. Oil & Energy Analysis Page**
Maps Brent and WTI price dynamics against:
- Oil and Gold volatility indices (OVX, GVZ)
- Regional energy trade metrics (imports/exports as % of total trade)
- OPEC basket pricing and supply pressure indicators
- Market sentiment signals

### Data Preparation for Power BI

After the Python ETL pipeline, data was further refined using **Power Query (Transform tool)** within Power BI:
- Additional duplicate and null value elimination
- Date-based normalization across all tables for consistent temporal slicing
- Restructured and normalized data model enabling cross-filter analysis across economic dimensions

> **File location:** `powerbi/gold_oil_dashboard.pbix`

---

## 🖥️ Streamlit Application

The Streamlit application provides an **interactive, data-driven web interface** built on top of the entire pipeline, allowing users to explore results without running notebooks.

### Application Features

- **📈 Price Prediction Viewer** — Interactive charts comparing model predictions vs. actual prices for Gold, Oil, and all 8 stock markets across the Jan–Apr 2026 test period
- **🔁 Model Selector** — Toggle between Full Model and Top Features Model results for side-by-side comparison
- **📊 Feature Importance Explorer** — Visual breakdown of the most impactful features driving each model's predictions
- **🌍 Data Explorer** — Browse the master table with filters for date range, asset class, and data source
- **📉 Cascade Pipeline Visualizer** — Step-through visualization of the three-stage cascade chain (Stock → Oil → Gold)
- **⚡ Next-Day Prediction Panel** — Displays the model's next-day directional signal for Brent Crude Oil

### Running the App

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the Streamlit app
streamlit run streamlit_app/app.py
```

> **Note:** The app loads pre-trained `.pkl` model files from `ai model/`. Ensure the modeling notebooks have been executed at least once before running the app.

---

## ▶️ Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
```

### Execution Order

1. **Run `collection_and_cleaning.ipynb`** — collects all raw data and outputs cleaned CSVs to `cleaned data/`
2. **Run `standalone_gold_model.ipynb`** — trains and evaluates the standalone gold prediction model
3. **Run `oil_model.ipynb`** — trains and evaluates the standalone oil prediction model
4. **Run `stock_markets_model.ipynb`** — trains all 8 standalone stock market models
5. **Run `gold_oil_dependent_stock_markets_models.ipynb`** — trains stock models with commodity prediction injection
6. **Run `cascade_gold_model.ipynb`** — runs the full cascade inference pipeline (loads pre-trained models, no re-training)
7. **Launch `streamlit run streamlit_app/app.py`** — start the interactive visualization app
8. **Open `powerbi/gold_oil_dashboard.pbix`** — explore the Power BI descriptive dashboards

> **Note:** Some data sources (CBE website, EGX30 portal) require an active internet connection and may experience downtime. Manual CSV fallbacks are documented in notebook cells for those sources.

---

## 📈 Results Summary

| Model | Asset | MAE | Directional Accuracy |
|---|---|---|---|
| Standalone Gold (Top 15) | XAU/USD | 159.47 USD/oz | **82.4%** |
| Standalone Oil (Top 20) | Brent USD/bbl | 5.41 USD/bbl | **78.2%** |
| Cascade Gold (Top 15) | XAU/USD | 170.03 USD/oz | **82.4%** |
| Cascade Oil (Top 15) | Brent USD/bbl | 5.91 USD/bbl | **77.3%** |

All models evaluated on a fully out-of-sample holdout: **January 1 – April 30, 2026**.

---

## 📝 Notes & Acknowledgements

This is our **first machine learning project**, built entirely from scratch during the DEPI Round 4 program. Every pipeline — from API integration to cascade model architecture to Power BI dashboards and Streamlit deployment — was designed, debugged, and refined by the team through hands-on learning.

The project was notably tested against a period of extreme market volatility in early 2026, driven by global tensions in the Strait of Hormuz — a real-world stress test that underscores both the challenge and value of robust commodity forecasting.

We are grateful to our project supervisor **Mohamed Hamed** and the entire DEPI Round 4 program for providing the structure and mentorship that made this possible.

---

*DEPI Round 4 | MS Data Engineering & AI Track | 2025–2026*
