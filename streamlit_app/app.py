import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import os

# PAGE CONFIG
st.set_page_config(
    page_title="Egypt Financial Dashboard",
    page_icon="🇪🇬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# THEME / CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background-color: #0d1117; }
    .block-container { padding: 1.5rem 2rem; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    section[data-testid="stSidebar"] * { color: #c9d1d9 !important; }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #161b22 0%, #1f2937 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        text-align: center;
        transition: transform .2s, border-color .2s;
    }
    .kpi-card:hover { transform: translateY(-3px); border-color: #58a6ff; }
    .kpi-label { color: #8b949e; font-size: 0.75rem; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; margin-bottom: .35rem; }
    .kpi-value { color: #f0f6fc; font-size: 1.7rem; font-weight: 700; line-height: 1.1; }
    .kpi-delta-pos { color: #3fb950; font-size: 0.8rem; font-weight: 600; }
    .kpi-delta-neg { color: #f85149; font-size: 0.8rem; font-weight: 600; }

    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #1f2937, #161b22);
        border-left: 4px solid #58a6ff;
        border-radius: 0 8px 8px 0;
        padding: .6rem 1rem;
        margin: 1.5rem 0 1rem 0;
        color: #f0f6fc;
        font-size: 1rem;
        font-weight: 700;
        letter-spacing: .03em;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: #161b22; border-radius: 8px; padding: 4px; gap: 4px; }
    .stTabs [data-baseweb="tab"] { border-radius: 6px; color: #8b949e; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #58a6ff !important; color: #0d1117 !important; }

    /* Plotly chart bg */
    .js-plotly-plot { border-radius: 10px; }

    /* Selectbox / slider */
    .stSelectbox label, .stSlider label, .stMultiSelect label { color: #8b949e !important; font-size: 0.82rem; }

    h1 { color: #f0f6fc !important; }
    h2, h3 { color: #c9d1d9 !important; }
    p, li { color: #8b949e; }
    .page-title {
        background: linear-gradient(135deg, #1B3A6B 0%, #2E5FAC 50%, #1B3A6B 100%);
        border: 1px solid #C5A028;
        border-left: 6px solid #C5A028;
        border-radius: 12px;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(197,160,40,0.15);
    }
    .page-title-icon { font-size: 2rem; display: block; margin-bottom: 0.2rem; }
    .page-title-text {
        font-size: 2rem; font-weight: 800;
        background: linear-gradient(90deg, #ffffff 0%, #C5A028 60%, #f0f6fc 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; display: block; line-height: 1.2;
    }
    .page-title-sub {
        font-size: 0.8rem; color: #8b949e; margin-top: 0.3rem;
        display: block; letter-spacing: 0.05em; text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# CHART DEFAULTS
CHART_BG   = "#0d1117"
PAPER_BG   = "#0d1117"
GRID_COLOR = "#21262d"
FONT_COLOR = "#c9d1d9"
ACCENT     = "#58a6ff"
COLORS     = ["#58a6ff","#3fb950","#e3b341","#f85149","#bc8cff","#79c0ff","#56d364","#ffa657"]

def base_layout(title="", height=400, **kw):
    return dict(
        title=dict(text=title, font=dict(color=FONT_COLOR, size=14), x=0.01),
        paper_bgcolor=PAPER_BG, plot_bgcolor=CHART_BG,
        font=dict(color=FONT_COLOR, family="Inter"),
        height=height,
        xaxis=dict(gridcolor=GRID_COLOR, showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=GRID_COLOR, showgrid=True, zeroline=False),
        margin=dict(l=50, r=20, t=45, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        **kw
    )

# DATA LOADERS
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_all():
    data = {}

    # --- Inflation (CBE xlsx) ---
    inf = pd.read_excel(os.path.join(DATA_DIR, "egy_cbe_inflation_rate.xlsx"), header=None)
    inf.columns = ["date","headline","core","regulated","fruits_veg"]
    inf = inf[inf["date"].astype(str).str.strip() != "Date"].copy()
    inf["date"] = pd.to_datetime(inf["date"].astype(str), format="%b %Y", errors="coerce")
    inf = inf.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    for c in ["headline","core","regulated","fruits_veg"]:
        inf[c] = inf[c].astype(str).str.replace("%","").str.strip()
        inf[c] = pd.to_numeric(inf[c], errors="coerce")
    data["inflation"] = inf

    # EGP/USD CBE xlsx
    egp = pd.read_excel(os.path.join(DATA_DIR, "egy_cbe_egpusd_rate.xlsx"), header=None)
    egp.columns = ["date","rate"]
    egp = egp[egp["date"].astype(str).str.strip() != "Date"].copy()
    egp["date"] = pd.to_datetime(egp["date"], errors="coerce")
    egp["rate"] = pd.to_numeric(egp["rate"], errors="coerce")
    egp = egp.dropna().sort_values("date").reset_index(drop=True)
    data["egpusd"] = egp

    # CPI
    cpi = pd.read_csv(os.path.join(DATA_DIR, "egy_cpi.csv"))
    cpi.columns = ["year","cpi"]
    cpi["year"] = pd.to_numeric(cpi["year"], errors="coerce")
    cpi = cpi.dropna().sort_values("year").reset_index(drop=True)
    data["cpi"] = cpi

    # Egyptian Gold (raw format from investing.com)
    eg_gold = pd.read_csv(os.path.join(DATA_DIR, "egy_gold_prices.csv"))
    # Normalise column names whether raw or cleaned
    eg_gold.columns = eg_gold.columns.str.strip()
    col_map = {}
    for c in eg_gold.columns:
        cl = c.lower().strip()
        if cl == "date":                          col_map[c] = "date"
        elif cl in ("price","price_oz_egp","close"): col_map[c] = "price_oz_egp"
        elif cl in ("open","open_price_egp"):     col_map[c] = "open_price_egp"
        elif cl in ("high","high_price_egp"):     col_map[c] = "high_price_egp"
        elif cl in ("low","low_price_egp"):       col_map[c] = "low_price_egp"
    eg_gold = eg_gold.rename(columns=col_map)
    eg_gold["date"] = pd.to_datetime(eg_gold["date"], format="mixed", dayfirst=False, errors="coerce")
    for c in ["price_oz_egp","open_price_egp","high_price_egp","low_price_egp"]:
        if c in eg_gold.columns:
            eg_gold[c] = eg_gold[c].astype(str).str.replace(",","").str.strip()
            eg_gold[c] = pd.to_numeric(eg_gold[c], errors="coerce")
    eg_gold = eg_gold.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    data["egy_gold"] = eg_gold

    def load_yf_csv(filepath):
        """Handle both raw yfinance (Date/Close) and cleaned (date/price_usd) formats."""
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()
        col_map = {}
        for c in df.columns:
            cl = c.lower().strip()
            if cl == "date":                                  col_map[c] = "date"
            elif cl in ("close","price_usd","price","value"): col_map[c] = "price_usd"
            elif cl in ("high","high_usd"):                   col_map[c] = "high_usd"
            elif cl in ("low","low_usd"):                     col_map[c] = "low_usd"
            elif cl in ("open","open_usd"):                   col_map[c] = "open_usd"
        df = df.rename(columns=col_map)
        if "date" not in df.columns:
            df = df.reset_index().rename(columns={"index": "date"})
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
        return df

    # Global Gold
    data["global_gold"] = load_yf_csv(os.path.join(DATA_DIR, "global_gold_prices.csv"))

    # Oil prices
    data["brent"] = load_yf_csv(os.path.join(DATA_DIR, "global_brent_oil_prices.csv"))
    data["wti"]   = load_yf_csv(os.path.join(DATA_DIR, "global_wti_price_prices.csv"))

    # OPEC (monthly, may not have date column)
    opec_raw = pd.read_csv(os.path.join(DATA_DIR, "opec_oil_prices.csv"))
    opec_raw.columns = opec_raw.columns.str.strip()
    # Rename date column if present
    for c in opec_raw.columns:
        if c.lower().strip() == "date":
            opec_raw = opec_raw.rename(columns={c: "date"})
            opec_raw["date"] = pd.to_datetime(opec_raw["date"], dayfirst=True, errors="coerce")
            break
    else:
        # No date column — generate monthly from 2016-01-01
        opec_raw["date"] = pd.date_range(start="2016-01-01", periods=len(opec_raw), freq="MS")
    price_col = next((c for c in opec_raw.columns if any(k in c.lower() for k in ["price","close","value"])), None)
    opec_raw["price_usd"] = pd.to_numeric(opec_raw[price_col], errors="coerce") if price_col else np.nan
    data["opec"] = opec_raw[["date","price_usd"]].dropna().sort_values("date").reset_index(drop=True)

    # Avg brent in budget
    budget_brent = pd.read_csv(os.path.join(DATA_DIR, "egy_avg_brent_price_in_budget.csv"))
    budget_brent.columns = budget_brent.columns.str.strip()
    data["budget_brent"] = budget_brent

    # Subsidies
    elec = pd.read_excel(os.path.join(DATA_DIR, "egy_subsidies_on_electricity_expected_vs_actual.xlsx"))
    elec.columns = ["year","planned_elec","actual_elec"]
    elec["year"] = elec["year"].astype(str).str.strip()
    data["sub_elec"] = elec

    petro = pd.read_excel(os.path.join(DATA_DIR, "egy_subsidies_on_petroleum_products_expected_vs_actual.xlsx"))
    petro.columns = ["year","planned_petro","actual_petro"]
    petro["year"] = petro["year"].astype(str).str.strip()
    data["sub_petro"] = petro

    # FX rates (raw yfinance or cleaned)
    fx_files = {
        "EUR/USD": "global_eurusd_rate_prices.csv",
        "GBP/USD": "global_gbpusd_rate_prices.csv",
        "JPY/USD": "global_jpyusd_rate_prices.csv",
        "CNY/USD": "global_cnyusd_rate_prices.csv",
        "CHF/USD": "global_chfusd_rate_prices.csv",
        "NOK/USD": "global_nokusd_rate_prices.csv",
        "RUB/USD": "global_rubusd_rate_prices.csv",
    }
    fx_all = {}
    for name, fname in fx_files.items():
        fx_all[name] = load_yf_csv(os.path.join(DATA_DIR, fname))
    data["fx"] = fx_all

    return data

data = load_all()

# SIDEBAR
with st.sidebar:
    st.markdown("## 🇪🇬 Egypt Finance")
    st.markdown("**Gold & Oil Prediction System**")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["🏠 Overview", "📈 Inflation & CPI", "💱 Exchange Rates",
         "🥇 Gold Prices", "🛢️ Oil Prices", "💰 Budget & Subsidies", "🔗 Correlations",
         "🤖 AI Model", "📊 Stock Markets"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**Date Range Filter**")
    year_min, year_max = 2016, 2026
    year_range = st.slider("Select Years", year_min, year_max, (2020, 2026), step=1)
    date_start = pd.Timestamp(f"{year_range[0]}-01-01")
    date_end   = pd.Timestamp(f"{year_range[1]}-12-31")

    st.markdown("---")
    st.markdown("<small style='color:#444'>Egypt Macroeconomic Intelligence</small>", unsafe_allow_html=True)

# HELPER: filter by date
def filt(df, col="date"):
    if col in df.columns:
        return df[(df[col] >= date_start) & (df[col] <= date_end)]
    return df

# PAGES

# OVERVIEW
if page == "🏠 Overview":
    st.markdown('<div class="page-title"><span class="page-title-icon">🇪🇬</span><span class="page-title-text">Egypt Financial Dashboard</span><span class="page-title-sub">Macroeconomic &amp; Market Data · 2016 – 2026</span></div>', unsafe_allow_html=True)
    st.markdown("<p>Macroeconomic & Market Data · 2016 – 2026</p>", unsafe_allow_html=True)

    # KPIs
    inf_df   = data["inflation"]
    egp_df   = data["egpusd"]
    gold_df  = data["egy_gold"]
    brent_df = data["brent"]

    latest_inf  = inf_df["headline"].dropna().iloc[-1]
    prev_inf    = inf_df["headline"].dropna().iloc[-2]
    latest_egp  = egp_df["rate"].iloc[-1]
    prev_egp    = egp_df["rate"].iloc[-2]
    latest_gold = gold_df["price_oz_egp"].iloc[-1]
    prev_gold   = gold_df["price_oz_egp"].iloc[-2]
    # KPIs always use full dataset (ignore date slider)
    latest_brent= brent_df["price_usd"].iloc[-1]
    prev_brent  = brent_df["price_usd"].iloc[-2]

    def delta_html(val, prev, fmt=".2f", suffix=""):
        chg = val - prev
        pct = (chg / abs(prev) * 100) if prev else 0
        cls = "kpi-delta-pos" if chg >= 0 else "kpi-delta-neg"
        arrow = "▲" if chg >= 0 else "▼"
        return f'<span class="{cls}">{arrow} {abs(chg):{fmt}}{suffix} ({abs(pct):.1f}%)</span>'

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">🔴 Headline Inflation</div>
            <div class="kpi-value">{latest_inf:.1f}%</div>
            {delta_html(latest_inf, prev_inf, ".1f", "%")}
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">💱 EGP / USD (CBE)</div>
            <div class="kpi-value">{latest_egp:.2f}</div>
            {delta_html(latest_egp, prev_egp)}
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">🥇 Gold (EGP/oz)</div>
            <div class="kpi-value">{latest_gold:,.0f}</div>
            {delta_html(latest_gold, prev_gold, ",.0f")}
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">🛢️ Brent Oil (USD)</div>
            <div class="kpi-value">${latest_brent:.1f}</div>
            {delta_html(latest_brent, prev_brent, ".1f", "$")}
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # Mini charts row 1
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-header">📉 Headline & Core Inflation (CBE)</div>', unsafe_allow_html=True)
        inf_f = inf_df[(inf_df["date"] >= date_start) & (inf_df["date"] <= date_end)]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=inf_f["date"], y=inf_f["headline"], name="Headline",
                                  line=dict(color=COLORS[0], width=2), fill="tozeroy",
                                  fillcolor="rgba(88,166,255,0.08)"))
        fig.add_trace(go.Scatter(x=inf_f["date"], y=inf_f["core"], name="Core",
                                  line=dict(color=COLORS[2], width=2)))
        fig.update_layout(**base_layout(height=300))
        fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="section-header">💱 EGP/USD Exchange Rate (CBE)</div>', unsafe_allow_html=True)
        egp_f = filt(egp_df)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=egp_f["date"], y=egp_f["rate"], name="EGP/USD",
                                   line=dict(color=COLORS[1], width=2), fill="tozeroy",
                                   fillcolor="rgba(63,185,80,0.08)"))
        fig2.update_layout(**base_layout(height=300))
        st.plotly_chart(fig2, use_container_width=True)

    # Mini charts row 2
    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<div class="section-header">🥇 Egyptian Gold Price (EGP/oz)</div>', unsafe_allow_html=True)
        gf = filt(gold_df)
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=gf["date"], y=gf["price_oz_egp"], name="Gold EGP",
                                   line=dict(color=COLORS[2], width=2), fill="tozeroy",
                                   fillcolor="rgba(227,179,65,0.08)"))
        fig3.update_layout(**base_layout(height=300))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.markdown('<div class="section-header">🛢️ Brent vs WTI vs OPEC Oil (USD)</div>', unsafe_allow_html=True)
        bf = filt(data["brent"]); wf = filt(data["wti"]); of = filt(data["opec"])
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=bf["date"], y=bf["price_usd"], name="Brent", line=dict(color=COLORS[0], width=1.5)))
        fig4.add_trace(go.Scatter(x=wf["date"], y=wf["price_usd"], name="WTI",   line=dict(color=COLORS[3], width=1.5)))
        fig4.add_trace(go.Scatter(x=of["date"], y=of["price_usd"], name="OPEC",  line=dict(color=COLORS[2], width=1.5)))
        fig4.update_layout(**base_layout(height=300))
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('''<div style="background:linear-gradient(90deg,#1a1a2e,#16213e);border-left:4px solid #e3b341;border-radius:8px;padding:0.7rem 1rem;margin-top:0.5rem;">
        <span style="color:#e3b341;font-weight:700;">⚠️ Data Note — WTI Negative Price (April 2020)</span><br>
        <span style="color:#c9d1d9;font-size:0.85rem;">The negative WTI price in April 2020 is real market data, not an error. It occurred due to a historic collapse in global demand during the COVID-19 pandemic combined with storage capacity reaching its limit.</span>
    </div>''', unsafe_allow_html=True)

# INFLATION & CPI
elif page == "📈 Inflation & CPI":
    st.markdown('<div class="page-title"><span class="page-title-icon">📈</span><span class="page-title-text">Inflation &amp; CPI</span><span class="page-title-sub">CBE Monthly · IMF Annual · Heatmap Analysis</span></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["CBE Monthly Inflation", "IMF CPI (Annual)"])

    with tab1:
        inf_f = data["inflation"]
        inf_f = inf_f[(inf_f["date"] >= date_start) & (inf_f["date"] <= date_end)]

        # KPIs
        k1, k2, k3, k4 = st.columns(4)
        metrics = [
            ("Headline Inflation", "headline", COLORS[0]),
            ("Core Inflation",     "core",     COLORS[2]),
            ("Regulated Items",    "regulated", COLORS[4]),
            ("Fruits & Veg",       "fruits_veg",COLORS[3]),
        ]
        for col, (label, field, _) in zip([k1,k2,k3,k4], metrics):
            val = inf_f[field].dropna().iloc[-1] if len(inf_f) and not inf_f[field].dropna().empty else None
            with col:
                st.metric(label, f"{val:.1f}%" if val else "N/A")

        st.markdown('<div class="section-header">All Inflation Components Over Time</div>', unsafe_allow_html=True)
        fig = go.Figure()
        for i, (label, field, color) in enumerate(metrics):
            fig.add_trace(go.Scatter(x=inf_f["date"], y=inf_f[field], name=label,
                                      line=dict(color=color, width=2)))
        fig.update_layout(**base_layout(height=420))
        fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-header">Monthly Inflation Heatmap</div>', unsafe_allow_html=True)
        hmap = inf_f.copy()
        hmap["month"] = hmap["date"].dt.month_name().str[:3]
        hmap["year"]  = hmap["date"].dt.year
        pivot = hmap.pivot_table(index="year", columns="month", values="headline", aggfunc="mean")
        month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        pivot = pivot.reindex(columns=[m for m in month_order if m in pivot.columns])
        figH = go.Figure(go.Heatmap(
            z=pivot.values, x=pivot.columns, y=pivot.index.astype(str),
            colorscale="RdYlGn_r", colorbar=dict(title="%"),
            text=np.round(pivot.values,1).astype(str),
            texttemplate="%{text}%"
        ))
        figH.update_layout(**base_layout(height=350))
        st.plotly_chart(figH, use_container_width=True)

    with tab2:
        cpi = data["cpi"]
        cpi_f = cpi[(cpi["year"] >= year_range[0]) & (cpi["year"] <= year_range[1])]

        st.markdown('<div class="section-header">IMF CPI — Annual % Change</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=cpi_f["year"], y=cpi_f["cpi"],
                              marker_color=[COLORS[3] if v > 15 else COLORS[0] for v in cpi_f["cpi"]],
                              name="CPI %"))
        fig.add_hline(y=10, line_dash="dot", line_color=COLORS[2], annotation_text="10% threshold")
        fig.update_layout(**base_layout(height=420))
        fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            cpi_f.rename(columns={"year":"Year","cpi":"CPI % Change"})\
                 .style.background_gradient(cmap="RdYlGn_r", subset=["CPI % Change"]),
            use_container_width=True, hide_index=True
        )

# EXCHANGE RATES 
elif page == "💱 Exchange Rates":
    st.markdown('<div class="page-title"><span class="page-title-icon">💱</span><span class="page-title-text">Exchange Rates</span><span class="page-title-sub">EGP/USD Official Rate · Global FX Comparison</span></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["EGP / USD (CBE)", "Global FX Rates"])

    with tab1:
        egp_f = filt(data["egpusd"])

        k1, k2, k3 = st.columns(3)
        latest  = egp_f["rate"].iloc[-1]
        mn      = egp_f["rate"].min()
        mx      = egp_f["rate"].max()
        k1.metric("Latest Rate", f"{latest:.4f} EGP")
        k2.metric("Period Low",  f"{mn:.4f} EGP")
        k3.metric("Period High", f"{mx:.4f} EGP")

        st.markdown('<div class="section-header">EGP / USD Daily Rate (CBE Official)</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=egp_f["date"], y=egp_f["rate"], name="EGP/USD",
                                  line=dict(color=COLORS[1], width=1.5),
                                  fill="tozeroy", fillcolor="rgba(63,185,80,0.07)"))

        # Add key event annotations
        events = {
            "2016-11-03": ("EGP Float\n2016", COLORS[3]),
            "2022-10-27": ("EGP Float\n2022", COLORS[3]),
            "2024-03-01": ("EGP Float\n2024", COLORS[3]),
        }
        for date_str, (label, color) in events.items():
            dt = pd.Timestamp(date_str)
            if date_start <= dt <= date_end:
                fig.add_shape(type="line",
                              x0=dt, x1=dt, y0=0, y1=1,
                              xref="x", yref="paper",
                              line=dict(color=color, width=1.5, dash="dash"))
                fig.add_annotation(x=dt, y=0.95, xref="x", yref="paper",
                                   text=label.replace("\n", "<br>"),
                                   showarrow=False, font=dict(color=color, size=10),
                                   bgcolor="rgba(0,0,0,0.4)", borderpad=3)

        fig.update_layout(**base_layout(height=420))
        st.plotly_chart(fig, use_container_width=True)

        # Rolling avg
        st.markdown('<div class="section-header">30-Day & 90-Day Rolling Average</div>', unsafe_allow_html=True)
        egp_r = egp_f.copy()
        egp_r["ma30"] = egp_r["rate"].rolling(30).mean()
        egp_r["ma90"] = egp_r["rate"].rolling(90).mean()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=egp_r["date"], y=egp_r["rate"],   name="Daily",  line=dict(color=COLORS[0], width=1, dash="dot")))
        fig2.add_trace(go.Scatter(x=egp_r["date"], y=egp_r["ma30"],   name="MA-30",  line=dict(color=COLORS[2], width=2)))
        fig2.add_trace(go.Scatter(x=egp_r["date"], y=egp_r["ma90"],   name="MA-90",  line=dict(color=COLORS[3], width=2)))
        fig2.update_layout(**base_layout(height=350))
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        fx = data["fx"]
        selected = st.multiselect("Select Currencies", list(fx.keys()), default=["EUR/USD","GBP/USD","CNY/USD"])

        if selected:
            st.markdown('<div class="section-header">Selected FX Rates vs USD (Normalized to 100)</div>', unsafe_allow_html=True)
            fig = go.Figure()
            for i, name in enumerate(selected):
                df = filt(fx[name])
                base = df["price_usd"].iloc[0] if len(df) else 1
                normalized = (df["price_usd"] / base) * 100
                fig.add_trace(go.Scatter(x=df["date"], y=normalized, name=name,
                                          line=dict(color=COLORS[i % len(COLORS)], width=2)))
            fig.add_hline(y=100, line_dash="dot", line_color="#444")
            fig.update_layout(**base_layout(height=420))
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="section-header">Raw Values — Latest Snapshot</div>', unsafe_allow_html=True)
            rows = []
            for name in list(fx.keys()):
                df = filt(fx[name])
                if len(df):
                    rows.append({
                        "Pair": name,
                        "Latest": round(df["price_usd"].iloc[-1], 4),
                        "Period High": round(df["price_usd"].max(), 4),
                        "Period Low":  round(df["price_usd"].min(), 4),
                        "Chg %": round((df["price_usd"].iloc[-1]/df["price_usd"].iloc[0]-1)*100, 2)
                    })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# GOLD PRICES
elif page == "🥇 Gold Prices":
    st.markdown('<div class="page-title"><span class="page-title-icon">🥇</span><span class="page-title-text">Gold Prices</span><span class="page-title-sub">Egyptian EGP · Global USD · Candlestick Charts</span></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Egyptian Gold (EGP)", "Global Gold (USD)"])

    with tab1:
        gf = filt(data["egy_gold"])
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Latest (EGP/oz)", f"{gf['price_oz_egp'].iloc[-1]:,.0f}")
        k2.metric("Period High",     f"{gf['price_oz_egp'].max():,.0f}")
        k3.metric("Period Low",      f"{gf['price_oz_egp'].min():,.0f}")
        chg = (gf['price_oz_egp'].iloc[-1]/gf['price_oz_egp'].iloc[0]-1)*100
        k4.metric("Period Return",   f"{chg:+.1f}%")

        st.markdown('<div class="section-header">Gold Price EGP/oz — Candlestick</div>', unsafe_allow_html=True)
        gf_m = gf.set_index("date").resample("W").agg(
            open=("open_price_egp","first"), high=("high_price_egp","max"),
            low=("low_price_egp","min"),   close=("price_oz_egp","last")
        ).dropna().reset_index()

        fig = go.Figure(go.Candlestick(
            x=gf_m["date"], open=gf_m["open"], high=gf_m["high"],
            low=gf_m["low"], close=gf_m["close"], name="Gold EGP",
            increasing_line_color=COLORS[1], decreasing_line_color=COLORS[3]
        ))
        fig.update_layout(**base_layout(height=450))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        gg = filt(data["global_gold"])
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Latest (USD/oz)", f"${gg['price_usd'].iloc[-1]:,.0f}")
        k2.metric("Period High",     f"${gg['price_usd'].max():,.0f}")
        k3.metric("Period Low",      f"${gg['price_usd'].min():,.0f}")
        chg = (gg['price_usd'].iloc[-1]/gg['price_usd'].iloc[0]-1)*100
        k4.metric("Period Return",   f"{chg:+.1f}%")

        st.markdown('<div class="section-header">Global Gold Price USD/oz — Candlestick</div>', unsafe_allow_html=True)
        gg_m = gg.set_index("date").resample("W").agg(
            open=("open_usd","first"), high=("high_usd","max"),
            low=("low_usd","min"),    close=("price_usd","last")
        ).dropna().reset_index()

        fig2 = go.Figure(go.Candlestick(
            x=gg_m["date"], open=gg_m["open"], high=gg_m["high"],
            low=gg_m["low"], close=gg_m["close"], name="Gold USD",
            increasing_line_color=COLORS[1], decreasing_line_color=COLORS[3]
        ))
        fig2.update_layout(**base_layout(height=450))
        st.plotly_chart(fig2, use_container_width=True)

        # EGP vs USD gold comparison
        st.markdown('<div class="section-header">EGP Gold vs USD Gold — Normalized Comparison</div>', unsafe_allow_html=True)
        gf2 = filt(data["egy_gold"])
        fig3 = go.Figure()
        b1 = gg["price_usd"].iloc[0]; b2 = gf2["price_oz_egp"].iloc[0]
        fig3.add_trace(go.Scatter(x=gg["date"],  y=gg["price_usd"]/b1*100,    name="Global USD",   line=dict(color=COLORS[2], width=2)))
        fig3.add_trace(go.Scatter(x=gf2["date"], y=gf2["price_oz_egp"]/b2*100, name="Egypt EGP",  line=dict(color=COLORS[0], width=2)))
        fig3.add_hline(y=100, line_dash="dot", line_color="#444", annotation_text="Base = 100")
        fig3.update_layout(**base_layout(height=380))
        st.plotly_chart(fig3, use_container_width=True)

# OIL PRICES 
elif page == "🛢️ Oil Prices":
    st.markdown('<div class="page-title"><span class="page-title-icon">🛢️</span><span class="page-title-text">Oil Prices</span><span class="page-title-sub">Brent · WTI · OPEC Basket · Egypt Budget</span></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Price Comparison", "Egypt Budget vs Brent"])

    with tab1:
        bf = filt(data["brent"]); wf = filt(data["wti"]); of = filt(data["opec"])

        k1, k2, k3 = st.columns(3)
        k1.metric("Brent (USD)",      f"${bf['price_usd'].iloc[-1]:.2f}" if len(bf) else "N/A")
        k2.metric("WTI (USD)",        f"${wf['price_usd'].iloc[-1]:.2f}" if len(wf) else "N/A")
        k3.metric("OPEC Basket (USD)",f"${of['price_usd'].iloc[-1]:.2f}" if len(of) else "N/A")

        st.markdown('<div class="section-header">Brent | WTI | OPEC Basket — Daily Prices</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=bf["date"], y=bf["price_usd"], name="Brent", line=dict(color=COLORS[0], width=2)))
        fig.add_trace(go.Scatter(x=wf["date"], y=wf["price_usd"], name="WTI",   line=dict(color=COLORS[3], width=2)))
        fig.add_trace(go.Scatter(x=of["date"], y=of["price_usd"], name="OPEC",  line=dict(color=COLORS[2], width=2)))
        fig.update_yaxes(tickprefix="$")
        fig.update_layout(**base_layout(height=430))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('''<div style="background:linear-gradient(90deg,#1a1a2e,#16213e);border-left:4px solid #e3b341;border-radius:8px;padding:0.9rem 1.2rem;margin-top:0.5rem;">
        <span style="color:#e3b341;font-weight:700;font-size:0.95rem;">⚠️ Data Note — WTI Negative Price (April 2020)</span><br><br>
        <span style="color:#c9d1d9;font-size:0.88rem;">
        The negative WTI crude oil price recorded in April 2020 (<b style="color:#f85149;">−$37.63/bbl</b>) is <b>real and accurate market data</b> — not an error in the dataset.<br><br>
        This unprecedented event was caused by two simultaneous shocks:<br>
        &nbsp;&nbsp;🦠 <b>Demand Shock:</b> Global COVID-19 lockdowns caused oil demand to collapse virtually overnight.<br>
        &nbsp;&nbsp;🏭 <b>Supply Glut:</b> Physical storage facilities reached full capacity, forcing sellers to pay buyers to take delivery of oil contracts.
        </span>
    </div>''', unsafe_allow_html=True)

        # Spread
        st.markdown('<div class="section-header">Brent – WTI Spread (USD)</div>', unsafe_allow_html=True)
        merged = pd.merge(bf[["date","price_usd"]], wf[["date","price_usd"]], on="date", suffixes=("_b","_w"))
        merged["spread"] = merged["price_usd_b"] - merged["price_usd_w"]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=merged["date"], y=merged["spread"], name="Spread",
                               marker_color=[COLORS[1] if v >= 0 else COLORS[3] for v in merged["spread"]]))
        fig2.add_hline(y=0, line_color="#555")
        fig2.update_layout(**base_layout(height=320))
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        bb = data["budget_brent"].copy()
        bb.columns = bb.columns.str.strip()
        for c in bb.columns[1:]:
            bb[c] = pd.to_numeric(bb[c], errors="coerce")

        st.markdown('<div class="section-header">Egypt Budget: Planned vs Actual Brent Price (USD/bbl)</div>', unsafe_allow_html=True)
        fig = go.Figure()
        if "avg_brent_price_planned" in bb.columns:
            fig.add_trace(go.Bar(x=bb["budget_year"], y=bb["avg_brent_price_planned"],
                                  name="Planned", marker_color=COLORS[0], opacity=0.8))
        if "avg_brent_price_actual" in bb.columns:
            fig.add_trace(go.Bar(x=bb["budget_year"], y=bb["avg_brent_price_actual"],
                                  name="Actual", marker_color=COLORS[1], opacity=0.9))
        fig.update_layout(**base_layout(height=420), barmode="group")
        fig.update_yaxes(tickprefix="$")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(bb, use_container_width=True, hide_index=True)

# BUDGET & SUBSIDIES
elif page == "💰 Budget & Subsidies":
    st.markdown('<div class="page-title"><span class="page-title-icon">💰</span><span class="page-title-text">Budget &amp; Subsidies</span><span class="page-title-sub">Petroleum · Electricity · Planned vs Actual</span></div>', unsafe_allow_html=True)

    sub_e = data["sub_elec"].copy()
    sub_p = data["sub_petro"].copy()
    for c in ["planned_elec","actual_elec"]:
        sub_e[c] = pd.to_numeric(sub_e[c], errors="coerce")
    for c in ["planned_petro","actual_petro"]:
        sub_p[c] = pd.to_numeric(sub_p[c], errors="coerce")

    tab1, tab2, tab3 = st.tabs(["Petroleum Subsidies", "Electricity Subsidies", "Combined View"])

    with tab1:
        st.markdown('<div class="section-header">Petroleum Subsidies: Planned vs Actual (EGP Millions)</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=sub_p["year"], y=sub_p["planned_petro"], name="Planned",
                              marker_color=COLORS[0], opacity=0.8))
        fig.add_trace(go.Bar(x=sub_p["year"], y=sub_p["actual_petro"],  name="Actual",
                              marker_color=COLORS[3], opacity=0.9))
        fig.update_layout(**base_layout(height=420), barmode="group")
        fig.update_yaxes(tickformat=",")
        st.plotly_chart(fig, use_container_width=True)

        sub_p["variance"] = sub_p["actual_petro"] - sub_p["planned_petro"]
        sub_p["var_%"] = (sub_p["variance"] / sub_p["planned_petro"] * 100).round(1)
        st.markdown('<div class="section-header">Variance (Actual – Planned)</div>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Bar(
            x=sub_p["year"], y=sub_p["variance"],
            marker_color=[COLORS[3] if v > 0 else COLORS[1] for v in sub_p["variance"]],
            text=sub_p["var_%"].astype(str)+"%", textposition="outside"
        ))
        fig2.update_layout(**base_layout(height=340))
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-header">Electricity Subsidies: Planned vs Actual (EGP Millions)</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=sub_e["year"], y=sub_e["planned_elec"], name="Planned",
                              marker_color=COLORS[4], opacity=0.8))
        fig.add_trace(go.Bar(x=sub_e["year"], y=sub_e["actual_elec"],  name="Actual",
                              marker_color=COLORS[2], opacity=0.9))
        fig.update_layout(**base_layout(height=420), barmode="group")
        fig.update_yaxes(tickformat=",")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        merged_sub = pd.merge(sub_p, sub_e, on="year", how="outer")
        merged_sub["total_planned"] = merged_sub["planned_petro"].fillna(0) + merged_sub["planned_elec"].fillna(0)
        merged_sub["total_actual"]  = merged_sub["actual_petro"].fillna(0)  + merged_sub["actual_elec"].fillna(0)

        st.markdown('<div class="section-header">Total Subsidies (Petroleum + Electricity)</div>', unsafe_allow_html=True)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=merged_sub["year"], y=merged_sub["total_planned"],
                              name="Total Planned", marker_color=COLORS[0], opacity=0.8), secondary_y=False)
        fig.add_trace(go.Bar(x=merged_sub["year"], y=merged_sub["total_actual"],
                              name="Total Actual",  marker_color=COLORS[3], opacity=0.9), secondary_y=False)
        fig.update_layout(**base_layout(height=450), barmode="group")
        fig.update_yaxes(tickformat=",")
        st.plotly_chart(fig, use_container_width=True)

        # Pie chart — use latest year with actual data available
        latest_planned = merged_sub.dropna(subset=["planned_petro","planned_elec"]).iloc[-1]
        latest_actual  = merged_sub.dropna(subset=["actual_petro","actual_elec"]).iloc[-1]
        st.markdown(f'<div class="section-header">Subsidy Mix — Planned: {latest_planned["year"]} | Actual: {latest_actual["year"]}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        for col, label, petro_val, elec_val, yr in [
            (c1, "Planned", latest_planned["planned_petro"], latest_planned["planned_elec"], latest_planned["year"]),
            (c2, "Actual",  latest_actual["actual_petro"],   latest_actual["actual_elec"],   latest_actual["year"])
        ]:
            figP = go.Figure(go.Pie(
                labels=["Petroleum","Electricity"],
                values=[petro_val, elec_val],
                marker_colors=[COLORS[2], COLORS[4]],
                hole=0.4
            ))
            figP.update_layout(paper_bgcolor=PAPER_BG, font=dict(color=FONT_COLOR),
                                height=280, margin=dict(t=30,b=10,l=10,r=10),
                                title=dict(text=f"{label} ({yr})", font=dict(color=FONT_COLOR)))
            col.plotly_chart(figP, use_container_width=True)

# CORRELATIONS
elif page == "🔗 Correlations":
    st.markdown('<div class="page-title"><span class="page-title-icon">🔗</span><span class="page-title-text">Correlation Analysis</span><span class="page-title-sub">Matrix · Scatter · Dual-Axis Time Series</span></div>', unsafe_allow_html=True)

    # Build monthly merged dataset
    @st.cache_data
    def build_corr_df():
        egp = data["egpusd"].set_index("date")["rate"].resample("MS").mean()
        inf = data["inflation"].set_index("date")["headline"].resample("MS").mean()
        gold_egy = data["egy_gold"].set_index("date")["price_oz_egp"].resample("MS").mean()
        gold_usd = data["global_gold"].set_index("date")["price_usd"].resample("MS").mean()
        brent    = data["brent"].set_index("date")["price_usd"].resample("MS").mean()
        wti      = data["wti"].set_index("date")["price_usd"].resample("MS").mean()

        df = pd.concat([egp, inf, gold_egy, gold_usd, brent, wti], axis=1)
        df.columns = ["EGP/USD","Inflation %","Gold EGP","Gold USD","Brent","WTI"]
        return df.dropna()

    corr_df = build_corr_df()
    corr_df_f = corr_df[(corr_df.index >= date_start) & (corr_df.index <= date_end)]

    st.markdown('<div class="section-header">Correlation Matrix (Monthly Averages)</div>', unsafe_allow_html=True)
    corr_mat = corr_df_f.corr().round(2)
    figC = go.Figure(go.Heatmap(
        z=corr_mat.values, x=corr_mat.columns, y=corr_mat.index,
        colorscale="RdBu", zmid=0, zmin=-1, zmax=1,
        text=corr_mat.values.round(2), texttemplate="%{text}",
        colorbar=dict(title="r")
    ))
    figC.update_layout(**base_layout(height=480))
    st.plotly_chart(figC, use_container_width=True)

    # Scatter
    st.markdown('<div class="section-header">Scatter: Select Two Variables</div>', unsafe_allow_html=True)
    cols = list(corr_df_f.columns)
    c1, c2 = st.columns(2)
    x_var = c1.selectbox("X Axis", cols, index=0)
    y_var = c2.selectbox("Y Axis", cols, index=2)

    scatter_df = corr_df_f[[x_var, y_var]].dropna()
    z = np.polyfit(scatter_df[x_var], scatter_df[y_var], 1)
    p = np.poly1d(z)
    x_line = np.linspace(scatter_df[x_var].min(), scatter_df[x_var].max(), 100)

    figS = go.Figure()
    figS.add_trace(go.Scatter(x=scatter_df[x_var], y=scatter_df[y_var], mode="markers",
                               marker=dict(color=COLORS[0], size=6, opacity=0.7), name="Data"))
    figS.add_trace(go.Scatter(x=x_line, y=p(x_line), mode="lines",
                               line=dict(color=COLORS[3], width=2, dash="dash"), name="Trend"))
    r = corr_df_f[x_var].corr(corr_df_f[y_var])
    figS.update_layout(**base_layout(f"r = {r:.3f}", height=420),
                        xaxis_title=x_var, yaxis_title=y_var)
    st.plotly_chart(figS, use_container_width=True)

    # Time series dual axis
    st.markdown('<div class="section-header">Dual-Axis Time Series</div>', unsafe_allow_html=True)
    figD = make_subplots(specs=[[{"secondary_y": True}]])
    figD.add_trace(go.Scatter(x=corr_df_f.index, y=corr_df_f[x_var], name=x_var,
                               line=dict(color=COLORS[0], width=2)), secondary_y=False)
    figD.add_trace(go.Scatter(x=corr_df_f.index, y=corr_df_f[y_var], name=y_var,
                               line=dict(color=COLORS[3], width=2)), secondary_y=True)
    figD.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=CHART_BG,
                        font=dict(color=FONT_COLOR, family="Inter"),
                        height=400, margin=dict(l=50,r=60,t=40,b=40),
                        legend=dict(bgcolor="rgba(0,0,0,0)"),
                        xaxis=dict(gridcolor=GRID_COLOR))
    figD.update_yaxes(title_text=x_var, gridcolor=GRID_COLOR, secondary_y=False)
    figD.update_yaxes(title_text=y_var, gridcolor=GRID_COLOR, secondary_y=True)
    st.plotly_chart(figD, use_container_width=True)

