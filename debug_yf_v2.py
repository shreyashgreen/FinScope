import yfinance as yf
import requests
import pandas as pd

ticker = "AAPL"
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
})

print(f"Testing {ticker} with session...")
try:
    stock = yf.Ticker(ticker, session=session)
    print("Fetching info...")
    info = stock.info
    print(f"Info retrieved: {bool(info)}")
    if info:
        print(f"Name: {info.get('longName')}")
    else:
        print("Info is empty.")
    
    print("Fetching history...")
    hist = stock.history(period="1mo")
    print(f"History shape: {hist.shape}")
    
except Exception as e:
    print(f"Caught Exception: {type(e).__name__}: {e}")

# Try without session just to compare
print("\nTesting without session...")
try:
    stock2 = yf.Ticker(ticker)
    info2 = stock2.info
    print(f"Info retrieved: {bool(info2)}")
except Exception as e:
    print(f"Caught Exception: {type(e).__name__}: {e}")
