import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from fpdf import FPDF
import io
import base64
import json
import tempfile
import os
import requests
from textblob import TextBlob
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─────────────────────────────────────────────
# PAGE CONFIG & THEME
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FinScope | Global Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* Global */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.08);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: rgba(255,255,255,0.6);
        font-size: 0.9rem;
        margin: 0.25rem 0 0 0;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.25);
    }
    .metric-label {
        color: rgba(255,255,255,0.5);
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.4rem;
    }
    .metric-value {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .metric-delta-pos { color: #00e676; font-size: 0.82rem; font-weight: 600; }
    .metric-delta-neg { color: #ff5252; font-size: 0.82rem; font-weight: 600; }

    /* Section headers */
    .section-header {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(255,255,255,0.06);
        letter-spacing: -0.3px;
    }

    /* Info box */
    .info-box {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.5rem 0;
    }
    .info-box .label {
        color: rgba(255,255,255,0.45);
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .info-box .value {
        color: #ffffff;
        font-size: 0.95rem;
        font-weight: 500;
        margin-top: 0.15rem;
    }

    /* Recommendation badge */
    .rec-badge {
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 50px;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .rec-buy { background: rgba(0,230,118,0.15); color: #00e676; border: 1px solid rgba(0,230,118,0.3); }
    .rec-sell { background: rgba(255,82,82,0.15); color: #ff5252; border: 1px solid rgba(255,82,82,0.3); }
    .rec-hold { background: rgba(255,193,7,0.15); color: #ffc107; border: 1px solid rgba(255,193,7,0.3); }
    .rec-neutral { background: rgba(144,164,174,0.15); color: #90a4ae; border: 1px solid rgba(144,164,174,0.3); }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117, #161b22);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stTextInput label {
        color: rgba(255,255,255,0.7) !important;
        font-weight: 600;
    }

    /* Global index card */
    .index-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 0.7rem 1rem;
        margin-bottom: 0.5rem;
    }
    .index-name { color: rgba(255,255,255,0.7); font-size: 0.78rem; font-weight: 600; }
    .index-price { color: #ffffff; font-size: 1rem; font-weight: 700; }
    .index-change-pos { color: #00e676; font-size: 0.78rem; font-weight: 600; }
    .index-change-neg { color: #ff5252; font-size: 0.78rem; font-weight: 600; }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(102,126,234,0.4) !important;
    }

    /* ────────────────────────────────────────────────────────────── */
    /* MOBILE RESPONSIVE DESIGN                                       */
    /* ────────────────────────────────────────────────────────────── */
    
    @media (max-width: 768px) {
        /* Reduce padding on small screens */
        .stApp {
            padding: 0;
        }
        
        .main-header {
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 12px;
        }
        
        .main-header h1 {
            font-size: 1.5rem;
        }
        
        .main-header p {
            font-size: 0.8rem;
        }
        
        /* Stack columns on mobile */
        .stColumn {
            margin-bottom: 0.5rem;
        }
        
        /* Optimize metric cards for mobile */
        .metric-card {
            padding: 1rem;
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            font-size: 0.65rem;
        }
        
        .metric-value {
            font-size: 1.2rem;
        }
        
        /* Section headers */
        .section-header {
            font-size: 1rem;
            margin: 1rem 0 0.6rem 0;
        }
        
        /* Tab styling for mobile */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            padding: 2px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px;
            font-size: 0.75rem;
            margin-right: 2px;
        }
        
        /* Adjust selectbox */
        .stSelectbox, .stMultiSelect {
            margin-bottom: 0.5rem;
        }
        
        /* Make buttons full width on mobile */
        button {
            min-height: 44px !important; /* Touch-friendly size */
        }
        
        /* Info box adjustments */
        .info-box {
            padding: 0.8rem;
            margin: 0.3rem 0;
        }
        
        /* Index cards */
        .index-card {
            padding: 0.6rem 0.8rem;
            margin-bottom: 0.4rem;
        }
        
        /* Hide sidebar on very small screens or make it overlay */
        section[data-testid="stSidebar"] {
            width: 80% !important;
        }
        
        /* Improve dataframe visibility on mobile */
        [data-testid="stDataFrame"] {
            font-size: 0.85rem;
        }
    }
    
    @media (max-width: 480px) {
        /* Extra small phone optimization */
        .main-header {
            padding: 0.8rem;
            margin-bottom: 0.8rem;
        }
        
        .main-header h1 {
            font-size: 1.2rem;
        }
        
        .section-header {
            font-size: 0.95rem;
        }
        
        .metric-card {
            padding: 0.8rem;
        }
        
        .metric-value {
            font-size: 1rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 6px 10px;
            font-size: 0.7rem;
        }
        
        /* Single column layout hint */
        .stColumn {
            width: 100% !important;
        }
    }
    
    /* Touch-friendly elements */
    @media (hover: none) and (pointer: coarse) {
        /* Mobile device detected */
        button, a, .stButton > button {
            min-height: 48px !important;
            font-size: 1rem !important;
        }
        
        input, select, textarea {
            min-height: 44px !important;
            font-size: 16px !important; /* Prevents zoom on input focus */
        }
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
GLOBAL_INDICES = {
    # Indices
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Dow Jones": "^DJI",
    "FTSE 100": "^FTSE",
    "DAX": "^GDAXI",
    "Nikkei 225": "^N225",
    "Hang Seng": "^HSI",
    "SENSEX": "^BSESN",
    "NIFTY 50": "^NSEI",
    "ASX 200": "^AXJO",
    # Currencies
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    # Commodities
    "Gold": "GC=F",
    "Brent Oil": "BZ=F",
    "Silver": "SI=F",
    # Crypto
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
}

POPULAR_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "JPM", "V", "JNJ", "WMT", "PG", "MA", "UNH", "HD", "DIS", "BAC",
    "XOM", "NFLX", "ADBE", "CRM", "AMD", "INTC", "CSCO", "PFE", "KO",
    "PEP", "ABT", "MRK", "COST", "NKE", "ORCL", "LLY", "TMO", "AVGO",
    "TXN", "QCOM", "PYPL", "INTU", "AMAT", "ISRG", "BKNG", "GILD",
    "MDLZ", "ADP", "REGN", "VRTX", "LRCX", "MU",
]

PERIOD_MAP = {
    "1 Day": "1d", "5 Days": "5d", "1 Month": "1mo", "3 Months": "3mo",
    "6 Months": "6mo", "1 Year": "1y", "2 Years": "2y", "5 Years": "5y",
    "10 Years": "10y", "Max": "max",
}

INTERVAL_MAP = {
    "1 Day": "5m", "5 Days": "15m", "1 Month": "1d", "3 Months": "1d",
    "6 Months": "1d", "1 Year": "1wk", "2 Years": "1wk", "5 Years": "1mo",
    "10 Years": "1mo", "Max": "1mo",
}

# ─────────────────────────────────────────────
# DATA FETCHING HELPERS
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def search_ticker(query: str):
    """Search for tickers based on a company name query."""
    try:
        search = yf.Search(query, max_results=8)
        results = []
        for res in search.quotes:
            if res.get('quoteType') in ('EQUITY', 'ETF', 'MUTUALFUND', 'INDEX', 'CRYPTOCURRENCY'):
                name = res.get('shortname') or res.get('longname') or res.get('symbol')
                results.append({
                    "symbol": res['symbol'],
                    "name": name,
                    "type": res.get('quoteType'),
                    "exchange": res.get('exchDisp', 'N/A')
                })
        return results
    except Exception:
        return []

# Domain/Industry mapping for better peer classification
INDUSTRY_DOMAIN_MAP = {
    # Technology
    "Consumer Electronics": {"domain": "Technology", "peers": ["MSFT", "GOOGL", "NVDA", "AAPL"]},
    "Software—Infrastructure": {"domain": "Technology", "peers": ["AMZN", "GOOGL", "ORCL", "MSFT"]},
    "Semiconductors": {"domain": "Technology", "peers": ["NVDA", "AMD", "INTC", "TSM"]},
    "Internet Content & Information": {"domain": "Technology", "peers": ["META", "GOOGL", "NFLX", "SNAP"]},
    "Software—Application": {"domain": "Technology", "peers": ["CRM", "ADBE", "INTU", "MSFT"]},
    
    # Finance
    "Banks—Diversified": {"domain": "Finance", "peers": ["JPM", "BAC", "WFC", "HSBC"]},
    "Insurance": {"domain": "Finance", "peers": ["BRK-B", "AIG", "PRU", "MET"]},
    "Financial Data & Services": {"domain": "Finance", "peers": ["V", "MA", "PYPL", "ADP"]},
    
    # Manufacturing & Industrial
    "Auto Manufacturers": {"domain": "Manufacturing", "peers": ["TM", "TSLA", "VWAGY", "BMW"]},
    "Electric Vehicles": {"domain": "Manufacturing", "peers": ["TSLA", "NIO", "XPEV", "TM"]},
    "Appliance & Machinery": {"domain": "Manufacturing", "peers": ["CAT", "CNH", "DE", "FAST"]},
    
    # Consumer
    "Retailers": {"domain": "Consumer", "peers": ["WMT", "AMZN", "COST", "TGT"]},
    "Specialty Retail": {"domain": "Consumer", "peers": ["NKE", "LULU", "ULTA", "HD"]},
    "Apparel Manufacturing": {"domain": "Consumer", "peers": ["NKE", "VFC", "PVH", "CAL"]},
    
    # Energy & Materials
    "Energy": {"domain": "Energy", "peers": ["XOM", "CVX", "COP", "SHELL"]},
    "Chemicals": {"domain": "Materials", "peers": ["LYB", "DOW", "EMN", "APD"]},
    "Metals & Mining": {"domain": "Materials", "peers": ["VALE", "RIO", "GLEN", "SCCO"]},
    
    # Healthcare
    "Pharmaceuticals": {"domain": "Healthcare", "peers": ["PFE", "JNJ", "ABBV", "MRK"]},
    "Medical Devices": {"domain": "Healthcare", "peers": ["JNJ", "ISRG", "TMO", "MDT"]},
    "Biotechnology": {"domain": "Healthcare", "peers": ["AMGN", "BIIB", "GILD", "VRTX"]},
    
    # Consumer Goods
    "Beverages—Non-Alcoholic": {"domain": "Consumer Goods", "peers": ["KO", "PEP", "MNST", "KDP"]},
    "Food Distribution": {"domain": "Consumer Goods", "peers": ["SYY", "GPS", "CORE", "UNFI"]},
    "Household & Personal Care": {"domain": "Consumer Goods", "peers": ["PG", "CL", "EL", "UL"]},
    
    # Entertainment & Media
    "Entertainment": {"domain": "Media & Entertainment", "peers": ["DIS", "NFLX", "WBD", "PARA"]},
    "Broadcasting": {"domain": "Media & Entertainment", "peers": ["IMAX", "CMCSA", "CHTR", "FOX"]},
}

def get_industry_peers(industry: str, sector: str):
    """Get a list of peer tickers for a given industry/sector with domain classification."""
    if industry in INDUSTRY_DOMAIN_MAP:
        return INDUSTRY_DOMAIN_MAP[industry]["peers"]
    
    # Fallback to search-based discovery for niche industries
    try:
        search = yf.Search(industry, max_results=5)
        peers = [q['symbol'] for q in search.quotes if q.get('quoteType') == 'EQUITY'][:3]
        return peers if peers else ["AAPL", "MSFT", "GOOGL"]
    except Exception:
        return ["AAPL", "MSFT", "GOOGL"]


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_intelligent_peers(ticker: str, industry: str, sector: str, market_cap: float = None, country: str = None):
    """Intelligently find global peer companies based on multiple criteria and domain classification."""
    peers_with_domain = []

    # 1. Get peers from industry domain map
    domain_info = None
    for ind, info in INDUSTRY_DOMAIN_MAP.items():
        if ind.lower() == industry.lower():
            domain_info = info
            break
    
    if domain_info:
        base_peers = domain_info["peers"]
        domain = domain_info["domain"]
        for peer in base_peers:
            if peer != ticker:
                peers_with_domain.append((peer, domain, 1.0))
    else:
        domain = sector or "Miscellaneous"
        try:
            search = yf.Search(industry, max_results=5)
            for q in search.quotes:
                if q.get('quoteType') == 'EQUITY' and q['symbol'] != ticker:
                    peers_with_domain.append((q['symbol'], domain, 0.8))
        except Exception:
            pass

    # 2. Find additional peers by market cap similarity and geography
    try:
        company_info = yf.Ticker(ticker).info
        company_cap = company_info.get('marketCap', 0)
        company_country = company_info.get('country', 'US')

        search_terms = [industry, sector]
        for term in search_terms[:2]:
            try:
                search_results = yf.Search(term, max_results=8)
                for result in search_results.quotes:
                    symbol = result.get('symbol')
                    if (result.get('quoteType') == 'EQUITY' and
                        symbol != ticker and
                        symbol not in [p[0] for p in peers_with_domain]):
                        
                        try:
                            peer_info = yf.Ticker(symbol).info
                            peer_cap = peer_info.get('marketCap', 0)
                            peer_country = peer_info.get('country', 'US')
                            
                            if company_cap > 0 and peer_cap > 0 and 0.1 <= (peer_cap / company_cap) <= 10:
                                peer_domain = peer_info.get('sector', domain) or domain
                                similarity_score = 1 / max(abs(1 - (peer_cap / company_cap)), 0.1)
                                if peer_country == company_country:
                                    similarity_score *= 1.3
                                peers_with_domain.append((symbol, peer_domain, similarity_score))
                        except Exception:
                            continue
            except Exception:
                continue

    except Exception:
        pass

    # 3. Remove duplicates, sort by score, group by domain
    seen = set()
    unique_peers = []
    for peer, domain, score in peers_with_domain:
        if peer not in seen:
            unique_peers.append((peer, domain, score))
            seen.add(peer)
    
    # Sort by domain first (for visualization), then by score
    unique_peers.sort(key=lambda x: (-x[2], x[1]))
    
    # Return just the symbols (up to 6 peers)
    return [p[0] for p in unique_peers[:6]]
@st.cache_data(ttl=3600)
def fetch_peer_data(tickers: list):
    """Fetch peer comparison data from yfinance for multiple tickers, sorted by domain."""
    peer_data = []
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            peer_data.append({
                'Ticker': ticker,
                'Name': info.get('longName', info.get('shortName', ticker)),
                'Currency': info.get('currency', 'USD'),
                'Price': info.get('currentPrice', 0),
                'Market Cap': info.get('marketCap', 0),
                'Revenue': info.get('totalRevenue', 0),
                'Div Yield': info.get('dividendYield', 0),
                'P/E Ratio': info.get('trailingPE', 0),
                'Domain': info.get('sector', 'Miscellaneous'),
                'Industry': info.get('industry', 'N/A'),
            })
        except Exception:
            # Add placeholder for failed tickers
            peer_data.append({
                'Ticker': ticker,
                'Name': ticker,
                'Currency': 'USD',
                'Price': 0,
                'Market Cap': 0,
                'Revenue': 0,
                'Div Yield': 0,
                'P/E Ratio': 0,
                'Domain': 'N/A',
                'Industry': 'N/A',
            })
    
    df = pd.DataFrame(peer_data)
    # Sort by Domain first, then by Market Cap descending
    df = df.sort_values(['Domain', 'Market Cap'], ascending=[True, False]).reset_index(drop=True)
    return df

def fetch_stock_data(ticker: str):
    """Fetch comprehensive stock data from yfinance."""
    stock = yf.Ticker(ticker)
    info = {}
    try:
        info = stock.info
        if not info or 'longName' not in info:
            # Fallback for missing info
            hist = stock.history(period="1d")
            if not hist.empty:
                info['currentPrice'] = hist['Close'].iloc[-1]
                info['longName'] = ticker
    except Exception:
        pass
    return info


@st.cache_data(ttl=120)
def fetch_history(ticker: str, period: str, interval: str):
    """Fetch historical price data."""
    stock = yf.Ticker(ticker)
    return stock.history(period=period, interval=interval)


@st.cache_data(ttl=600)
def fetch_index_data(symbol: str):
    """Fetch current index price."""
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period="2d")
        if len(hist) >= 2:
            current = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-2]
            change = current - prev
            pct = (change / prev) * 100
            return current, change, pct
        elif len(hist) == 1:
            return hist["Close"].iloc[-1], 0, 0
    except Exception:
        pass
    return None, None, None


@st.cache_data(ttl=300)
def fetch_recommendations(ticker: str):
    """Fetch analyst recommendations."""
    try:
        stock = yf.Ticker(ticker)
        recs = stock.recommendations
        if recs is not None and not recs.empty:
            return recs
    except Exception:
        pass
    return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_actions(ticker: str):
    """Fetch stock actions (dividends, splits)."""
    try:
        stock = yf.Ticker(ticker)
        return stock.actions
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_financials(ticker: str):
    """Fetch financial statements."""
    try:
        stock = yf.Ticker(ticker)
        income = stock.income_stmt
        balance = stock.balance_sheet
        cashflow = stock.cashflow
        return income, balance, cashflow
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_news(ticker: str):
    """Fetch latest stock news."""
    try:
        stock = yf.Ticker(ticker)
        return stock.news
    except Exception:
        return []


@st.cache_data(ttl=600)  # Cache for 10 minutes
def fetch_enhanced_news(ticker: str, company_name: str = None):
    """Fetch comprehensive news exclusively from yfinance with sentiment analysis and categorization."""
    all_news = []

    # Fetch news from Yahoo Finance exclusively
    try:
        stock = yf.Ticker(ticker)
        yf_news = stock.news
        if yf_news:
            for item in yf_news:
                # Extract and normalize news data from yfinance
                title = item.get('title', '')
                summary = item.get('summary', '')
                
                if not title:  # Skip items without titles
                    continue
                
                news_item = {
                    'title': title,
                    'summary': summary,
                    'link': item.get('link', ''),
                    'providerPublishTime': item.get('providerPublishTime', int(datetime.now().timestamp())),
                    'publisher': item.get('publisher', 'Yahoo Finance'),
                    'source': 'Yahoo Finance',
                    'thumbnail': item.get('thumbnail'),
                    'sentiment': analyze_sentiment(title + ' ' + summary),
                    'category': categorize_news(title, summary),
                }
                all_news.append(news_item)
    except Exception:
        pass

    # Sort by publish time and remove duplicates
    all_news = sorted(all_news, key=lambda x: x.get('providerPublishTime', 0), reverse=True)
    seen_titles = set()
    unique_news = []
    for item in all_news:
        title = item.get('title', '').lower().strip()
        if title not in seen_titles and len(title) > 10:
            seen_titles.add(title)
            unique_news.append(item)

    return unique_news[:20]  # Return top 20 unique news items


def analyze_sentiment(text: str):
    """Analyze sentiment of news text."""
    try:
        if not text or len(text.strip()) < 10:
            return 'neutral'

        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    except Exception:
        return 'neutral'


def categorize_news(title: str, summary: str = ""):
    """Categorize news into topics."""
    text = (title + " " + summary).lower()

    categories = {
        'earnings': ['earnings', 'revenue', 'profit', 'loss', 'quarter', 'annual', 'financial results'],
        'mergers': ['merger', 'acquisition', 'buyout', 'takeover', 'deal'],
        'regulatory': ['sec', 'fda', 'regulation', 'compliance', 'lawsuit', 'legal'],
        'product': ['product', 'launch', 'release', 'update', 'technology', 'innovation'],
        'market': ['market', 'trading', 'volatility', 'bull', 'bear', 'crash', 'rally'],
        'executive': ['ceo', 'executive', 'board', 'management', 'leadership'],
        'economic': ['economy', 'fed', 'interest rate', 'inflation', 'recession']
    }

    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category.title()

    return 'General'


# ─────────────────────────────────────────────
# PDF REPORT GENERATOR
# ─────────────────────────────────────────────
class EquityResearchPDF(FPDF):
    """Custom PDF class for equity research reports."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_fill_color(15, 12, 41)
        self.rect(0, 0, 210, 35, 'F')
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(255, 255, 255)
        self.set_y(8)
        self.cell(0, 10, "FinScope Equity Research Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(180, 180, 200)
        self.cell(0, 6, f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"FinScope Research  |  Page {self.page_no()}/{{nb}}  |  For informational purposes only", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(48, 43, 99)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(102, 126, 234)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(80, 80, 100)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def key_value(self, key, value):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(80, 80, 100)
        self.cell(65, 6, str(key), new_x="RIGHT")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.cell(0, 6, str(value), new_x="LMARGIN", new_y="NEXT")

    def add_table(self, headers, data, col_widths=None):
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)
        # Header
        self.set_fill_color(48, 43, 99)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 9)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 8, str(h), border=1, fill=True, align="C")
        self.ln()
        # Data
        self.set_font("Helvetica", "", 9)
        self.set_text_color(60, 60, 60)
        fill = False
        for row in data:
            if fill:
                self.set_fill_color(240, 240, 250)
            else:
                self.set_fill_color(255, 255, 255)
            for i, val in enumerate(row):
                self.cell(col_widths[i], 7, str(val), border=1, fill=True, align="C")
            self.ln()
            fill = not fill
        self.ln(3)


def generate_research_pdf(ticker: str, info: dict, hist: pd.DataFrame,
                          recs: pd.DataFrame, actions: pd.DataFrame,
                          income: pd.DataFrame, balance: pd.DataFrame,
                          cashflow: pd.DataFrame):
    """Generate a comprehensive equity research PDF report."""
    pdf = EquityResearchPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    name = info.get("longName", ticker)
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    country = info.get("country", "N/A")
    exchange = info.get("exchange", "N/A")
    currency = info.get("currency", "USD")

    # ── Cover Info
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(15, 12, 41)
    pdf.cell(0, 12, f"{name} ({ticker})", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 120)
    pdf.cell(0, 7, f"{sector}  |  {industry}  |  {exchange}  |  {country}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # ── Company Overview
    pdf.section_title("1. Company Overview")
    summary = info.get("longBusinessSummary", "No business summary available.")
    pdf.body_text(summary)

    # ── Key Metrics
    pdf.section_title("2. Key Financial Metrics")

    def fmt(val, prefix="", suffix="", div=1):
        if val is None or val == "N/A":
            return "N/A"
        try:
            v = float(val) / div
            if div >= 1e9:
                return f"{prefix}{v:.2f}B{suffix}"
            elif div >= 1e6:
                return f"{prefix}{v:.2f}M{suffix}"
            return f"{prefix}{v:,.2f}{suffix}"
        except (ValueError, TypeError):
            return str(val)

    metrics = [
        ("Market Cap", fmt(info.get("marketCap"), prefix=f"{currency} ", div=1e9)),
        ("Enterprise Value", fmt(info.get("enterpriseValue"), prefix=f"{currency} ", div=1e9)),
        ("Current Price", fmt(info.get("currentPrice"), prefix=f"{currency} ")),
        ("52-Week High", fmt(info.get("fiftyTwoWeekHigh"), prefix=f"{currency} ")),
        ("52-Week Low", fmt(info.get("fiftyTwoWeekLow"), prefix=f"{currency} ")),
        ("P/E Ratio (Trailing)", fmt(info.get("trailingPE"))),
        ("P/E Ratio (Forward)", fmt(info.get("forwardPE"))),
        ("PEG Ratio", fmt(info.get("pegRatio"))),
        ("Price to Book", fmt(info.get("priceToBook"))),
        ("EPS (Trailing)", fmt(info.get("trailingEps"), prefix=f"{currency} ")),
        ("EPS (Forward)", fmt(info.get("forwardEps"), prefix=f"{currency} ")),
        ("Dividend Yield", fmt(info.get("dividendYield", 0) * 100 if info.get("dividendYield") else None, suffix="%")),
        ("Beta", fmt(info.get("beta"))),
        ("Revenue", fmt(info.get("totalRevenue"), prefix=f"{currency} ", div=1e9)),
        ("Gross Margins", fmt(info.get("grossMargins", 0) * 100 if info.get("grossMargins") else None, suffix="%")),
        ("Operating Margins", fmt(info.get("operatingMargins", 0) * 100 if info.get("operatingMargins") else None, suffix="%")),
        ("Profit Margins", fmt(info.get("profitMargins", 0) * 100 if info.get("profitMargins") else None, suffix="%")),
        ("ROE", fmt(info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else None, suffix="%")),
        ("Debt to Equity", fmt(info.get("debtToEquity"))),
        ("Free Cash Flow", fmt(info.get("freeCashflow"), prefix=f"{currency} ", div=1e9)),
    ]

    for key, val in metrics:
        pdf.key_value(key, val)
    pdf.ln(4)

    # ── Price Performance
    pdf.section_title("3. Historical Price Performance")
    if not hist.empty:
        pdf.sub_title("Recent Price Summary")
        recent = hist.tail(20)
        headers = ["Date", "Open", "High", "Low", "Close", "Volume"]
        data = []
        for idx, row in recent.iterrows():
            date_str = idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx)[:10]
            data.append([
                date_str,
                f"{row.get('Open', 0):.2f}",
                f"{row.get('High', 0):.2f}",
                f"{row.get('Low', 0):.2f}",
                f"{row.get('Close', 0):.2f}",
                f"{int(row.get('Volume', 0)):,}",
            ])
        pdf.add_table(headers, data, col_widths=[30, 28, 28, 28, 28, 48])

        # Performance stats
        if len(hist) > 1:
            pdf.sub_title("Performance Statistics")
            close = hist["Close"]
            returns = close.pct_change().dropna()
            pdf.key_value("Period Return", f"{((close.iloc[-1] / close.iloc[0]) - 1) * 100:.2f}%")
            pdf.key_value("Average Daily Return", f"{returns.mean() * 100:.4f}%")
            pdf.key_value("Volatility (Std Dev)", f"{returns.std() * 100:.4f}%")
            pdf.key_value("Max Drawdown", f"{((close / close.cummax()) - 1).min() * 100:.2f}%")
            pdf.key_value("Highest Close", f"{currency} {close.max():.2f}")
            pdf.key_value("Lowest Close", f"{currency} {close.min():.2f}")
            pdf.ln(3)

    # ── Analyst Recommendations
    pdf.section_title("4. Analyst Recommendations")
    target_high = info.get("targetHighPrice")
    target_low = info.get("targetLowPrice")
    target_mean = info.get("targetMeanPrice")
    target_median = info.get("targetMedianPrice")
    rec = info.get("recommendationKey", "N/A")
    num_analysts = info.get("numberOfAnalystOpinions", "N/A")

    pdf.key_value("Consensus Recommendation", rec.upper() if rec != "N/A" else "N/A")
    pdf.key_value("Number of Analysts", str(num_analysts))
    pdf.key_value("Price Target (Mean)", fmt(target_mean, prefix=f"{currency} "))
    pdf.key_value("Price Target (Median)", fmt(target_median, prefix=f"{currency} "))
    pdf.key_value("Price Target (High)", fmt(target_high, prefix=f"{currency} "))
    pdf.key_value("Price Target (Low)", fmt(target_low, prefix=f"{currency} "))
    pdf.ln(2)

    if not recs.empty:
        pdf.sub_title("Recent Analyst Actions")
        recent_recs = recs.tail(15)
        headers_r = ["Date", "Firm", "To Grade", "From Grade", "Action"]

        data_r = []
        for idx, row in recent_recs.iterrows():
            date_str = idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx)[:10]
            firm = str(row.get("Firm", "N/A"))[:25]
            to_grade = str(row.get("To Grade", row.get("toGrade", "N/A")))
            from_grade = str(row.get("From Grade", row.get("fromGrade", "-")))
            action = str(row.get("Action", row.get("action", "N/A")))
            data_r.append([date_str, firm, to_grade, from_grade, action])

        pdf.add_table(headers_r, data_r, col_widths=[28, 55, 38, 38, 31])

    # ── Stock Actions
    pdf.section_title("5. Corporate Actions (Dividends & Splits)")
    if not actions.empty:
        recent_actions = actions.tail(20)
        headers_a = ["Date"]
        if "Dividends" in recent_actions.columns:
            headers_a.append("Dividend")
        if "Stock Splits" in recent_actions.columns:
            headers_a.append("Split Ratio")

        data_a = []
        for idx, row in recent_actions.iterrows():
            date_str = idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx)[:10]
            r = [date_str]
            if "Dividends" in recent_actions.columns:
                d = row.get("Dividends", 0)
                r.append(f"{currency} {d:.4f}" if d > 0 else "-")
            if "Stock Splits" in recent_actions.columns:
                s = row.get("Stock Splits", 0)
                r.append(f"{s:.1f}" if s > 0 else "-")
            data_a.append(r)
        widths = [60] + [65] * (len(headers_a) - 1)
        pdf.add_table(headers_a, data_a, col_widths=widths)
    else:
        pdf.body_text("No corporate actions data available for this security.")

    # ── Financial Statements Summary
    pdf.section_title("6. Financial Statements Summary")

    if not income.empty:
        pdf.sub_title("Income Statement Highlights")
        key_rows = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income", "EBITDA"]
        for row_name in key_rows:
            if row_name in income.index:
                vals = income.loc[row_name]
                latest = vals.iloc[0] if len(vals) > 0 else None
                if latest is not None:
                    pdf.key_value(row_name, fmt(latest, prefix=f"{currency} ", div=1e9))
        pdf.ln(2)

    if not balance.empty:
        pdf.sub_title("Balance Sheet Highlights")
        key_rows_b = ["Total Assets", "Total Liabilities Net Minority Interest",
                       "Stockholders Equity", "Total Debt", "Cash And Cash Equivalents"]
        for row_name in key_rows_b:
            if row_name in balance.index:
                vals = balance.loc[row_name]
                latest = vals.iloc[0] if len(vals) > 0 else None
                if latest is not None:
                    pdf.key_value(row_name, fmt(latest, prefix=f"{currency} ", div=1e9))
        pdf.ln(2)

    if not cashflow.empty:
        pdf.sub_title("Cash Flow Highlights")
        key_rows_c = ["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow",
                       "Investing Cash Flow", "Financing Cash Flow"]
        for row_name in key_rows_c:
            if row_name in cashflow.index:
                vals = cashflow.loc[row_name]
                latest = vals.iloc[0] if len(vals) > 0 else None
                if latest is not None:
                    pdf.key_value(row_name, fmt(latest, prefix=f"{currency} ", div=1e9))

    # ── Disclaimer
    pdf.add_page()
    pdf.section_title("Disclaimer")
    pdf.body_text(
        "This report is generated automatically by FinScope using publicly available data from Yahoo Finance "
        "(yfinance). It is intended for informational and educational purposes only and does not constitute "
        "financial, investment, or trading advice. The information provided may not be accurate, complete, "
        "or current. Past performance does not guarantee future results.\n\n"
        "Users should conduct their own due diligence and consult qualified financial advisors before making "
        "any investment decisions. FinScope assumes no liability for any losses or damages arising from the "
        "use of this report."
    )

    return bytes(pdf.output())


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <span style="font-size: 2.5rem;">📊</span>
        <h2 style="color: #ffffff; margin: 0.3rem 0 0 0; font-weight: 800; letter-spacing: -0.5px;">FinScope</h2>
        <p style="color: rgba(255,255,255,0.5); font-size: 0.78rem; margin: 0;">Global Financial Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Advanced Search Integration
    if 'selected_ticker' not in st.session_state:
        st.session_state.selected_ticker = "AAPL"
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""

    search_query = st.text_input("🔍 Search Company or Ticker", 
                                value=st.session_state.search_query,
                                placeholder="e.g. Apple, Reliance, Tesla...")
    
    if search_query and search_query != st.session_state.search_query:
        st.session_state.search_query = search_query
        results = search_ticker(search_query)
        if results:
            st.session_state.search_results = results
        else:
            st.sidebar.warning("No matches found. Try a different name.")
    
    if 'search_results' in st.session_state and search_query:
        options = {f"{r['name']} ({r['symbol']}) - {r['exchange']}": r['symbol'] for r in st.session_state.search_results}
        selected_option = st.selectbox("Select Result", options.keys(), index=0)
        if selected_option:
            st.session_state.selected_ticker = options[selected_option]

    st.markdown("")
    quick_pick = st.selectbox("⚡ Quick Pick", [""] + POPULAR_STOCKS, 
                               index=0, key="quick_pick")
    if quick_pick:
        st.session_state.selected_ticker = quick_pick

    selected_ticker = st.session_state.selected_ticker

    st.markdown("---")

    # Global Markets Sidebar
    st.sidebar.markdown("""
    <p style="color: rgba(255,255,255,0.7); font-size: 0.78rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; margin-bottom: 0.5rem;">🌏 Global Overview</p>
    """, unsafe_allow_html=True)
    
    market_categories = {
        "📉 Indices": ["S&P 500", "NASDAQ", "Dow Jones", "FTSE 100", "DAX", "Nikkei 225", "Hang Seng", "SENSEX", "NIFTY 50", "ASX 200"],
        "💱 Currencies": ["EUR/USD", "GBP/USD", "USD/JPY"],
        "🏗️ Commodities": ["Gold", "Brent Oil", "Silver"],
        "₿ Crypto": ["Bitcoin", "Ethereum"]
    }

    for cat_name, symbols in market_categories.items():
        with st.sidebar.expander(cat_name, expanded=(cat_name == "📉 Indices")):
            for name in symbols:
                symbol = GLOBAL_INDICES.get(name)
                if symbol:
                    data = fetch_index_data(symbol)
                    if data:
                        price, change, pct = data
                        color = "#00e676" if change >= 0 else "#ff5252"
                        arrow = "▲" if change >= 0 else "▼"
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 0.1rem;">
                            <span style="color: rgba(255,255,255,0.5);">{name}</span>
                            <span style="color: {color}; font-weight: 600;">{price:,.2f}</span>
                        </div>
                        <div style="text-align: right; font-size: 0.72rem; color: {color}; margin-bottom: 0.6rem; opacity: 0.8;">
                            {arrow} {abs(pct):.2f}%
                        </div>
                        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
    <p style="color: rgba(255,255,255,0.35); font-size: 0.7rem; text-align: center;">
        Data from Yahoo Finance<br>
        Last refresh: {datetime.now().strftime('%H:%M:%S')}
    </p>
    """, unsafe_allow_html=True)

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <h1>📊 FinScope Dashboard</h1>
    <p>Real-time financial intelligence powered by Yahoo Finance • {datetime.now().strftime('%A, %B %d, %Y')}</p>
</div>
""", unsafe_allow_html=True)

# Fetch data
with st.spinner(f"Loading data for **{selected_ticker}**..."):
    info = fetch_stock_data(selected_ticker)
    stock = yf.Ticker(selected_ticker)

if not info:
    st.error(f"⚠️ Could not fetch data for **{selected_ticker}**. Please verify the ticker symbol and try again.")
    st.stop()

# ── Company header
name = info.get("longName", selected_ticker)
sector = info.get("sector", "N/A")
industry = info.get("industry", "N/A")
currency = info.get("currency", "USD")
current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose", 0)
prev_close = info.get("previousClose", current_price)
price_change = current_price - prev_close if current_price and prev_close else 0
price_pct = (price_change / prev_close * 100) if prev_close else 0

col_title, col_price = st.columns([3, 1])
with col_title:
    st.markdown(f"""
    <h2 style="color:#ffffff; margin:0; font-weight:800;">{name}</h2>
    <p style="color:rgba(255,255,255,0.5); margin:0.2rem 0; font-size:0.88rem;">
        {selected_ticker} • {sector} • {industry} • {info.get('exchange', 'N/A')}
    </p>
    """, unsafe_allow_html=True)

with col_price:
    delta_class = "metric-delta-pos" if price_change >= 0 else "metric-delta-neg"
    arrow = "▲" if price_change >= 0 else "▼"
    st.markdown(f"""
    <div style="text-align: right;">
        <span style="color:#ffffff; font-size:2rem; font-weight:800;">{currency} {current_price:,.2f}</span><br>
        <span class="{delta_class}">{arrow} {abs(price_change):,.2f} ({abs(price_pct):.2f}%)</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# ── Key Metrics Strip
metrics_cols = st.columns(6)
metric_items = [
    ("Market Cap", f"{currency} {info.get('marketCap', 0)/1e9:.2f}B" if info.get('marketCap') else "N/A"),
    ("P/E Ratio", f"{info.get('trailingPE', 0):.2f}" if info.get('trailingPE') else "N/A"),
    ("EPS", f"{currency} {info.get('trailingEps', 0):.2f}" if info.get('trailingEps') else "N/A"),
    ("52W High", f"{currency} {info.get('fiftyTwoWeekHigh', 0):,.2f}" if info.get('fiftyTwoWeekHigh') else "N/A"),
    ("52W Low", f"{currency} {info.get('fiftyTwoWeekLow', 0):,.2f}" if info.get('fiftyTwoWeekLow') else "N/A"),
    ("Volume", f"{info.get('volume', 0):,}" if info.get('volume') else "N/A"),
]
for col, (label, value) in zip(metrics_cols, metric_items):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 Price Charts",
    "🎯 Analyst Recommendations",
    "📰 News",
    "⚖️ Peer Comparison",
    "📜 Historical Actions",
    "📊 Financials",
    "📄 Research Report",
])


# ── TAB 1: PRICE CHARTS
with tab1:
    st.markdown('<div class="section-header">Interactive Price Charts</div>', unsafe_allow_html=True)

    chart_col1, chart_col2, chart_col3 = st.columns([2, 2, 1])
    with chart_col1:
        period_label = st.selectbox("Time Period", list(PERIOD_MAP.keys()), index=5)
    with chart_col2:
        chart_type = st.selectbox("Chart Type", ["Candlestick", "Line", "Area", "OHLC"])
    with chart_col3:
        show_volume = st.checkbox("Show Volume", value=True)

    period = PERIOD_MAP[period_label]
    interval = INTERVAL_MAP[period_label]
    hist = fetch_history(selected_ticker, period, interval)

    if not hist.empty:
        # Main chart
        if show_volume:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                vertical_spacing=0.03, row_heights=[0.75, 0.25])
        else:
            fig = make_subplots(rows=1, cols=1)

        if chart_type == "Candlestick":
            fig.add_trace(go.Candlestick(
                x=hist.index, open=hist["Open"], high=hist["High"],
                low=hist["Low"], close=hist["Close"], name="OHLC",
                increasing_line_color="#00e676", decreasing_line_color="#ff5252",
                increasing_fillcolor="#00e676", decreasing_fillcolor="#ff5252",
            ), row=1, col=1)
        elif chart_type == "OHLC":
            fig.add_trace(go.Ohlc(
                x=hist.index, open=hist["Open"], high=hist["High"],
                low=hist["Low"], close=hist["Close"], name="OHLC",
                increasing_line_color="#00e676", decreasing_line_color="#ff5252",
            ), row=1, col=1)
        elif chart_type == "Area":
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"], mode="lines", name="Close",
                line=dict(color="#667eea", width=2),
                fill="tozeroy", fillcolor="rgba(102,126,234,0.15)",
            ), row=1, col=1)
        else:  # Line
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"], mode="lines", name="Close",
                line=dict(color="#667eea", width=2.5),
            ), row=1, col=1)

        # Moving averages
        if len(hist) >= 20:
            ma20 = hist["Close"].rolling(20).mean()
            fig.add_trace(go.Scatter(
                x=hist.index, y=ma20, mode="lines", name="MA 20",
                line=dict(color="#ffc107", width=1, dash="dot"), opacity=0.7,
            ), row=1, col=1)

        if len(hist) >= 50:
            ma50 = hist["Close"].rolling(50).mean()
            fig.add_trace(go.Scatter(
                x=hist.index, y=ma50, mode="lines", name="MA 50",
                line=dict(color="#ff9800", width=1, dash="dash"), opacity=0.7,
            ), row=1, col=1)

        # Volume
        if show_volume and "Volume" in hist.columns:
            colors = ["#00e676" if c >= o else "#ff5252"
                      for c, o in zip(hist["Close"], hist["Open"])]
            fig.add_trace(go.Bar(
                x=hist.index, y=hist["Volume"], name="Volume",
                marker_color=colors, opacity=0.5,
            ), row=2, col=1)

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=30, b=0),
            height=550,
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        font=dict(size=11)),
            font=dict(family="Inter"),
            hovermode="x unified",
        )
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.04)", zeroline=False)
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)", zeroline=False)

        st.plotly_chart(fig, use_container_width=True)

        # Price statistics
        st.markdown('<div class="section-header">Price Statistics</div>', unsafe_allow_html=True)
        stat_cols = st.columns(4)
        close = hist["Close"]
        returns = close.pct_change().dropna()

        stats = [
            ("Period Return", f"{((close.iloc[-1]/close.iloc[0])-1)*100:.2f}%",
             ((close.iloc[-1]/close.iloc[0])-1)*100 >= 0),
            ("Avg Daily Return", f"{returns.mean()*100:.4f}%", returns.mean() >= 0),
            ("Volatility", f"{returns.std()*100:.4f}%", None),
            ("Max Drawdown", f"{((close/close.cummax())-1).min()*100:.2f}%", None),
        ]

        for col, (label, value, positive) in zip(stat_cols, stats):
            with col:
                delta_cls = ""
                if positive is True:
                    delta_cls = "metric-delta-pos"
                elif positive is False:
                    delta_cls = "metric-delta-neg"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value {'metric-delta-pos' if positive else 'metric-delta-neg' if positive is False else ''}">{value}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("No historical data available for this period.")


