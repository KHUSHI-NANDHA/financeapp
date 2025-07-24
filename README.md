# Finance AI App

A modern, Streamlit-based Finance AI application that helps you analyze stocks, track your portfolio and expenses, screen stocks/ETFs, and stay updated with financial news. Built with free APIs and designed for both beginners and advanced users.

## Features

- **Stock Advisor:**
  - Analyze stocks with PE/PB ratios, intrinsic value, balance sheet, and ownership breakdown
  - Buy/sell recommendations (moving average logic)
  - Platform-specific buy instructions
  - Add stocks to your watchlist
- **Screener:**
  - View a curated list of stocks and ETFs for India and USA
- **Portfolio Tracker:**
  - Add, view, and track your holdings
  - Real-time price updates and P&L calculation
- **Expense Tracker:**
  - Track brokerage, deposits, withdrawals, and other expenses
- **Finance News:**
  - Latest financial news (requires free NewsAPI key)
- **Watchlist:**
  - Track your favorite stocks
- **Modern UI:**
  - Tabs, charts, and responsive design

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/finance-ai-app.git
cd finance-ai-app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Add Your NewsAPI Key

Create a file at `.streamlit/secrets.toml` with:

```
NEWS_API_KEY = "your_actual_newsapi_key_here"
```

Or, if using Streamlit Cloud, add `NEWS_API_KEY` in the app's Secrets UI.

### 4. Run the App

```bash
streamlit run app.py
```

### 5. (Optional) Run in Google Colab

- Upload all files to Colab
- Install dependencies:
  ```python
  !pip install streamlit yfinance plotly
  ```
- Create the secrets file:
  ```python
  import os
  os.makedirs("/content/.streamlit", exist_ok=True)
  with open("/content/.streamlit/secrets.toml", "w") as f:
      f.write('NEWS_API_KEY = "your_actual_newsapi_key_here"\n')
  ```
- Run Streamlit in Colab (with ngrok or localtunnel)

## File Structure

```
finance-ai-app/
├── app.py
├── requirements.txt
├── README.md
└── .streamlit/
    └── secrets.toml
```

## Requirements
- Python 3.8+
- Streamlit
- yfinance
- plotly
- pandas
- requests

## Screenshots

_Add screenshots or GIFs of your app here._

## License

MIT License

---

**Made with :sparkling_heart: by Finance AI** 
