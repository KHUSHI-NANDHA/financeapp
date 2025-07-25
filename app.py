import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
import requests

# ========== CONFIG ==========
NEWSAPI_KEY = ""  # <-- Get your free API key from https://newsapi.org/

def get_stock_data(ticker, period="6mo"):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        return hist
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except Exception as e:
        st.error(f"Error fetching info: {e}")
        return None

def get_news(query="stock market"):
    if not NEWSAPI_KEY:
        return []
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWSAPI_KEY}&language=en&sortBy=publishedAt&pageSize=5"
    try:
        resp = requests.get(url)
        data = resp.json()
        return data.get("articles", [])
    except Exception as e:
        st.warning(f"News fetch error: {e}")
        return []

def moving_average_recommendation(hist):
    if hist is None or len(hist) < 50:
        return "Not enough data for recommendation."
    hist = hist.copy()
    hist["MA20"] = hist["Close"].rolling(window=20).mean()
    hist["MA50"] = hist["Close"].rolling(window=50).mean()
    if hist["MA20"].iloc[-1] > hist["MA50"].iloc[-1]:
        return "Buy (Short-term uptrend detected)"
    elif hist["MA20"].iloc[-1] < hist["MA50"].iloc[-1]:
        return "Sell (Short-term downtrend detected)"
    else:
        return "Hold (No clear trend)"

def get_platform_instructions(platform):
    instructions = {
        "Zerodha": "1. Log in to Zerodha Kite.\n2. Search for the stock.\n3. Click 'Buy'.\n4. Enter quantity, price, and order type.\n5. Click 'Buy' to confirm.",
        "Groww": "1. Log in to Groww.\n2. Search for the stock.\n3. Click 'Buy'.\n4. Enter details and confirm.",
        "Upstox": "1. Log in to Upstox.\n2. Search for the stock.\n3. Click 'Buy'.\n4. Enter order details and confirm.",
        "Robinhood": "1. Log in to Robinhood.\n2. Search for the stock.\n3. Click 'Buy'.\n4. Enter amount and confirm.",
        "Other": "1. Log in to your platform.\n2. Search for the stock.\n3. Follow the platform's buy process."
    }
    return instructions.get(platform, instructions["Other"])

# ========== SESSION STATE INIT ==========
def init_state():
    if "portfolio" not in st.session_state:
        st.session_state["portfolio"] = []
    if "expenses" not in st.session_state:
        st.session_state["expenses"] = []
    if "watchlist" not in st.session_state:
        st.session_state["watchlist"] = []

init_state()

# ========== SIDEBAR ==========
st.sidebar.title("Finance AI")
st.sidebar.markdown("---")

# Country and currency selection
def_country = "India"
def_currency = {"India": "INR", "USA": "USD", "UK": "GBP", "Canada": "CAD", "Australia": "AUD", "Other": "USD"}
countries = list(def_currency.keys())
country = st.sidebar.selectbox("Your Country", countries)
currency = st.sidebar.selectbox("Currency", [def_currency[country]], key="currency_select")

# Account balance input
if "account_balance" not in st.session_state:
    st.session_state["account_balance"] = 0.0
account_balance = st.sidebar.number_input(f"Account Balance ({currency})", min_value=0.0, value=st.session_state["account_balance"], step=100.0, key="account_balance_input")
st.session_state["account_balance"] = account_balance

platform = st.sidebar.selectbox("Your Trading Platform", ["Zerodha", "Groww", "Upstox", "Robinhood", "Other"])
st.sidebar.markdown(f"**How to Buy:**\n{get_platform_instructions(platform)}")

st.sidebar.markdown("---")
if st.sidebar.button("Reset Portfolio & Expenses"):
    st.session_state["portfolio"] = []
    st.session_state["expenses"] = []
    st.session_state["watchlist"] = []
    st.sidebar.success("Data reset!")

# ========== MAIN TABS ==========
tabs = st.tabs(["Stock Advisor", "Screener", "Portfolio", "Expenses", "News", "Watchlist"])