# ── TAB 2: ANALYST RECOMMENDATIONS
with tab2:
    st.markdown('<div class="section-header">Analyst Recommendations & Price Targets</div>', unsafe_allow_html=True)

    # Price targets
    target_cols = st.columns(4)
    targets = [
        ("Target High", info.get("targetHighPrice"), "#00e676"),
        ("Target Mean", info.get("targetMeanPrice"), "#667eea"),
        ("Target Median", info.get("targetMedianPrice"), "#ffc107"),
        ("Target Low", info.get("targetLowPrice"), "#ff5252"),
    ]
    for col, (label, val, color) in zip(target_cols, targets):
        with col:
            display = f"{currency} {val:,.2f}" if val else "N/A"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{display}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # Consensus
    rec_key = info.get("recommendationKey", "none")
    num_analysts = info.get("numberOfAnalystOpinions", 0)
    rec_class = "rec-buy" if rec_key in ("buy", "strong_buy") else "rec-sell" if rec_key in ("sell", "strong_sell") else "rec-hold" if rec_key == "hold" else "rec-neutral"

    col_rec1, col_rec2 = st.columns(2)
    with col_rec1:
        st.markdown(f"""
        <div class="info-box" style="text-align:center;">
            <div class="label">Consensus Rating</div>
            <div style="margin-top:0.5rem;">
                <span class="rec-badge {rec_class}">{rec_key.replace("_", " ").upper()}</span>
            </div>
            <div style="color:rgba(255,255,255,0.4); font-size:0.75rem; margin-top:0.5rem;">
                Based on {num_analysts} analyst(s)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_rec2:
        if current_price and info.get("targetMeanPrice"):
            upside = ((info["targetMeanPrice"] - current_price) / current_price) * 100
            u_color = "#00e676" if upside >= 0 else "#ff5252"
            u_arrow = "▲" if upside >= 0 else "▼"
            st.markdown(f"""
            <div class="info-box" style="text-align:center;">
                <div class="label">Upside / Downside Potential</div>
                <div style="margin-top:0.5rem; font-size:1.8rem; font-weight:800; color:{u_color};">
                    {u_arrow} {abs(upside):.2f}%
                </div>
                <div style="color:rgba(255,255,255,0.4); font-size:0.75rem; margin-top:0.3rem;">
                    vs Mean Target {currency} {info['targetMeanPrice']:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # Recommendations table
    recs = fetch_recommendations(selected_ticker)
    if not recs.empty:
        st.markdown('<div class="section-header">Recent Analyst Actions</div>', unsafe_allow_html=True)

        # Visualize recommendation distribution
        grade_counts = {}
        grade_col = "To Grade" if "To Grade" in recs.columns else "toGrade" if "toGrade" in recs.columns else None
        if grade_col and grade_col in recs.columns:
            for g in recs[grade_col].dropna():
                g_str = str(g).strip()
                if g_str:
                    grade_counts[g_str] = grade_counts.get(g_str, 0) + 1

        if grade_counts:
            fig_rec = go.Figure(go.Bar(
                x=list(grade_counts.values()),
                y=list(grade_counts.keys()),
                orientation="h",
                marker=dict(
                    color=list(grade_counts.values()),
                    colorscale=[[0, "#ff5252"], [0.5, "#ffc107"], [1, "#00e676"]],
                ),
                text=list(grade_counts.values()),
                textposition="outside",
            ))
            fig_rec.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=300,
                margin=dict(l=0, r=40, t=10, b=0),
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=False),
                font=dict(family="Inter"),
            )
            st.plotly_chart(fig_rec, use_container_width=True)

        # Table
        display_recs = recs.tail(25).sort_index(ascending=False)
        st.dataframe(display_recs, use_container_width=True, height=400)
    else:
        st.info("No analyst recommendations available for this ticker.")


