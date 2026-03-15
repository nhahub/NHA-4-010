# 🪙 Gold and Oil Prediction System

### **DEPI Round 4 | Microsoft Data Engineer and AI Track**

## 👥 Project Team
* **Ahmed Bassiony**
* **Lamiaa Selim**
* **Mohamed ElNaggar, hpelnaggar**
* **Nourhan Habila**
* **Sara Seoudi**

## 📌 Project Overview
This project establishes an automated data engineering pipeline to collect, clean, and prepare global and local economic indicators for a Gold and Oil price prediction model. The dataset spans from **2016 to 2026**, focusing on the Egyptian market's relationship with global commodity trends.

## 🛠️ Data Engineering Tech Stack
* **Language**: Python 3.x
* **Data Libraries**: `Pandas`, `NumPy`
* **Automation & Scraping**: `Selenium WebDriver`, `WebDriver Manager`
* **APIs**: `yfinance` (Yahoo Finance), `fredapi` (St. Louis Fed), `requests` (IMF API)
* **Environment**: Jupyter Notebook / VS Code

## 📊 Data Pipelines Built

### 1. Global Market Data (`yfinance` & `FRED`)
* **Commodities**: Gold (`GC=F`), Brent Crude (`BZ=F`), and WTI Crude (`CL=F`).
* **Forex Rates**: USD vs. major global currencies (EUR, CNY, JPY, GBP, RUB, CHF, NOK).
* **OPEC Basket**: Monthly historical oil prices retrieved via FRED API.
* **Volatility Index**: Market fear gauge (`^VIX`) for risk assessment.

### 2. Local Egyptian Data (CBE & Manual)
* **Exchange Rates**: Daily USD/EGP rates scraped and processed from the **Central Bank of Egypt**.
* **Inflation Rates**: Headline and Core CPI data processed from CBE Excel reports.
* **Local Gold**: Historical XAU/EGP prices integrated from manual sources.
* **Subsidies**: Macroeconomic data regarding petroleum and electricity subsidies.

## ⚙️ Data Cleaning & Logic
The pipeline implements the following rigorous "Strict Necessity" cleaning rules:
* **Chronological Sorting**: All data is sorted from oldest (2016) to newest (2026).
* **Continuous Timeline**: Used `pd.date_range` to ensure every single day from Jan 1, 2016, is accounted for.
* **Missing Value Logic**: Applied **Backward Fill (`bfill`)** to handle weekends and market holidays.
* **Normalization**: Handled mixed date formats (US vs International) and standardized numeric values (removing symbols like `%` or `,`).
* **Categorization**: Integrated `region` and `ticker` columns for multi-source data merging.

## 📁 Repository Structure
```text
├── raw data/               # Original CSV/Excel files from APIs and Scraping
├── cleaned data/           
│   ├── market_daily/       # High-frequency data (Prices, FX)
│   └── macro_periodic/     # Low-frequency data (CPI, Subsidies)
└── data_cleaning.ipynb     # Main ETL pipeline and cleaning functions