# ========== STOCK ADVISOR TAB ==========
with tabs[0]:
    st.header(":chart_with_upwards_trend: Stock Advisor")
    popular_stocks = {
        "India": ["RELIANCE.NS", "TCS.NS"],
        "USA": ["AAPL", "MSFT"],
        "UK": ["HSBA.L", "BP.L"],
        "Canada": ["RY.TO", "TD.TO"],
        "Australia": ["CBA.AX", "BHP.AX"],
        "Other": ["AAPL", "MSFT"]
    }
    ticker = st.text_input(f"Enter Stock Ticker (e.g., {', '.join(popular_stocks[country])})", popular_stocks[country][0])

    # Store last analyzed ticker in session state
    if "last_analyzed_ticker" not in st.session_state:
        st.session_state["last_analyzed_ticker"] = None
    if "last_hist" not in st.session_state:
        st.session_state["last_hist"] = None
    if "last_info" not in st.session_state:
        st.session_state["last_info"] = None
    if "last_balance_sheet" not in st.session_state:
        st.session_state["last_balance_sheet"] = None

    if st.button("Analyze Stock"):
        hist = get_stock_data(ticker)
        info = get_stock_info(ticker)
        # Try to get balance sheet
        try:
            stock = yf.Ticker(ticker)
            balance_sheet = stock.balance_sheet
        except Exception:
            balance_sheet = None
        if hist is not None and info is not None:
            st.session_state["last_analyzed_ticker"] = ticker
            st.session_state["last_hist"] = hist
            st.session_state["last_info"] = info
            st.session_state["last_balance_sheet"] = balance_sheet

    # Show analysis if available
    if st.session_state["last_analyzed_ticker"]:
        info = st.session_state["last_info"]
        hist = st.session_state["last_hist"]
        balance_sheet = st.session_state["last_balance_sheet"]
        st.subheader(f"{info.get('shortName', st.session_state['last_analyzed_ticker'])} ({st.session_state['last_analyzed_ticker']})")
        st.write(f"**Sector:** {info.get('sector', 'N/A')} | **Market Cap:** {info.get('marketCap', 'N/A')}")
        st.write(f"**Summary:** {info.get('longBusinessSummary', 'N/A')}")

        # --- PE and PB Ratio Section ---
        pe_ratio = info.get('trailingPE', 'N/A')
        pb_ratio = info.get('priceToBook', 'N/A')
        with st.container():
            st.markdown("#### :bar_chart: Valuation Ratios")
            st.metric("PE Ratio", pe_ratio)
            st.metric("PB Ratio", pb_ratio)

        # --- Intrinsic Value Section ---
        with st.container():
            st.markdown("#### :money_with_wings: Intrinsic Value")
            intrinsic_value = 'N/A'
            explanation = "Intrinsic value is an estimate of a stock's true worth. Calculating it accurately requires detailed financial projections. This app uses a simple placeholder."
            eps = info.get('trailingEps', None)
            if eps is not None and eps != 'N/A':
                try:
                    intrinsic_value = round(eps * 15, 2)
                    explanation += f"\nEstimated using: Intrinsic Value ≈ EPS × 15 (Graham's rule-of-thumb)."
                except Exception:
                    pass
            st.metric("Intrinsic Value (Estimate)", intrinsic_value)
            st.caption(explanation)

        # --- Balance Sheet Table ---
        if balance_sheet is not None and not balance_sheet.empty:
            st.markdown("**Balance Sheet (Most Recent Year):**")
            keys = ['Total Assets', 'Total Liabilities Net Minority Interest', 'Total Equity Gross Minority Interest', 'Total Current Assets', 'Total Current Liabilities']
            bs_display = {}
            for k in keys:
                if k in balance_sheet.index:
                    bs_display[k] = balance_sheet.loc[k].iloc[0]
            if bs_display:
                bs_df = pd.DataFrame(bs_display, index=["Value"])
                st.dataframe(bs_df.T, use_container_width=True)
            else:
                st.write("Balance sheet data not available.")
        else:
            st.write("Balance sheet data not available.")

        # --- Institutional & Retail Holdings ---
        inst = info.get('heldPercentInstitutions', None)
        retail = info.get('heldPercentInsiders', None)
        st.markdown("**Ownership:**")
        st.write(f"Institutional Holdings: {round(inst*100,2) if inst is not None else 'N/A'}%")
        st.write(f"Insider (Retail) Holdings: {round(retail*100,2) if retail is not None else 'N/A'}%")

        # --- Chart with full zoom ---
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name='Candlestick'))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=20).mean(), mode='lines', name='MA20'))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=50).mean(), mode='lines', name='MA50'))
        fig.update_layout(xaxis_rangeslider_visible=True, dragmode='zoom', yaxis=dict(fixedrange=False))
        st.plotly_chart(fig, use_container_width=True)

        # Recommendation
        rec = moving_average_recommendation(hist)
        st.info(f"**Recommendation:** {rec}")

        # --- Affordability check ---
        current_price = hist['Close'].iloc[-1] if not hist.empty else None
        if current_price is not None:
            if current_price > account_balance:
                st.warning(f"You do not have enough balance to buy 1 share. Current price: {current_price:.2f} {currency}, Your balance: {account_balance:.2f} {currency}")
            else:
                st.success(f"You can afford to buy at least 1 share. Current price: {current_price:.2f} {currency}, Your balance: {account_balance:.2f} {currency}")

        # Add to watchlist button (always available after analysis)
        if st.button("Add to Watchlist"):
            if st.session_state["last_analyzed_ticker"] not in st.session_state["watchlist"]:
                st.session_state["watchlist"].append(st.session_state["last_analyzed_ticker"])
                st.success(f"{st.session_state['last_analyzed_ticker']} added to watchlist!")
            else:
                st.warning(f"{st.session_state['last_analyzed_ticker']} already in watchlist.")

    # --- Popular & Affordable Stocks/ETFs Section ---
    st.markdown(f"### Top Stocks & ETFs in {country}")

    expanded_stocks = {
        "India": [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
            "BALKRISIND.NS", "POLYCAB.NS", "LTIM.NS", "CERA.NS", "TATAMOTORS.NS",
            "NIFTYBEES.NS", "BANKBEES.NS", "GOLDBEES.NS"
        ],
        "USA": [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
            "PLTR", "F", "SOFI", "NIO", "AMC",
            "SPY", "VOO", "QQQ", "IWM", "ARKK"
        ],
        "UK": [
            "HSBA.L", "BP.L", "VOD.L", "GSK.L", "BARC.L",
            "EZJ.L", "SMT.L", "ITV.L", "SBRY.L", "TSCO.L",
            "VUKE.L", "ISF.L"
        ],
        "Canada": [
            "RY.TO", "TD.TO", "BNS.TO", "ENB.TO", "SHOP.TO",
            "WEED.TO", "AC.TO", "GIL.TO", "LSPD.TO", "BB.TO",
            "XIU.TO", "ZCN.TO"
        ],
        "Australia": [
            "CBA.AX", "BHP.AX", "WBC.AX", "NAB.AX", "CSL.AX",
            "APT.AX", "FMG.AX", "TPG.AX", "Z1P.AX", "MIN.AX",
            "VAS.AX", "STW.AX"
        ],
        "Other": [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
            "PLTR", "F", "SOFI", "NIO", "AMC",
            "SPY", "VOO", "QQQ", "IWM", "ARKK"
        ]
    }

    all_prices = []
    for t in expanded_stocks[country]:
        try:
            price = yf.Ticker(t).history(period="1d")["Close"].iloc[-1]
            all_prices.append((t, price))
        except Exception:
            continue

    if account_balance > 0:
        affordable = [item for item in all_prices if item[1] <= account_balance]
        if affordable:
            st.table(pd.DataFrame(affordable, columns=["Ticker", f"Price ({currency})"]))
        else:
            all_prices_sorted = sorted(all_prices, key=lambda x: x[1])
            st.table(pd.DataFrame(all_prices_sorted[:5], columns=["Ticker", f"Price ({currency})"]))
    else:
        st.table(pd.DataFrame(all_prices[:8], columns=["Ticker", f"Price ({currency})"]))

    st.markdown("### Quick Buy Guide")
    st.markdown(get_platform_instructions(platform))

