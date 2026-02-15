import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="Trading Master Hub", layout="wide")

# --- 1. DATA LISTS ---
sectors = {'XLE': 'Energy', 'XLF': 'Financials', 'XLI': 'Industrials', 'XLK': 'Technology', 'XLY': 'Cons Disc', 'XLP': 'Cons Staples', 'XLV': 'Health Care', 'XLU': 'Utilities', 'XLB': 'Materials', 'XLRE': 'Real Estate', 'XLC': 'Comm Services'}

dividend_factor = {'CGDV': 'Cap Group Div', 'DGRO': 'iShares Div Growth', 'DYNF': 'Equity Factor', 'ELM': 'Elm Navigator', 'GMOD': 'GMO Dynamic', 'MFUS': 'PIMCO Multi-Factor', 'TOPC': 'S&P 500 Capped', 'VLU': 'SPDR Value Tilt', 'XOEF': 'S&P 500 ex-100', 'XOEX': 'S&P 100 Ex-Top 20'}

intl_value = {'FTIHX': 'Fid Intl Index', 'IDVO': 'Intl Div ETF', 'VEXC': 'Vanguard Intl', 'IGRO': 'iShares Intl Div', 'AVDV': 'Avantis Intl SCV', 'LVHI': 'Legg Mason Intl', 'EELV': 'Invesco EM Vol'}

# --- 2. FETCH DATA ---
all_tickers = list(sectors.keys()) + list(dividend_factor.keys()) + list(intl_value.keys()) + ['SPY']
@st.cache_data(ttl=3600)
def get_data():
    data = yf.download(all_tickers, period="2y", interval="1d")
    return data['Close'], data['Volume']

prices, volumes = get_data()

# --- 3. SCORING LOGIC ---
def render_table(ticker_dict):
    rows = []
    for ticker, name in ticker_dict.items():
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
        rows.append({'Ticker': ticker, 'Name': name, 'Score': score, 'Price': current_price, 'RSI': rsi})
    df = pd.DataFrame(rows).sort_values('Score', ascending=False)
    st.table(df.style.format({'Price': '{:.2f}', 'RSI': '{:.1f}'}))

# --- 4. THE TABS ---
st.title("📊 Trading Master Control")
t1, t2, t3, t4 = st.tabs(["Sectors", "Master Allocation", "International", "Study Log"])

with t1:
    st.header("Sector Relative Strength")
    render_table(sectors)

with t2:
    st.header("Dividend & Factor Core")
    render_table(dividend_factor)

with t3:
    st.header("International Value")
    render_table(intl_value)

with t4:
    st.header("Monday Study Master Dashboard")
    st.info("Baseline: 36-fund Version 4.3 | Target: Lowering Avg Price")
    st.write("- Check for 'Oversold' RSI in other tabs.")
    st.write("- Review Market Fragility Log Q1 2026.")
