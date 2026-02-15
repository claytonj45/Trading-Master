import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

st.set_page_config(page_title="Trading Master Hub", layout="wide")

# Custom CSS for centering and clean tables
st.markdown("""
    <style>
    th {text-align: center !important;}
    td {text-align: center !important;}
    div[data-testid="stTable"] {display: flex; justify-content: center;}
    </style>
    """, unsafe_allow_html=True)

# --- 1. DATA LISTS ---
sectors = {'XLE': 'Energy', 'XLF': 'Financials', 'XLI': 'Industrials', 'XLK': 'Technology', 'XLY': 'Cons Disc', 'XLP': 'Cons Staples', 'XLV': 'Health Care', 'XLU': 'Utilities', 'XLB': 'Materials', 'XLRE': 'Real Estate', 'XLC': 'Comm Services'}

us_allocation = {'CGDV': 'Cap Group Div', 'DGRO': 'iShares Div Growth', 'DYNF': 'Equity Factor', 'ELM': 'Elm Navigator', 'GMOD': 'GMO Dynamic', 'MFUS': 'PIMCO Multi-Factor', 'TOPC': 'S&P 500 Capped', 'VLU': 'SPDR Value Tilt', 'XOEF': 'S&P 500 ex-100', 'XOEX': 'S&P 100 Ex-Top 20'}

intl_list = {
    'AVDV': 'Avantis Intl SCV', 'DFIV': 'Dimensional Intl Val', 'EFAS': 'iShares MSCI EAFE', 
    'EYLD': 'Cambria Emerging', 'FEMR': 'Fid EM Risk', 'FIDI': 'Fid Intl Div', 
    'FIVA': 'Fid Intl Val', 'GMOI': 'GMO Intl', 'GVAL': 'Cambria Global Val', 
    'IDEV': 'iShares Core Intl', 'IDVO': 'Intl Div ETF', 'IEMG': 'iShares Core EM', 
    'IGRO': 'iShares Intl Div', 'IQDF': 'IndexIQ Intl', 'IVLU': 'iShares Value', 
    'LVHI': 'Legg Mason Intl', 'PXF': 'Invesco FTSE RAFI', 'SCHY': 'Schwab Intl Div', 
    'VEXC': 'Vanguard Intl', 'VNQI': 'Vanguard Global RE', 'SPY': 'Benchmark'
}

# --- 2. FETCH DATA ---
all_tickers = list(set(list(sectors.keys()) + list(us_allocation.keys()) + list(intl_list.keys()) + ['^VIX', 'SPY']))

@st.cache_data(ttl=3600)
def get_data():
    try:
        data = yf.download(all_tickers, period="2y", interval="1d", group_by='column')
        if data.empty:
            return None, None
        return data['Close'], data['Volume']
    except Exception:
        return None, None

prices, volumes = get_data()

# --- 3. SCORING LOGIC ---
def render_table(ticker_dict):
    if prices is None:
        st.error("Data currently unavailable from Yahoo Finance. Try refreshing.")
        return
        
    rows = []
    for ticker, name in ticker_dict.items():
        try:
            if ticker not in prices.columns: continue
            
            # Indicators
            series = prices[ticker].dropna()
            if len(series) < 200: continue
            
            ma50 = series.rolling(50).mean().iloc[-1]
            ma200 = series.rolling(200).mean().iloc[-1]
            current_price = series.iloc[-1]
            
            score = 0
            if current_price > ma50 > ma200: score += 25
            
            rsi_series = ta.rsi(series)
            rsi = rsi_series.iloc[-1] if not rsi_series.empty else 0
            if 50 <= rsi <= 70: score += 25
            
            spy_perf = (prices['SPY'].iloc[-1] / prices['SPY'].iloc[-65]) - 1
            tick_perf = (series.iloc[-1] / series.iloc[-65]) - 1
            if tick_perf > spy_perf: score += 25
            
            vol_series = volumes[ticker].dropna()
            if vol_series.iloc[-1] > vol_series.rolling(20).mean().iloc[-1]: score += 25
            
            rows.append({'Name': name, 'Ticker': ticker, 'Score': score, 'Price': current_price, 'RSI': rsi})
        except:
            continue
    
    df = pd.DataFrame(rows).sort_values('Score', ascending=False)
    st.table(df.style.format({'Price': '{:.2f}', 'RSI': '{:.1f}'}).hide(axis='index'))

# --- 4. THE TABS ---
st.title("📊 Trading Master Control")

if prices is not None:
    t1, t2, t3, t4 = st.tabs(["Sectors", "U.S.", "International", "Study Log"])

    with t1: render_table(sectors)
    with t2: render_table(us_allocation)
    with t3: render_table(intl_list)
    with t4:
        st.header(f"Pre-Trade Checklist - {datetime.now().strftime('%Y-%m-%d')}")
        spy_price = prices['SPY'].iloc[-1]
        spy_ma200 = prices['SPY'].rolling(200).mean().iloc[-1]
        vix_price = prices['^VIX'].iloc[-1] if '^VIX' in prices.columns else 0
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("1. Market State")
            st.metric("SPY Trend (vs 200MA)", "UP" if spy_price > spy_ma200 else "DOWN")
            st.metric("Volatility (VIX)", f"{vix_price:.2f}", "High" if vix_price > 20 else "Normal/Low")
        with c2:
            st.subheader("2. Participant State")
            st.write("- **Sentiment:** Review surveys")
            st.write("- **Positioning:** Systematics/CTAs")
        st.divider()
        st.text_area("Portfolio Impact & Strategy Notes:", placeholder="Type notes here...")
else:
    st.warning("Loading data... If this takes more than 1 minute, refresh the page.")
