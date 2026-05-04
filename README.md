# 🛢️ Gold & Oil Prediction System
### DEPI Round 4 — MS Data Engineering & AI Track | Final Project

> A full end-to-end machine learning system that ingests, cleans, and models global and local economic data to predict **Gold** and **Brent Crude Oil** prices — built from scratch by a cross-functional team as our first ML project.

---

## 👥 Team

| Name | GitHub |
|------|--------|
| Ahmed Bassiony | [@ahmedbasiony007](https://github.com/ahmedbasiony007) |
| Lamiaa Selim | [@lamiaaselim630](https://github.com/lamiaaselim630) |
| **Mohamed El-Naggar** | [@hpelnaggar](https://github.com/hpelnaggar) |
| Nourhan Habila | [@NourhanHabila](https://github.com/NourhanHabila) |
| Sara Seoudi | [@saraseoudy74](https://github.com/saraseoudy74) |

> We come from diverse professional backgrounds — shipping, engineering, finance, and technology. This project represents our collective first step into applied machine learning, built with curiosity, persistence, and a great deal of collaboration.

---

## 📌 Project Overview

This project builds a **complete data-to-prediction pipeline** targeting two of the world's most strategically important commodities: **Gold** and **Brent Crude Oil**.

The pipeline spans three major phases:

1. **Data Engineering** — automated collection from 10+ sources across APIs, web scraping, and manual downloads
2. **Data Cleaning & Harmonization** — standardizing heterogeneous datasets into a unified daily time series (2016–2026)
3. **Machine Learning Modeling** — feature engineering, leakage prevention, time-series cross-validation, and ensemble model training

---

## 🗂️ Repository Structure

```
├── data_cleaning.ipynb       # Part 1: Data gathering, ETL, and cleaning pipeline
├── gold_model.ipynb          # Part 2: Gold price prediction model
├── oil_model.ipynb           # Part 2: Oil price prediction model
├── ai data/                  # Files related to saved models and images shows comparison between actual market and predicted values   
├── raw data/                 # Original files from APIs and scraping
└── cleaned data/
    ├── market data/          # High-frequency daily data (prices, FX rates)
    └── macroeconomic data/   # Low-frequency indicators (CPI, GDP, interest rates)
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
| Visualization | `matplotlib`, `seaborn` |
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

Collected daily exchange rates of USD vs. EUR, CNY, JPY, GBP, RUB, CHF, and NOK — key currencies for commodity pricing dynamics.

### 3. Egyptian Local Market Data (via Selenium + CBE)

Automated browser-based scraping of the **Central Bank of Egypt (CBE)** website to extract:
- **USD/EGP Exchange Rate** — daily historical data
- **Headline & Core Inflation** — CPI from CBE Excel reports
- **EGX30** — Egyptian stock index from the official EGX website

Local gold prices (XAU/EGP) were sourced from [investing.com](https://www.investing.com) and integrated manually.

### 4. Macroeconomic Indicators (Multi-Country)

Comprehensive macro data collected from dedicated central bank APIs:

| Region | Data Points | Source |
|---|---|---|
| Egypt | CPI, Interest Rate | IMF API, CBE |
| USA | Fed Funds Rate, Treasury Yields (1Y–30Y), CPI, GDP, Dollar Index | FRED API |
| Euro Zone | Interest Rate, CPI, GDP | ECB API |
| Norway | Interest Rate, CPI, GDP, 2Y/10Y Yields | Norges Bank API, SSB API |
| China | CPI, Interest Rate, GDP | FRED API |
| Japan | CPI, Interest Rate, GDP, 2Y/10Y Yields | FRED API |

### 5. Geopolitical Risk Indices

- **GPR Index** (Geopolitical Risk) — measures adverse geopolitical events based on newspaper article tallies, capturing military conflicts, terror threats, and political crises
- **AI-GPR Index** — AI-enhanced version of the GPR daily index

### 6. Global Energy Data (World Bank API)

Energy production and trade indicators for 11 countries (US, Egypt, Germany, Norway, China, Japan, Russia, Saudi Arabia, Kuwait, Qatar, UAE):
- Oil-based electricity production percentage
- Energy use per capita
- Fuel import/export as % of total trade
- Gas-based electricity production percentage

---

## 🧹 Data Cleaning Logic

All raw datasets — regardless of source — were processed through a **rigorous, standardized cleaning pipeline**:

- **Chronological Sorting** — all data sorted from 2016-01-01 to present
- **Continuous Daily Timeline** — `pd.date_range` used to ensure no date gaps; every calendar day is accounted for
- **Missing Value Strategy** — `bfill` applied to the first valid entry; `ffill` applied thereafter to handle weekends, market holidays, and reporting lags
- **Date Normalization** — mixed formats (US `MM/DD/YYYY`, international `DD/MM/YYYY`, quarterly `YYYY-Q1`) all standardized to `DD/MM/YYYY`
- **Numeric Cleaning** — symbols like `%`, `$`, and `,` stripped and values cast to `float`
- **Schema Standardization** — every output CSV follows the schema: `id | region | ticker | date | value`
- **Duplicate Removal** — duplicate date entries detected and resolved (particularly in CBE exchange rate data)

---

## 🤖 Machine Learning Pipeline

Both the **Gold** and **Oil** models follow the same structured approach:

### Feature Engineering
Engineered features capture cross-asset relationships and market dynamics:
- `net_energy_imports` = fuel imports − fuel exports
- `opec_pressure` = OPEC basket price × Brent price
- `geo_risk_oil` = AI-GPR × oil sensitivity factor
- `oil_vol_x_vix` = Oil VIX × VIX (combined fear indicator)
- `oil_sp500` = Brent × S&P 500 (risk-on/off signal)
- `oil_x_dxy` = Brent × Dollar Index (inverse correlation signal)
- `copper_oil_ratio`, `wti_brent_spread`
- Lag features: returns at lags 1, 2, 3, 5, 10, 20 days
- Rolling volatility and momentum: 7-day and 20-day windows

### Leakage Prevention
Careful removal of any features that directly encode the target variable (e.g., open/high/low prices of the predicted asset, same-day correlated values) to ensure the model only uses information available at prediction time.

### Target Engineering
The prediction target is defined as the **5-day rolling mean of log returns**, clipped to ±4% to reduce the effect of extreme outliers:

```
log_price  = log(price)
return     = Δlog_price
target     = rolling(return, 5).mean().shift(-1), clipped to [-0.04, 0.04]
```

### Model Training

| Step | Detail |
|---|---|
| Train/Test Split | Chronological — train: up to 2025-12-31, test: 2026-01-01 to 2026-04-30 |
| Cross-Validation | `TimeSeriesSplit` (no shuffling to respect time ordering) |
| Base Model | `LGBMRegressor` (LightGBM) — 3,000 estimators, learning rate 0.01 |
| Feature Selection | Top-20 features selected via LightGBM feature importance |
| Final Models | Full-feature model and Top-20 model both trained and serialized |
| Evaluation Metrics | MAE, RMSE, R², MAPE |
| Serialization | Models saved as `.pkl` files via `pickle` |

---

## ▶️ Getting Started

### Execution Order

1. **Run `data_cleaning.ipynb`** — collects all raw data and outputs cleaned CSVs to `cleaned data/`
2. **Run `gold_model.ipynb`** — trains and evaluates the gold price prediction model
3. **Run `oil_model.ipynb`** — trains and evaluates the oil price prediction model

> **Note:** Some data sources (CBE website, EGX30 portal) require an active internet connection and may experience downtime. Manual CSV fallbacks are documented in the notebook cells for those sources.

---

## 📝 Notes & Acknowledgements

This is our **first machine learning project**, built entirely from scratch during the DEPI Round 4 program. Every pipeline — from API integration to model serialization — was designed, debugged, and refined by the team through hands-on learning.

We are grateful to the DEPI program instructor | Mohamed Hamed | [@MohammedHameds](https://github.com/MohammedHameds) | and our peers for their guidance throughout this journey. The breadth of data sources and modeling rigor reflects the team's commitment to building something genuinely useful, not just academically complete.

---

*DEPI Round 4 | MS Data Engineering & AI Track | 2025–2026*