# ========== SCREENER TAB ==========
with tabs[1]:
    st.header(":mag: Stock Screener")
    screener_stocks = {
        "India": [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
            "SUZLON.NS", "YESBANK.NS", "IDEA.NS", "JPPOWER.NS", "PNB.NS", "IRFC.NS", "NHPC.NS",
            "NIFTYBEES.NS", "BANKBEES.NS", "GOLDBEES.NS"
        ],
        "USA": [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
            "PLTR", "F", "SOFI", "NIO", "AMC",
            "SPY", "VOO", "QQQ", "IWM", "ARKK"
        ]
    }
    for country, tickers in screener_stocks.items():
        st.subheader(f"{country} Stocks & ETFs")
        results = []
        for t in tickers:
            try:
                price = yf.Ticker(t).history(period="1d")["Close"].iloc[-1]
                results.append((t, price))
            except Exception:
                continue
        st.table(pd.DataFrame(results, columns=["Ticker", "Price"]))

# ========== PORTFOLIO TAB ==========
with tabs[2]:
    st.header(":moneybag: Portfolio Tracker")
    with st.form("add_portfolio"):
        p_ticker = st.text_input("Stock Ticker", "AAPL", key="p_ticker")
        p_qty = st.number_input("Quantity", min_value=1, value=1, key="p_qty")
        p_price = st.number_input("Buy Price per Share", min_value=0.0, value=100.0, key="p_price")
        submitted = st.form_submit_button("Add to Portfolio")
        if submitted:
            st.session_state["portfolio"].append({"ticker": p_ticker.upper(), "qty": p_qty, "price": p_price, "date": str(datetime.now().date())})
            st.success(f"Added {p_qty} shares of {p_ticker.upper()} at {currency} {p_price} each.")
    if st.session_state["portfolio"]:
        df = pd.DataFrame(st.session_state["portfolio"])
        df["Current Price"] = df["ticker"].apply(lambda t: yf.Ticker(t).history(period="1d")["Close"].iloc[-1] if not yf.Ticker(t).history(period="1d").empty else 0)
        df["Current Value"] = df["Current Price"] * df["qty"]
        df["Invested"] = df["price"] * df["qty"]
        df["P/L"] = df["Current Value"] - df["Invested"]
        st.dataframe(df[["ticker", "qty", "price", "Current Price", "Current Value", "Invested", "P/L", "date"]], use_container_width=True)
        st.plotly_chart(go.Figure([go.Pie(labels=df["ticker"], values=df["Current Value"], hole=.4)]), use_container_width=True)
        st.metric("Total Invested", f"{currency} {df['Invested'].sum():,.2f}")
        st.metric("Current Value", f"{currency} {df['Current Value'].sum():,.2f}")
        st.metric("Total P/L", f"{currency} {df['P/L'].sum():,.2f}")
    else:
        st.info("No holdings yet. Add stocks above!")