# AI MODEL
elif page == "🤖 AI Model":
    import pickle, warnings
    warnings.filterwarnings("ignore")

    st.markdown('''<div class="page-title">
        <span class="page-title-icon">🤖</span>
        <span class="page-title-text">AI Prediction Model</span>
        <span class="page-title-sub">Gold & Oil Price Forecasting · LightGBM · 7-Day Outlook</span>
    </div>''', unsafe_allow_html=True)

    @st.cache_data
    def load_master_ai():
        DATA_DIR_AI = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_csv(os.path.join(DATA_DIR_AI, "new_master_table.csv"))
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        new_cols = {}
        new_cols["log_gold"]       = np.log(df["gold_price_usd"])
        new_cols["gold_return"]    = new_cols["log_gold"].diff()
        new_cols["return_lag_1"]   = new_cols["gold_return"].shift(1)
        new_cols["return_lag_2"]   = new_cols["gold_return"].shift(2)
        new_cols["return_lag_3"]   = new_cols["gold_return"].shift(3)
        new_cols["return_lag_5"]   = new_cols["gold_return"].shift(5)
        new_cols["return_lag_10"]  = new_cols["gold_return"].shift(10)
        new_cols["return_lag_20"]  = new_cols["gold_return"].shift(20)
        new_cols["vol_7"]          = new_cols["gold_return"].rolling(7).std()
        new_cols["vol_20"]         = new_cols["gold_return"].rolling(20).std()
        new_cols["mom_7"]          = new_cols["log_gold"] - new_cols["log_gold"].shift(7)
        new_cols["sp500_mom"]      = np.log(df["sp500_price_usd"]) - np.log(df["sp500_price_usd"].shift(20))
        new_cols["log_price"]      = np.log(df["brent_oil_price_usd"])
        new_cols["log_price_lag1"] = new_cols["log_price"].shift(1)
        new_cols["price_trend_7"]  = new_cols["log_price"] - new_cols["log_price"].shift(7)
        new_cols["wti_brent_spread"] = df["wti_price_usd"] - df["brent_oil_price_usd"]
        new_cols["opec_pressure"]  = df["opec_basket_value"] * df["brent_oil_price_usd"]
        new_cols["oil_vol_x_vix"]  = df["oil_vi_value"] * df["vix_price_usd"]
        new_cols["oil_sp500"]      = df["brent_oil_price_usd"] * df["sp500_price_usd"]
        new_cols["oil_x_dxy"]      = df["brent_oil_price_usd"] * df["dollarindex_value"]
        new_cols["copper_oil_ratio"]= df["copper_price_usd"] / df["brent_oil_price_usd"]
        new_cols["geo_risk_oil"]   = df["ai_gpr_gpr_oil"] * df["brent_oil_price_usd"]
        new_cols["net_energy_imports"] = df["egypt_energy_fuel_imports"] - df["egypt_energy_fuel_exports"]
        df2 = pd.concat([df, pd.DataFrame(new_cols)], axis=1)
        # gold return col named "return"
        df2["return"] = new_cols["gold_return"]
        return df2

    @st.cache_resource
    def load_models_ai():
        DATA_DIR_AI = os.path.dirname(os.path.abspath(__file__))
        models = {}
        for name, fname in [
            ("gold", "gold_price_top_model.pkl"),
            ("oil",  "oil_price_full_model.pkl"),
        ]:
            path = os.path.join(DATA_DIR_AI, fname)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    m = pickle.load(f)
                    models[name] = m.booster_
        return models

    df_master = load_master_ai()
    ai_models = load_models_ai()

    def predict_7_days_ai(df, booster, price_col, log_col, is_oil=False):
        df_sim = df.copy()
        last_date = df_sim["date"].max()
        feats = booster.feature_name()
        predictions = []

        for day in range(1, 8):
            valid = df_sim.dropna(subset=feats)
            if len(valid) == 0:
                break
            last = valid.tail(1)
            X = last[feats].values
            pred_return = booster.predict(X)[0]
            last_price = last[price_col].values[0]
            pred_price = last_price * np.exp(pred_return)
            next_date = last_date + pd.Timedelta(days=day)
            predictions.append({"date": next_date, "predicted_price": pred_price})

            new_row = last.copy()
            new_row["date"] = next_date
            new_row[price_col] = pred_price
            new_row[log_col] = np.log(pred_price)
            new_row["return"] = pred_return
            new_row["return_lag_1"] = last["return"].values[0]
            new_row["return_lag_2"] = last["return_lag_1"].values[0]
            new_row["return_lag_3"] = last["return_lag_2"].values[0]
            new_row["return_lag_5"] = last["return_lag_3"].values[0]
            new_row["return_lag_10"]= last["return_lag_5"].values[0]
            new_row["return_lag_20"]= last["return_lag_10"].values[0]
            df_sim = pd.concat([df_sim, new_row], ignore_index=True)

        return pd.DataFrame(predictions)

    tab_gold, tab_oil, tab_perf = st.tabs(["🥇 Gold Prediction", "🛢️ Oil Prediction", "📊 Model Performance"])

    with tab_gold:
        if "gold" in ai_models:
            gold_booster = ai_models["gold"]
            gold_feats = gold_booster.feature_name()
            gold_preds = predict_7_days_ai(df_master, gold_booster, "gold_price_usd", "log_gold")
            last_gold  = df_master["gold_price_usd"].dropna().iloc[-1]
            last_date_gold = df_master["date"].max()

            k1, k2, k3, k4 = st.columns(4)
            p1 = gold_preds["predicted_price"].iloc[0]
            p7 = gold_preds["predicted_price"].iloc[-1]
            k1.metric("Current Price", f"${last_gold:,.2f}")
            k2.metric("Tomorrow",      f"${p1:,.2f}", f"{(p1-last_gold)/last_gold*100:+.2f}%")
            k3.metric("Day 7",         f"${p7:,.2f}", f"{(p7-last_gold)/last_gold*100:+.2f}%")
            k4.metric("7-Day Outlook", "📈 Bullish" if p7 > last_gold else "📉 Bearish")

            st.markdown('<div class="section-header">🥇 Gold Price — Historical & 7-Day Forecast</div>', unsafe_allow_html=True)
            hist_g = df_master[["date","gold_price_usd"]].dropna().tail(60)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist_g["date"], y=hist_g["gold_price_usd"],
                                     name="Historical", line=dict(color=COLORS[2], width=2)))
            fig.add_trace(go.Scatter(x=gold_preds["date"], y=gold_preds["predicted_price"],
                                     name="Predicted", mode="lines+markers",
                                     line=dict(color=COLORS[0], width=2.5, dash="dash"),
                                     marker=dict(size=7)))
            fig.add_shape(type="rect", x0=gold_preds["date"].iloc[0], x1=gold_preds["date"].iloc[-1], y0=0, y1=1, xref="x", yref="paper", fillcolor="rgba(88,166,255,0.07)", line_width=0)
            fig.add_shape(type="line", x0=last_date_gold, x1=last_date_gold, y0=0, y1=1, xref="x", yref="paper", line=dict(dash="dot", color="#555", width=1.5))
            fig.update_layout(**base_layout("Gold USD/oz", height=430))
            fig.update_yaxes(tickprefix="$", tickformat=",")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="section-header">📋 Gold — Daily Forecast Breakdown</div>', unsafe_allow_html=True)
            gt = gold_preds.copy()
            gt["Day"]   = [f"Day {i+1}" for i in range(len(gt))]
            gt["Date"]  = gt["date"].dt.strftime("%a %d %b %Y")
            gt["Price (USD)"] = gt["predicted_price"].map(lambda x: f"${x:,.2f}")
            gt["Change"]      = gt["predicted_price"].map(lambda x: f"{(x-last_gold)/last_gold*100:+.2f}%")
            gt["Signal"]      = gt["predicted_price"].map(lambda x: "🟢 Up" if x > last_gold else "🔴 Down")
            st.dataframe(gt[["Day","Date","Price (USD)","Change","Signal"]],
                         use_container_width=True, hide_index=True)
        else:
            st.warning("Gold model file not found.")

    with tab_oil:
        if "oil" in ai_models:
            oil_booster = ai_models["oil"]

            # Prepare oil-specific df (return = oil return)
            df_oil = df_master.copy()
            df_oil["return"]        = df_oil["log_price"].diff()
            df_oil["return_lag_1"]  = df_oil["return"].shift(1)
            df_oil["return_lag_2"]  = df_oil["return"].shift(2)
            df_oil["return_lag_3"]  = df_oil["return"].shift(3)
            df_oil["return_lag_5"]  = df_oil["return"].shift(5)
            df_oil["return_lag_10"] = df_oil["return"].shift(10)
            df_oil["return_lag_20"] = df_oil["return"].shift(20)
            df_oil["vol_7"]  = df_oil["return"].rolling(7).std()
            df_oil["vol_20"] = df_oil["return"].rolling(20).std()
            df_oil["mom_7"]  = df_oil["log_price"] - df_oil["log_price"].shift(7)

            oil_preds  = predict_7_days_ai(df_oil, oil_booster, "brent_oil_price_usd", "log_price", is_oil=True)
            last_oil   = df_master["brent_oil_price_usd"].dropna().iloc[-1]
            last_date_oil = df_master["date"].max()

            k1, k2, k3, k4 = st.columns(4)
            p1o = oil_preds["predicted_price"].iloc[0]
            p7o = oil_preds["predicted_price"].iloc[-1]
            k1.metric("Current Price", f"${last_oil:,.2f}")
            k2.metric("Tomorrow",      f"${p1o:,.2f}", f"{(p1o-last_oil)/last_oil*100:+.2f}%")
            k3.metric("Day 7",         f"${p7o:,.2f}", f"{(p7o-last_oil)/last_oil*100:+.2f}%")
            k4.metric("7-Day Outlook", "📈 Bullish" if p7o > last_oil else "📉 Bearish")

            st.markdown('<div class="section-header">🛢️ Brent Oil — Historical & 7-Day Forecast</div>', unsafe_allow_html=True)
            hist_o = df_master[["date","brent_oil_price_usd"]].dropna().tail(60)
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=hist_o["date"], y=hist_o["brent_oil_price_usd"],
                                      name="Historical", line=dict(color=COLORS[3], width=2)))
            fig2.add_trace(go.Scatter(x=oil_preds["date"], y=oil_preds["predicted_price"],
                                      name="Predicted", mode="lines+markers",
                                      line=dict(color=COLORS[1], width=2.5, dash="dash"),
                                      marker=dict(size=7)))
            fig2.add_shape(type="rect", x0=oil_preds["date"].iloc[0], x1=oil_preds["date"].iloc[-1], y0=0, y1=1, xref="x", yref="paper", fillcolor="rgba(63,185,80,0.07)", line_width=0)
            fig2.add_shape(type="line", x0=last_date_oil, x1=last_date_oil, y0=0, y1=1, xref="x", yref="paper", line=dict(dash="dot", color="#555", width=1.5))
            fig2.update_layout(**base_layout("Brent Oil USD/bbl", height=430))
            fig2.update_yaxes(tickprefix="$")
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown('<div class="section-header">📋 Oil — Daily Forecast Breakdown</div>', unsafe_allow_html=True)
            ot = oil_preds.copy()
            ot["Day"]   = [f"Day {i+1}" for i in range(len(ot))]
            ot["Date"]  = ot["date"].dt.strftime("%a %d %b %Y")
            ot["Price (USD)"] = ot["predicted_price"].map(lambda x: f"${x:,.2f}")
            ot["Change"]      = ot["predicted_price"].map(lambda x: f"{(x-last_oil)/last_oil*100:+.2f}%")
            ot["Signal"]      = ot["predicted_price"].map(lambda x: "🟢 Up" if x > last_oil else "🔴 Down")
            st.dataframe(ot[["Day","Date","Price (USD)","Change","Signal"]],
                         use_container_width=True, hide_index=True)
        else:
            st.warning("Oil model file not found.")

    with tab_perf:
        import base64
        from pathlib import Path

        def img_to_b64(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()

        DATA_DIR_AI = os.path.dirname(os.path.abspath(__file__))

        # Gold Model Performance
        st.markdown('<div class="section-header">🥇 Gold Price Forecasting — Model Results</div>', unsafe_allow_html=True)

        # Gold metrics
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown("""<div class="kpi-card">
                <div class="kpi-label">MAE — Top-15</div>
                <div class="kpi-value" style="font-size:1.4rem;">$159.5</div>
                <div class="kpi-delta-pos">Full Model: $284.2</div>
            </div>""", unsafe_allow_html=True)
        with k2:
            st.markdown("""<div class="kpi-card">
                <div class="kpi-label">RMSE — Top-15</div>
                <div class="kpi-value" style="font-size:1.4rem;">$181.8</div>
                <div class="kpi-delta-pos">Full Model: $310.7</div>
            </div>""", unsafe_allow_html=True)
        with k3:
            st.markdown("""<div class="kpi-card">
                <div class="kpi-label">R² — Top-15</div>
                <div class="kpi-value" style="font-size:1.4rem;">0.500</div>
                <div class="kpi-delta-neg">Full Model: -0.462</div>
            </div>""", unsafe_allow_html=True)
        with k4:
            st.markdown("""<div class="kpi-card">
                <div class="kpi-label">MAPE — Top-15</div>
                <div class="kpi-value" style="font-size:1.4rem;">3.30%</div>
                <div class="kpi-delta-pos">Full Model: 5.80%</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")
        gold_img_path = os.path.join(DATA_DIR_AI, "gold_price_prediction_model.png")
        if os.path.exists(gold_img_path):
            st.image(gold_img_path, use_container_width=True,
                     caption="Gold Price Forecasting — Actual vs Predicted (Jan–Apr 2026)")
        else:
            st.warning("gold_price_prediction_model.png not found in app folder.")

        st.markdown("")

        # Oil Model Performance
        st.markdown('<div class="section-header">🛢️ Brent Oil Forecasting — Model Results</div>', unsafe_allow_html=True)

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown("""<div class="kpi-card">
                <div class="kpi-label">MAE — Top-20</div>
                <div class="kpi-value" style="font-size:1.4rem;">$5.41</div>
                <div class="kpi-delta-pos">Full Model: $11.19</div>
            </div>""", unsafe_allow_html=True)
        with k2:
            st.markdown("""<div class="kpi-card">
                <div class="kpi-label">RMSE — Top-20</div>
                <div class="kpi-value" style="font-size:1.4rem;">$7.35</div>
                <div class="kpi-delta-pos">Full Model: $14.39</div>
            </div>""", unsafe_allow_html=True)
        with k3:
            st.markdown("""<div class="kpi-card">
                <div class="kpi-label">R² — Top-20</div>
                <div class="kpi-value" style="font-size:1.4rem;">0.843</div>
                <div class="kpi-delta-pos">Full Model: 0.398</div>
            </div>""", unsafe_allow_html=True)
        with k4:
            st.markdown("""<div class="kpi-card">
                <div class="kpi-label">MAPE — Top-20</div>
                <div class="kpi-value" style="font-size:1.4rem;">5.79%</div>
                <div class="kpi-delta-pos">Full Model: 11.64%</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")
        oil_img_path = os.path.join(DATA_DIR_AI, "oil_price_prediction_model.png")
        if os.path.exists(oil_img_path):
            st.image(oil_img_path, use_container_width=True,
                     caption="Brent Oil Forecasting — Actual vs Predicted (Jan–Apr 2026)")
        else:
            st.warning("oil_price_prediction_model.png not found in app folder.")

        st.markdown("")

        # Correlation Heatmap
        st.markdown('<div class="section-header">🔗 Feature Correlation Heatmap</div>', unsafe_allow_html=True)
        corr_img_path = os.path.join(DATA_DIR_AI, "correlation_heatmap.png")
        if os.path.exists(corr_img_path):
            st.image(corr_img_path, use_container_width=True,
                     caption="Correlation Matrix — All Model Features")
        else:
            st.warning("correlation_heatmap.png not found in app folder.")

        st.markdown("")

        # Model Comparison Table
        st.markdown('<div class="section-header">📋 Model Comparison Summary</div>', unsafe_allow_html=True)
        import pandas as pd
        comparison = pd.DataFrame({
            "Asset":      ["Gold", "Gold", "Oil", "Oil"],
            "Model":      ["Top-15 Features", "Full Features", "Top-20 Features", "Full Features"],
            "MAE":        ["$159.5", "$284.2", "$5.41", "$11.19"],
            "RMSE":       ["$181.8", "$310.7", "$7.35", "$14.39"],
            "R²":         ["0.500", "-0.462", "0.843", "0.398"],
            "MAPE":       ["3.30%", "5.80%", "5.79%", "11.64%"],
            "Winner":     ["✅", "❌", "✅", "❌"],
        })
        st.dataframe(comparison, use_container_width=True, hide_index=True)
        st.caption("✅ Top-feature models outperform full-feature models on all metrics — less overfitting, better generalization.")

# STOCK MARKETS 
elif page == "📊 Stock Markets":
    import pickle, warnings
    warnings.filterwarnings("ignore")

    st.markdown('''<div class="page-title">
        <span class="page-title-icon">📊</span>
        <span class="page-title-text">Stock Markets Prediction</span>
        <span class="page-title-sub">Global & Egyptian Markets · LightGBM · 7-Day Forecast</span>
    </div>''', unsafe_allow_html=True)

    MARKETS = {
        "🇪🇬 EGX30":     {"col": "egx30_price_egp",              "currency": "EGP", "model": "standalone_EGX30_top_features_model"},
        "🇺🇸 NASDAQ":    {"col": "nasdaq_price_usd",             "currency": "USD", "model": "standalone_NASDAQ_top_features_model"},
        "🇺🇸 S&P 500":   {"col": "sp500_price_usd",              "currency": "USD", "model": "standalone_SP500_top_features_model"},
        "🇺🇸 Dow Jones": {"col": "dowjones_price_usd",           "currency": "USD", "model": "standalone_Dow_top_features_model"},
        "🇨🇳 Shanghai":  {"col": "china_shanghai_price_usd",     "currency": "USD", "model": "standalone_shanghai_top_features_model"},
        "🇭🇰 Hong Kong": {"col": "hongkong_hongkong_price_usd",  "currency": "USD", "model": "standalone_hongkong_top_features_model"},
        "🇬🇧 London":    {"col": "uk_london_price_usd",          "currency": "USD", "model": "standalone_london_top_features_model"},
        "🇯🇵 Tokyo":     {"col": "japan_tokyo_price_usd",        "currency": "USD", "model": "standalone_tokyo_top_features_model"},
    }

    @st.cache_data
    def load_stocks_data():
        DATA_DIR_S = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_csv(os.path.join(DATA_DIR_S, "new_master_table_stocks.csv"))
        df["date"] = pd.to_datetime(df["date"], dayfirst=False, format="mixed", errors="coerce")
        df = df.sort_values("date").reset_index(drop=True)
        return df

    @st.cache_resource
    def load_stock_model(model_name):
        DATA_DIR_S = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(DATA_DIR_S, f"{model_name}.pkl")
        if os.path.exists(path):
            with open(path, "rb") as f:
                m = pickle.load(f)
            return m.booster_ if hasattr(m, "booster_") else m
        return None

    def engineer_stock_features(df, target_col):
        d = df.copy()
        for col in d.columns:
            if d[col].dtype == "object":
                d[col] = pd.to_numeric(d[col], errors="coerce")
        d["real_rate_us"]      = d.get("usd_fedfunds_value", 0) - d.get("cpi_value", 0)
        d["real_rate_eu"]      = d.get("euro_interest_value", 0) - d.get("euro_inflation_value", 0)
        d["yield_spread_10_2"] = d.get("10y_treasury_historical_data_monthly_value", 0) - d.get("2y_treasury_historical_data_monthly_value", 0)
        d["yield_spread_10_1"] = d.get("10y_treasury_historical_data_monthly_value", 0) - d.get("1y_treasury_historical_data_monthly_value", 0)
        d["oil_x_dxy"]         = d.get("brent_oil_price_usd", 1) * d.get("dollarindex_value", 1)
        d["vix_x_dxy"]         = d.get("vix_price_usd", 1) * d.get("dollarindex_value", 1)
        d["gold_x_dxy"]        = d.get("gold_price_usd", 1) * d.get("dollarindex_value", 1)
        d["vix_mom"]           = d.get("vix_price_usd", pd.Series(0, index=d.index)).pct_change()
        d["oil_mom"]           = d.get("brent_oil_price_usd", pd.Series(0, index=d.index)).pct_change()
        d["gold_mom"]          = d.get("gold_price_usd", pd.Series(0, index=d.index)).pct_change()
        d["log_price"]         = np.log(d[target_col].replace(0, np.nan))
        d["return"]            = d["log_price"].diff()
        for w in [5, 10, 20, 50]:
            d[f"sma_{w}"]          = d[target_col].rolling(w).mean().shift(1)
            d[f"price_vs_sma_{w}"] = (d[target_col] / d[f"sma_{w}"] - 1).shift(1)
        _delta = d["return"].clip(lower=0)
        _loss  = (-d["return"]).clip(lower=0)
        _ag    = _delta.rolling(14).mean()
        _al    = _loss.rolling(14).mean().replace(0, 1e-9)
        d["rsi_14"]            = (100 - 100 / (1 + _ag / _al)).shift(1)
        _bb_mid                = d[target_col].rolling(20).mean()
        _bb_std                = d[target_col].rolling(20).std()
        d["bb_width"]          = (4 * _bb_std / _bb_mid).shift(1)
        d["day_of_week"]       = d["date"].dt.dayofweek
        d["month"]             = d["date"].dt.month
        d["quarter"]           = d["date"].dt.quarter
        d["is_month_end"]      = d["date"].dt.is_month_end.astype(int)
        d["is_quarter_end"]    = d["date"].dt.is_quarter_end.astype(int)
        for lag in [1,2,3,5,10,20]:
            d[f"return_lag_{lag}"] = d["return"].shift(lag)
        d["log_price_lag1"]    = d["log_price"].shift(1)
        d["vix_lag1"]          = d.get("vix_price_usd", pd.Series(0, index=d.index)).shift(1)
        d["gold_lag1"]         = d.get("gold_price_usd", pd.Series(0, index=d.index)).shift(1)
        d["oil_lag1"]          = d.get("brent_oil_price_usd", pd.Series(0, index=d.index)).shift(1)
        d["dxy_lag1"]          = d.get("dollarindex_value", pd.Series(0, index=d.index)).shift(1)
        d["vol_7"]             = d["return"].rolling(7).std().shift(1)
        d["vol_20"]            = d["return"].rolling(20).std().shift(1)
        d["vol_ratio"]         = d["vol_7"] / (d["vol_20"] + 1e-9)
        d["mom_7"]             = d["return"].rolling(7).mean().shift(1)
        d["mom_20"]            = d["return"].rolling(20).mean().shift(1)
        d["mom_crossover"]     = d["mom_7"] - d["mom_20"]
        d["price_trend_7"]     = d[target_col].rolling(7).mean().shift(1)
        d["price_trend_20"]    = d[target_col].rolling(20).mean().shift(1)
        return d

    def predict_stock_7d(df_eng, booster, target_col):
        feats = booster.feature_name()
        valid_feats = [f for f in feats if f in df_eng.columns]
        df_sim = df_eng.copy()
        last_date = df_sim["date"].max()
        preds = []
        for day in range(1, 8):
            row = df_sim.dropna(subset=valid_feats)
            if len(row) == 0:
                break
            last = row.tail(1)
            X = last[valid_feats].values
            pred_r = booster.predict(X)[0]
            last_price = last[target_col].values[0]
            pred_price = last_price * np.exp(pred_r)
            next_date = last_date + pd.Timedelta(days=day)
            preds.append({"date": next_date, "predicted_price": pred_price})
            new_row = last.copy()
            new_row["date"] = next_date
            new_row[target_col] = pred_price
            new_row["log_price"] = np.log(pred_price)
            new_row["return"] = pred_r
            new_row["return_lag_1"] = last["return"].values[0]
            new_row["return_lag_2"] = last["return_lag_1"].values[0]
            new_row["return_lag_3"] = last["return_lag_2"].values[0]
            new_row["return_lag_5"] = last["return_lag_3"].values[0]
            new_row["return_lag_10"]= last["return_lag_5"].values[0]
            new_row["return_lag_20"]= last["return_lag_10"].values[0]
            df_sim = pd.concat([df_sim, new_row], ignore_index=True)
        return pd.DataFrame(preds)

    df_stocks = load_stocks_data()

    # All Markets Snapshot
    st.markdown('<div class="section-header">🌍 All Markets — Current Snapshot</div>', unsafe_allow_html=True)
    snap_rows = []
    for mname, mdata in MARKETS.items():
        col = mdata["col"]
        cur = mdata["currency"]
        if col in df_stocks.columns:
            vals = df_stocks[col].dropna()
            if len(vals) >= 2:
                last = vals.iloc[-1]
                prev = vals.iloc[-2]
                chg  = (last - prev) / prev * 100
                snap_rows.append({"Market": mname, "Price": f"{last:,.2f} {cur}",
                                   "Daily Change": f"{chg:+.2f}%", "Signal": "🟢" if chg >= 0 else "🔴"})
    st.dataframe(pd.DataFrame(snap_rows), use_container_width=True, hide_index=True)

    st.markdown("")

    # Market Selector — Cards
    st.markdown('<div class="section-header">🔮 7-Day Price Forecast — Select a Market</div>', unsafe_allow_html=True)

    # CSS for market cards
    st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #161b22, #1f2937);
        border: 1px solid #30363d;
        border-radius: 12px;
        color: #c9d1d9;
        padding: 0.8rem 0.5rem;
        font-size: 0.85rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    div.stButton > button:hover {
        border-color: #58a6ff;
        color: #58a6ff;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(88,166,255,0.15);
    }
    div.stButton > button:focus {
        border-color: #C5A028;
        color: #C5A028;
        box-shadow: 0 4px 15px rgba(197,160,40,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

    # Market cards in 4 columns x 2 rows
    market_list = list(MARKETS.keys())
    if "selected_market" not in st.session_state:
        st.session_state.selected_market = market_list[0]

    row1 = st.columns(4)
    row2 = st.columns(4)
    all_cols = row1 + row2

    for i, (mname, col) in enumerate(zip(market_list, all_cols)):
        mdata = MARKETS[mname]
        mcol  = mdata["col"]
        cur   = mdata["currency"]
        if mcol in df_stocks.columns:
            vals = df_stocks[mcol].dropna()
            last = vals.iloc[-1] if len(vals) else 0
            prev = vals.iloc[-2] if len(vals) >= 2 else last
            chg  = (last - prev) / prev * 100 if prev else 0
            arrow = "▲" if chg >= 0 else "▼"
            color = "#3fb950" if chg >= 0 else "#f85149"
            is_selected = st.session_state.selected_market == mname
            border_color = "#C5A028" if is_selected else "#30363d"
            bg_color = "linear-gradient(135deg, #1B3A6B, #2E5FAC)" if is_selected else "linear-gradient(135deg, #161b22, #1f2937)"
            col.markdown(f"""
            <div style="background:{bg_color};border:2px solid {border_color};border-radius:12px;
                        padding:0.9rem 0.7rem;text-align:center;margin-bottom:0.5rem;
                        box-shadow:{'0 4px 15px rgba(197,160,40,0.2)' if is_selected else 'none'}">
                <div style="font-size:1.3rem">{mname.split()[0]}</div>
                <div style="font-size:0.82rem;font-weight:700;color:#f0f6fc;margin:0.2rem 0">{" ".join(mname.split()[1:])}</div>
                <div style="font-size:0.88rem;color:#c9d1d9">{last:,.0f} <span style="font-size:0.7rem">{cur}</span></div>
                <div style="font-size:0.78rem;color:{color};font-weight:600">{arrow} {abs(chg):.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
            if col.button("Select", key=f"btn_{i}"):
                st.session_state.selected_market = mname
                st.rerun()

    selected = st.session_state.selected_market
    minfo      = MARKETS[selected]
    target_col = minfo["col"]
    currency   = minfo["currency"]
    model_name = minfo["model"]

    booster = load_stock_model(model_name)

    if booster is None:
        st.warning(f"Model `{model_name}.pkl` not found — please add it to the app folder.")
    elif target_col not in df_stocks.columns:
        st.warning(f"Data column `{target_col}` not found.")
    else:
        df_eng    = engineer_stock_features(df_stocks, target_col)
        preds     = predict_stock_7d(df_eng, booster, target_col)
        last_price= df_stocks[target_col].dropna().iloc[-1]
        last_date = df_stocks["date"].max()

        k1, k2, k3, k4 = st.columns(4)
        p1   = preds["predicted_price"].iloc[0]
        p7   = preds["predicted_price"].iloc[-1]
        chg1 = (p1 - last_price) / last_price * 100
        chg7 = (p7 - last_price) / last_price * 100
        k1.metric("Current Price", f"{last_price:,.2f} {currency}")
        k2.metric("Tomorrow",      f"{p1:,.2f}",  f"{chg1:+.2f}%")
        k3.metric("Day 7",         f"{p7:,.2f}",  f"{chg7:+.2f}%")
        k4.metric("7-Day Outlook", "📈 Bullish" if p7 > last_price else "📉 Bearish")

        st.markdown("")
        hist  = df_stocks[["date", target_col]].dropna().tail(90)
        color = COLORS[2] if "EGX30" in selected else COLORS[0]
        fig   = go.Figure()
        fig.add_trace(go.Scatter(x=hist["date"], y=hist[target_col],
                                  name="Historical", line=dict(color=color, width=2)))
        fig.add_trace(go.Scatter(x=preds["date"], y=preds["predicted_price"],
                                  name="Predicted", mode="lines+markers",
                                  line=dict(color=COLORS[1], width=2.5, dash="dash"),
                                  marker=dict(size=7, color=COLORS[1])))
        fig.add_shape(type="rect",
                      x0=preds["date"].iloc[0], x1=preds["date"].iloc[-1],
                      y0=0, y1=1, xref="x", yref="paper",
                      fillcolor="rgba(63,185,80,0.07)", line_width=0)
        fig.add_shape(type="line",
                      x0=last_date, x1=last_date, y0=0, y1=1,
                      xref="x", yref="paper",
                      line=dict(dash="dot", color="#555", width=1.5))
        fig.update_layout(**base_layout(f"{selected} — Last 90 Days + 7-Day Forecast", height=430))
        fig.update_yaxes(tickformat=",")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-header">📋 Daily Forecast Breakdown</div>', unsafe_allow_html=True)
        t = preds.copy()
        t["Day"]    = [f"Day {i+1}" for i in range(len(t))]
        t["Date"]   = t["date"].dt.strftime("%a %d %b %Y")
        t["Price"]  = t["predicted_price"].map(lambda x: f"{x:,.2f} {currency}")
        t["Change"] = t["predicted_price"].map(lambda x: f"{(x-last_price)/last_price*100:+.2f}%")
        t["Signal"] = t["predicted_price"].map(lambda x: "🟢 Up" if x > last_price else "🔴 Down")
        st.dataframe(t[["Day","Date","Price","Change","Signal"]],
                     use_container_width=True, hide_index=True)
