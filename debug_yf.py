import yfinance as yf
ticker = "AAPL"
print(f"Ticker: {ticker}")
try:
    stock = yf.Ticker(ticker)
    info = stock.info
    print(f"Info keys: {list(info.keys())[:5]}")
    print(f"Name: {info.get('longName')}")
    hist = stock.history(period='1d')
    print(f"History: {hist.shape}")
    if not hist.empty:
        print(f"Price: {hist['Close'].iloc[-1]}")
except Exception as e:
    print(f"Error: {e}")