# ========== EXPENSES TAB ==========
with tabs[3]:
    st.header(":credit_card: Expense Tracker")
    with st.form("add_expense"):
        e_name = st.text_input("Expense Name", "Brokerage Fee", key="e_name")
        e_amt = st.number_input("Amount", min_value=0.0, value=10.0, key="e_amt")
        e_cat = st.selectbox("Category", ["Brokerage", "Deposit", "Withdrawal", "Other"], key="e_cat")
        e_date = st.date_input("Date", datetime.now(), key="e_date")
        e_submit = st.form_submit_button("Add Expense")
        if e_submit:
            st.session_state["expenses"].append({"name": e_name, "amount": e_amt, "category": e_cat, "date": str(e_date)})
            st.success(f"Added expense: {e_name} - {currency} {e_amt}")
    if st.session_state["expenses"]:
        edf = pd.DataFrame(st.session_state["expenses"])
        st.dataframe(edf, use_container_width=True)
        fig = go.Figure()
        for cat in edf["category"].unique():
            cat_df = edf[edf["category"] == cat]
            fig.add_trace(go.Bar(x=cat_df["date"], y=cat_df["amount"], name=cat))
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Total Expenses", f"{currency} {edf['amount'].sum():,.2f}")
    else:
        st.info("No expenses yet. Add above!")

# ========== NEWS TAB ==========
with tabs[4]:
    st.header(":newspaper: Finance News")
    if not NEWSAPI_KEY:
        st.warning("Add your NewsAPI key at the top of the file to see news.")
    else:
        news = get_news()
        for article in news:
            st.subheader(article["title"])
            st.write(article["description"])
            st.write(f"[Read more]({article['url']})")
            st.markdown("---")

# ========== WATCHLIST TAB ==========
with tabs[5]:
    st.header(":eyes: Watchlist")
    if st.session_state["watchlist"]:
        wdf = pd.DataFrame({"Ticker": st.session_state["watchlist"]})
        wdf["Current Price"] = wdf["Ticker"].apply(lambda t: yf.Ticker(t).history(period="1d")["Close"].iloc[-1] if not yf.Ticker(t).history(period="1d").empty else 0)
        st.dataframe(wdf, use_container_width=True)
    else:
        st.info("No stocks in watchlist. Add from Stock Advisor tab!")

# ========== FOOTER ==========
st.markdown("---")
st.markdown("Made by :sparkling_heart: Khushi Nandha :sparkling_heart: by Finance AI | Powered by Streamlit, yfinance, NewsAPI, Plotly") 