# ── TAB 3: NEWS
with tab3:
    st.markdown('<div class="section-header">Latest Market News & Analysis</div>', unsafe_allow_html=True)

    # Note about yfinance news source
    st.info("📰 **Real-Time News:** News is fetched from Yahoo Finance providing live market insights and company updates sorted by domain expertise.")

    # News controls
    news_col1, news_col2, news_col3 = st.columns([2, 1, 1])

    # News source options (yfinance only)
    available_sources = ["All Sources", "Yahoo Finance"]

    with news_col1:
        news_source = st.selectbox("News Source", available_sources)
    with news_col2:
        sentiment_filter = st.selectbox("Sentiment", ["All", "Positive", "Negative", "Neutral"])
    with news_col3:
        category_filter = st.selectbox("Category", ["All", "Earnings", "Mergers", "Regulatory", "Product", "Market", "Executive", "Economic", "General"])

    # Fetch enhanced news
    company_name = info.get("longName", "").split()[0] if info.get("longName") else None
    news_items = fetch_enhanced_news(selected_ticker, company_name)

    # Filter news
    filtered_news = []
    for item in news_items:
        # Source filter
        if news_source != "All Sources" and item.get('source') != news_source:
            continue

        # Sentiment filter
        if sentiment_filter != "All" and item.get('sentiment') != sentiment_filter.lower():
            continue

        # Category filter
        if category_filter != "All":
            item_category = categorize_news(item.get('title', ''), item.get('summary', ''))
            if item_category != category_filter:
                continue

        filtered_news.append(item)

    if filtered_news:
        # News statistics
        sentiment_counts = {}
        category_counts = {}
        for item in filtered_news:
            sent = item.get('sentiment', 'neutral')
            sentiment_counts[sent] = sentiment_counts.get(sent, 0) + 1

            cat = categorize_news(item.get('title', ''), item.get('summary', ''))
            category_counts[cat] = category_counts.get(cat, 0) + 1

        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            total_news = len(filtered_news)
            st.metric("Total Articles", total_news)
        with stat_col2:
            pos_pct = (sentiment_counts.get('positive', 0) / total_news * 100) if total_news > 0 else 0
            st.metric("Positive Sentiment", f"{pos_pct:.1f}%")
        with stat_col3:
            top_cat = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else "N/A"
            st.metric("Top Category", top_cat)

        st.markdown("---")

        # Display news items
        for idx, n in enumerate(filtered_news[:15]):
            with st.container():
                col_n1, col_n2 = st.columns([1, 4])

                # Thumbnail
                thumb = None
                if "thumbnail" in n and n["thumbnail"] and "resolutions" in n["thumbnail"]:
                    thumb = n["thumbnail"]["resolutions"][0]["url"]
                elif n.get('thumbnail') and isinstance(n['thumbnail'], dict):
                    thumb = n['thumbnail'].get('url')

                with col_n1:
                    if thumb:
                        try:
                            st.image(thumb, use_container_width=True)
                        except:
                            st.markdown("""
                            <div style="background: rgba(255,255,255,0.05); aspect-ratio: 16/9; display: flex; align-items: center; justify-content: center; border-radius: 8px;">
                                <span style="font-size: 2rem; opacity: 0.3;">📰</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background: rgba(255,255,255,0.05); aspect-ratio: 16/9; display: flex; align-items: center; justify-content: center; border-radius: 8px;">
                            <span style="font-size: 2rem; opacity: 0.3;">📰</span>
                        </div>
                        """, unsafe_allow_html=True)

                with col_n2:
                    # Title with sentiment indicator
                    sentiment = n.get('sentiment', 'neutral')
                    sentiment_emoji = {'positive': '🟢', 'negative': '🔴', 'neutral': '🟡'}.get(sentiment, '🟡')
                    category = categorize_news(n.get('title', ''), n.get('summary', ''))

                    st.markdown(f"#### {sentiment_emoji} [{n.get('title')}]({n.get('link', '#')})")

                    # Metadata
                    pub_time = datetime.fromtimestamp(n.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M')
                    source = n.get('source', 'Unknown')
                    publisher = n.get('publisher', 'Unknown')

                    st.markdown(f"""
                    <p style="color: rgba(255,255,255,0.4); font-size: 0.8rem; margin: 0.2rem 0;">
                        <strong>{publisher}</strong> • {pub_time} • {source} • {category}
                    </p>
                    """, unsafe_allow_html=True)

                    # Summary
                    summary = n.get('summary', '')
                    if summary and len(summary) > 50:
                        st.markdown(f"""
                        <p style="color: rgba(255,255,255,0.7); font-size: 0.85rem; margin: 0.5rem 0; line-height: 1.4;">
                            {summary[:200]}{'...' if len(summary) > 200 else ''}
                        </p>
                        """, unsafe_allow_html=True)

                st.markdown('<div style="margin: 1.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);"></div>', unsafe_allow_html=True)
    else:
        st.info(f"No news found for {selected_ticker} matching your filters. Try adjusting the filters or check back later.")


# ── TAB 4: PEER COMPARISON
with tab4:
    st.markdown('<div class="section-header">Intelligent Global Peer Comparison</div>', unsafe_allow_html=True)

    # Peer selection method
    peer_method = st.radio("Peer Selection Method",
                          ["Industry Leaders", "Intelligent Matching", "Custom Selection"],
                          horizontal=True)

    if peer_method == "Custom Selection":
        custom_peers = st.multiselect("Select Peer Companies",
                                     POPULAR_STOCKS + [t for t in GLOBAL_INDICES.keys() if t not in GLOBAL_INDICES],
                                     default=[], max_selections=5)
        comparison_tickers = [selected_ticker] + custom_peers
    else:
        # Get intelligent peers
        market_cap = info.get('marketCap')
        country = info.get('country')
        if peer_method == "Intelligent Matching":
            peers = get_intelligent_peers(selected_ticker, industry, sector, market_cap, country)
        else:  # Industry Leaders
            peers = get_industry_peers(industry, sector)

        comparison_tickers = list(dict.fromkeys([selected_ticker] + peers))[:6]

    with st.spinner(f"Comparing {selected_ticker} with {len(comparison_tickers)-1} peer companies..."):
        peer_df = fetch_peer_data(comparison_tickers)

    if not peer_df.empty:
        # Peer overview
        st.markdown("#### Peer Company Overview")
        overview_cols = st.columns(len(comparison_tickers))
        for i, (_, row) in enumerate(peer_df.iterrows()):
            if i < len(overview_cols):
                with overview_cols[i]:
                    is_selected = row['Ticker'] == selected_ticker
                    border_style = "border: 2px solid #667eea;" if is_selected else "border: 1px solid rgba(255,255,255,0.1);"

                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.03); {border_style} border-radius: 10px; padding: 1rem; text-align: center; margin-bottom: 0.5rem;">
                        <div style="font-weight: 700; font-size: 1.1rem; color: {'#667eea' if is_selected else '#ffffff'};">
                            {row['Ticker']}
                        </div>
                        <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6); margin: 0.2rem 0;">
                            {row['Name'][:20]}{'...' if len(str(row['Name'])) > 20 else ''}
                        </div>
                        <div style="font-size: 1rem; font-weight: 600; color: #ffffff;">
                            {row['Currency']} {row['Price']:,.2f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")

        # Comparison Table
        st.markdown("#### Key Metrics Comparison")
        formatted_df = peer_df.copy()

        # Format market cap
        formatted_df["Market Cap"] = formatted_df["Market Cap"].apply(
            lambda x: f"{x/1e9:,.2f}B" if pd.notnull(x) and x > 0 else "N/A"
        )

        # Format revenue
        formatted_df["Revenue"] = formatted_df["Revenue"].apply(
            lambda x: f"{x/1e9:,.2f}B" if pd.notnull(x) and x > 0 else "N/A"
        )

        # Format dividend yield
        formatted_df["Div Yield"] = formatted_df["Div Yield"].apply(
            lambda x: f"{x*100:.2f}%" if pd.notnull(x) and x > 0 else "N/A"
        )

        # Format P/E ratio
        formatted_df["P/E Ratio"] = formatted_df["P/E Ratio"].apply(
            lambda x: f"{x:.2f}" if pd.notnull(x) and x > 0 else "N/A"
        )

        # Highlight selected company
        def highlight_selected(val):
            if val == selected_ticker:
                return 'background-color: rgba(102,126,234,0.2)'
            return ''

        styled_df = formatted_df.drop(columns=["Currency"]).style.applymap(
            highlight_selected, subset=["Ticker"]
        )

        st.dataframe(styled_df, use_container_width=True)

        # Performance comparison
        st.markdown("#### Relative Performance Comparison")
        perf_periods = st.multiselect("Compare Performance Over",
                                     ["1 Month", "3 Months", "6 Months", "1 Year", "2 Years"],
                                     default=["1 Year"], max_selections=3)

        for period in perf_periods:
            period_key = PERIOD_MAP[period]
            interval_key = INTERVAL_MAP[period]

            comp_hist = {}
            for t in comparison_tickers:
                h = fetch_history(t, period_key, interval_key)
                if not h.empty and len(h) > 1:
                    # Normalize to percentage change from start
                    start_price = h["Close"].iloc[0]
                    comp_hist[t] = ((h["Close"] - start_price) / start_price) * 100

            if comp_hist:
                fig_perf = go.Figure()
                for t, series in comp_hist.items():
                    is_selected = t == selected_ticker
                    fig_perf.add_trace(go.Scatter(
                        x=series.index, y=series, mode="lines",
                        name=f"{t} ({peer_df[peer_df['Ticker']==t]['Name'].iloc[0][:15] if not peer_df[peer_df['Ticker']==t].empty else t})",
                        line=dict(width=3 if is_selected else 2, color='#667eea' if is_selected else None),
                        opacity=1 if is_selected else 0.7
                    ))

                fig_perf.update_layout(
                    title=f"Relative Performance - {period}",
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=400,
                    margin=dict(l=0, r=0, t=40, b=0),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    font=dict(family="Inter"),
                    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False, title="% Change")
                )
                st.plotly_chart(fig_perf, use_container_width=True)

    else:
        st.warning("Unable to fetch peer comparison data. Please try again later.")


