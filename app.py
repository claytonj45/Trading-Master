import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

st.set_page_config(page_title="Trading Master Hub", layout="wide")

# Custom CSS to center headers and columns
st.markdown("""
    <style>
    th {text-align: center !important;}
    td {text-align: center !important;}
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
all_tickers = list(sectors.keys()) + list(us_allocation.keys()) + list(intl_list.keys()) + ['^VIX']
@st.cache_data(ttl=3600)
def get_data():
    data = yf.download(all_tickers, period="2y", interval="1d")
    return data['Close'], data['Volume']

prices, volumes = get_data()

# --- 3. SCORING LOGIC ---
def render_table(ticker_dict):
    rows = []
    for ticker, name in ticker_dict.items():
        if ticker == '^VIX': continue
        score = 0
        ma50, ma200 = prices[ticker].rolling(50).mean().iloc[-1], prices[ticker].rolling(200).mean().iloc[-1]
        current_price = prices[ticker].iloc[-1]
        if current_price > ma50 > ma200: score += 25
        rsi = ta.rsi(prices[ticker]).iloc[-1]
        if 50 <= rsi <= 70: score += 25
        spy_perf = (prices['SPY'].iloc[-1] / prices['SPY'].iloc[-65]) - 1
        tick_perf = (prices[ticker].iloc[-1] / prices[ticker].iloc[-65]) - 1
        if tick_perf > spy_perf: score += 25
        if volumes[ticker].iloc[-1] > volumes[ticker].rolling(20).mean().iloc[-1]: score += 25
        
        rows.append({'Name': name, 'Ticker': ticker, 'Score': score, 'Price': current_price, 'RSI': rsi})
    
    df = pd.DataFrame(rows).sort_values('Score', ascending=False)
    st.table(df.style.format({'Price': '{:.2f}', 'RSI': '{:.1f}'}).hide(axis='index'))
