#!/usr/bin/env python3
"""
Minimal test version of FinScope to debug issues
"""

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# Simple test
st.set_page_config(page_title="FinScope Debug", layout="wide")

st.title("FinScope Debug Test")

# Test basic yfinance functionality
try:
    ticker = st.text_input("Enter ticker symbol", "AAPL")
    if ticker:
        with st.spinner("Fetching data..."):
            stock = yf.Ticker(ticker)
            info = stock.info

            if info:
                st.success(f"Successfully fetched data for {ticker}")
                st.write(f"Company: {info.get('longName', 'N/A')}")
                st.write(f"Price: ${info.get('currentPrice', 'N/A')}")
                st.write(f"Market Cap: ${info.get('marketCap', 'N/A')}")
            else:
                st.error("Could not fetch stock info")
except Exception as e:
    st.error(f"Error: {str(e)}")

# Test news functionality
try:
    if ticker:
        news = stock.news
        if news:
            st.subheader("Latest News")
            for item in news[:3]:
                st.write(f"- {item.get('title', 'No title')}")
        else:
            st.write("No news available")
except Exception as e:
    st.error(f"News error: {str(e)}")