# ── TAB 5: HISTORICAL ACTIONS
with tab5:
    st.markdown('<div class="section-header">Stock Actions — Dividends & Splits</div>', unsafe_allow_html=True)

    actions = fetch_actions(selected_ticker)

    if not actions.empty:
        col_a1, col_a2 = st.columns(2)

        # Dividends
        if "Dividends" in actions.columns:
            divs = actions[actions["Dividends"] > 0][["Dividends"]].copy()
            with col_a1:
                st.markdown('<div class="section-header">💰 Dividend History</div>', unsafe_allow_html=True)
                if not divs.empty:
                    fig_div = go.Figure()
                    fig_div.add_trace(go.Bar(
                        x=divs.index, y=divs["Dividends"],
                        marker_color="#667eea",
                        marker_line_color="#764ba2",
                        marker_line_width=1,
                        name="Dividend",
                    ))
                    fig_div.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=350,
                        margin=dict(l=0, r=0, t=10, b=0),
                        xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", title="Amount"),
                        font=dict(family="Inter"),
                    )
                    st.plotly_chart(fig_div, use_container_width=True)

                    # Stats
                    total_div = divs["Dividends"].sum()
                    avg_div = divs["Dividends"].mean()
                    div_yield = info.get("dividendYield")
                    sc1, sc2, sc3 = st.columns(3)
                    with sc1:
                        st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Paid</div>
                        <div class="metric-value">{currency} {total_div:.2f}</div></div>""", unsafe_allow_html=True)
                    with sc2:
                        st.markdown(f"""<div class="metric-card"><div class="metric-label">Avg Dividend</div>
                        <div class="metric-value">{currency} {avg_div:.4f}</div></div>""", unsafe_allow_html=True)
                    with sc3:
                        yield_str = f"{div_yield*100:.2f}%" if div_yield else "N/A"
                        st.markdown(f"""<div class="metric-card"><div class="metric-label">Current Yield</div>
                        <div class="metric-value">{yield_str}</div></div>""", unsafe_allow_html=True)

                    st.markdown("")
                    st.dataframe(divs.sort_index(ascending=False).head(30), use_container_width=True)
                else:
                    st.info("No dividend payments recorded.")

        # Splits
        if "Stock Splits" in actions.columns:
            splits = actions[actions["Stock Splits"] > 0][["Stock Splits"]].copy()
            with col_a2:
                st.markdown('<div class="section-header">✂️ Stock Splits</div>', unsafe_allow_html=True)
                if not splits.empty:
                    split_data = []
                    for idx, row in splits.iterrows():
                        date_str = idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx)[:10]
                        ratio = row["Stock Splits"]
                        split_data.append({"Date": date_str, "Split Ratio": f"{ratio}:1"})
                    st.dataframe(pd.DataFrame(split_data), use_container_width=True)
                else:
                    st.info("No stock splits recorded.")
    else:
        st.info("No stock actions (dividends/splits) data available for this ticker.")

    # Full historical data download
    st.markdown('<div class="section-header">📥 Download Full Historical Data</div>', unsafe_allow_html=True)
    dl_period = st.selectbox("Select period for download", list(PERIOD_MAP.keys()), index=9, key="dl_period")
    dl_data = fetch_history(selected_ticker, PERIOD_MAP[dl_period], INTERVAL_MAP[dl_period])

    if not dl_data.empty:
        csv_buffer = dl_data.to_csv()
        st.download_button(
            label=f"⬇️ Download {selected_ticker} Historical Data (CSV)",
            data=csv_buffer,
            file_name=f"{selected_ticker}_historical_{dl_period.replace(' ', '_').lower()}.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ── TAB 6: FINANCIALS
with tab6:
    st.markdown('<div class="section-header">Financial Statements</div>', unsafe_allow_html=True)
    income, balance, cashflow = fetch_financials(selected_ticker)

    fin_tab1, fin_tab2, fin_tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])

    with fin_tab1:
        if not income.empty:
            st.dataframe(income, use_container_width=True, height=450)
        else:
            st.info("Income statement data not available.")

    with fin_tab2:
        if not balance.empty:
            st.dataframe(balance, use_container_width=True, height=450)
        else:
            st.info("Balance sheet data not available.")

    with fin_tab3:
        if not cashflow.empty:
            st.dataframe(cashflow, use_container_width=True, height=450)
        else:
            st.info("Cash flow data not available.")

    # Revenue & Net Income chart
    if not income.empty:
        st.markdown('<div class="section-header">Revenue & Net Income Trend</div>', unsafe_allow_html=True)
        rev_data = {}
        ni_data = {}
        for col in income.columns:
            year = col.strftime("%Y") if hasattr(col, 'strftime') else str(col)[:4]
            if "Total Revenue" in income.index:
                rev_data[year] = income.loc["Total Revenue", col]
            if "Net Income" in income.index:
                ni_data[year] = income.loc["Net Income", col]

        if rev_data:
            years = sorted(rev_data.keys())
            fig_fin = go.Figure()
            fig_fin.add_trace(go.Bar(
                x=years, y=[rev_data[y]/1e9 for y in years],
                name="Revenue (B)", marker_color="#667eea",
            ))
            if ni_data:
                fig_fin.add_trace(go.Bar(
                    x=years, y=[ni_data.get(y, 0)/1e9 for y in years],
                    name="Net Income (B)", marker_color="#00e676",
                ))
            fig_fin.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=350,
                margin=dict(l=0, r=0, t=10, b=0),
                barmode="group",
                font=dict(family="Inter"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)", title=f"Amount ({currency} Billions)"),
            )
            st.plotly_chart(fig_fin, use_container_width=True)


# ── TAB 7: RESEARCH REPORT
with tab7:
    st.markdown('<div class="section-header">📄 Equity Research Report Generator</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="info-box">
        <div class="label">Report Details</div>
        <div class="value">
            Generate a comprehensive equity research PDF for <strong>{name} ({selected_ticker})</strong> including
            company overview, key metrics, price performance, analyst recommendations,
            corporate actions, and financial statement summaries.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    report_period = st.selectbox("Historical data period for report",
                                  list(PERIOD_MAP.keys()), index=5, key="report_period")

    if st.button("🚀 Generate Research Report", use_container_width=True, type="primary"):
        with st.spinner("Generating comprehensive equity research report..."):
            report_info = fetch_stock_data(selected_ticker)
            report_stock = yf.Ticker(selected_ticker)
            report_hist = fetch_history(selected_ticker, PERIOD_MAP[report_period],
                                         INTERVAL_MAP[report_period])
            report_recs = fetch_recommendations(selected_ticker)
            report_actions = fetch_actions(selected_ticker)
            report_income, report_balance, report_cashflow = fetch_financials(selected_ticker)

            pdf_bytes = generate_research_pdf(
                selected_ticker, report_info, report_hist,
                report_recs, report_actions,
                report_income, report_balance, report_cashflow,
            )

        st.success("✅ Report generated successfully!")

        st.download_button(
            label=f"⬇️ Download {selected_ticker} Research Report (PDF)",
            data=pdf_bytes,
            file_name=f"FinScope_{selected_ticker}_Research_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        # Preview
        st.markdown('<div class="section-header">Report Preview</div>', unsafe_allow_html=True)
        b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
        pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding: 1rem 0;">
    <p style="color:rgba(255,255,255,0.3); font-size:0.75rem;">
        FinScope © 2025 • Data sourced from Yahoo Finance via yfinance •
        For informational purposes only — not financial advice
    </p>
</div>
""", unsafe_allow_html=True)
