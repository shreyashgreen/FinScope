# FinScope Codebase Analysis

## 📋 Project Overview
FinScope is a Streamlit-based financial dashboard that provides real-time stock data, intelligent peer comparison, advanced news analysis, and research report generation.

---

## 📁 File Structure & Purposes

### 1. **app.py** (Main Application - ~1,900 lines)
- **Purpose**: Core Streamlit application with all UI and business logic
- **Key Components**:
  - Configuration & styling (CSS, theme)
  - Data fetching functions
  - UI components (tabs, charts, tables)
  - Peer comparison logic
  - Research report generation
  - News display with sentiment analysis

### 2. **debug_app.py** (Testing/Debug - ~35 lines)
- **Purpose**: Minimal test version to debug functionality
- **Contents**: Basic ticker search, data fetching, and news tests
- **Usage**: Troubleshooting without full app complexity

### 3. **requirements.txt** (Dependencies)
- **Purpose**: Python package specifications
- **Key Packages**:
  - `streamlit` (>=1.30.0) - UI framework
  - `yfinance` (>=0.2.40) - Yahoo Finance data
  - `plotly` (>=5.18.0) - Interactive charts
  - `newsapi-python` (>=0.2.7) - NewsAPI integration
  - `textblob` (>=0.17.1) - Sentiment analysis
  - `beautifulsoup4` (>=4.12.0) - Web scraping
  - `python-dotenv` (>=1.0.0) - Environment variables
  - `fpdf2` (>=2.7.0) - PDF generation

### 4. **.env** (Configuration - Not Committed)
- **Purpose**: Environment variables storage
- **Contents**: `NEWS_API_KEY` (optional - for enhanced news)
- **Security**: Not committed to git

### 5. **test_enhancements.py** (Test Script - ~40 lines)
- **Purpose**: Test enhanced features in isolation
- **Tests**: Sentiment analysis, news categorization, peer finding

### 6. **set_news_api.sh** (Setup Script - Shell)
- **Purpose**: Helper script to set up NewsAPI key

### 7. **README.md** (Documentation)
- **Purpose**: User guide and setup instructions

---

## 🔄 Current News Fetching Implementation

### **Three-Tier News Source System**

#### 1. **Yahoo Finance News (Primary - Always Available)**
```python
def fetch_news(ticker: str):
    """Fetch latest stock news."""
    stock = yf.Ticker(ticker)
    return stock.news
```
- Simple wrapper around yfinance
- No API key required
- Limited headlines but reliable

#### 2. **Enhanced Multi-Source News (fetch_enhanced_news)**
Uses fallback approach - tries sources in order:

**Tier 1: Yahoo Finance (via yfinance)**
- Gets `stock.news` data
- Data structure: `{title, summary, link, providerPublishTime, publisher, thumbnail}`
- Adds sentiment analysis and `source: 'Yahoo Finance'` tag

**Tier 2: NewsAPI Integration** (if `NEWS_API_KEY` is set in .env)
```python
newsapi = NewsApiClient(api_key=api_key)
newsapi_response = newsapi.get_everything(
    q=query,  # ticker or company name
    language='en',
    sort_by='publishedAt',
    page_size=5  # Limited for free tier
)
```
- Pulls from 70,000+ news sources
- Free tier: 100 requests/day
- Standardizes response format to match Yahoo Finance structure
- Adds sentiment analysis

**Tier 3: Web Scraping (Fallback)**
- **Source**: Seeking Alpha (seekingalpha.com)
- **Trigger**: Only if less than 5 articles from previous sources
- **Method**: BeautifulSoup HTML parsing
- **Data**: Headlines extracted from `div.title` elements
- **Limitation**: Basic implementation, limited reliability

### **News Processing Pipeline**
1. **Sentiment Analysis** (`analyze_sentiment`):
   - Uses TextBlob polarity scoring
   - Returns: 'positive', 'negative', or 'neutral'
   - Threshold: ±0.1 polarity score

2. **News Categorization** (`categorize_news`):
   - Categories: earnings, mergers, regulatory, product, market, executive, economic
   - Uses keyword matching in title and summary
   - Helps organize news by relevance

3. **Caching**: 
   - `fetch_enhanced_news` cached for 600 seconds (10 minutes)
   - Reduces API usage and improves responsiveness

---

## ⚠️ CRITICAL ISSUE: Missing `fetch_peer_data` Function

### **Problem**
- Called at line 1478: `peer_df = fetch_peer_data(comparison_tickers)`
- **Function is NOT DEFINED** in the codebase
- This causes runtime NameError when peer comparison tab is accessed

### **Usage Context**
```python
comparison_tickers = list(dict.fromkeys([selected_ticker] + peers))[:6]

with st.spinner(f"Comparing {selected_ticker} with {len(comparison_tickers)-1} peer companies..."):
    peer_df = fetch_peer_data(comparison_tickers)  # ❌ UNDEFINED FUNCTION

if not peer_df.empty:
    # Display peer overview, comparison table, performance metrics
```

### **Expected DataFrame Structure**

Based on usage at lines 1500-1540, `peer_df` should have these columns:

| Column | Type | Format | Example |
|--------|------|--------|---------|
| **Ticker** | str | Uppercase | "AAPL" |
| **Name** | str | Company name | "Apple Inc." |
| **Currency** | str | 3-letter code | "USD" |
| **Price** | float | Current stock price | 190.50 |
| **Market Cap** | float | Numeric (displayed as billions) | 3000000000000 |
| **Revenue** | float | Numeric (displayed as billions) | 394000000000 |
| **Div Yield** | float | Decimal (converted to % display) | 0.0045 |
| **P/E Ratio** | float | Numeric, 2 decimals | 25.43 |

### **Implementation Blueprint**
```python
@st.cache_data(ttl=600)
def fetch_peer_data(tickers: list) -> pd.DataFrame:
    """Fetch key metrics for peer companies.
    
    Args:
        tickers: List of ticker symbols
        
    Returns:
        DataFrame with columns: [Ticker, Name, Currency, Price, Market Cap, Revenue, Div Yield, P/E Ratio]
    """
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            data.append({
                'Ticker': ticker,
                'Name': info.get('longName', ticker),
                'Currency': info.get('currency', 'USD'),
                'Price': info.get('currentPrice', 0),
                'Market Cap': info.get('marketCap', 0),
                'Revenue': info.get('totalRevenue', 0),
                'Div Yield': info.get('dividendYield', 0),
                'P/E Ratio': info.get('trailingPE', 0),
            })
        except Exception as e:
            # Handle errors gracefully
            pass
    
    return pd.DataFrame(data)
```

---

## 🔍 Current Peer Matching Implementation

### **Two Peer Discovery Methods**

#### 1. **Industry Leaders Method** (`get_industry_peers`)
- Uses hardcoded industry-to-ticker mapping
- Returns top 3 companies per industry (e.g., MSFT, GOOGL, NVDA for Consumer Electronics)
- Industries covered: 11 major categories
- **Limitation**: Fixed list, doesn't scale to new companies

#### 2. **Intelligent Matching Method** (`get_intelligent_peers`)
- Parameters:
  - `ticker`: Stock symbol
  - `industry`: Company industry
  - `sector`: Business sector
  - `market_cap`: Market capitalization (optional)
  - `country`: Country of domicile (optional)
- Matching algorithm: Filters global stock list by similar characteristics
- **Returns**: Up to 6 similar companies

#### 3. **Custom Selection**
- Users manually select from `POPULAR_STOCKS` list (48 major tickers)
- Alternative: Search from global indices

### **Data Integration**
- Peer selection: Done BEFORE `fetch_peer_data` is called
- Tickers combined with selected ticker: `[selected_ticker] + peers`
- Limited to 6 companies total for performance

---

## 📊 All Data Fetching Functions

| Function | Input | Output | Data Source | Cache | Purpose |
|----------|-------|--------|-------------|-------|---------|
| `fetch_stock_data()` | ticker | dict (info) | yfinance | None | Basic company info |
| `fetch_history()` | ticker, period, interval | DataFrame | yfinance | 120s | Historical prices |
| `fetch_index_data()` | symbol | (price, change, %) | yfinance | 600s | Index snapshots |
| `fetch_recommendations()` | ticker | DataFrame | yfinance | 300s | Analyst ratings |
| `fetch_actions()` | ticker | DataFrame | yfinance | 300s | Dividends & splits |
| `fetch_financials()` | ticker | 3 DataFrames | yfinance | None | Income, balance, cashflow |
| `fetch_news()` | ticker | list | yfinance | None | Basic news headlines |
| `fetch_enhanced_news()` | ticker, company_name | list | yfinance + NewsAPI + Seeking Alpha | 600s | Multi-source news w/ sentiment |
| `fetch_peer_data()` | tickers[] | DataFrame | **❌ NOT DEFINED** | - | Peer comparison metrics |

---

## 🐛 Identified Issues & Bugs

### **CRITICAL**
1. **Missing Function**: `fetch_peer_data()` undefined (line 1478 call fails)
   - **Impact**: Peer comparison tab completely broken
   - **Severity**: BLOCKER
   - **Fix**: Implement function to fetch yfinance info for list of tickers

### **HIGH**
2. **Hard-coded Peer Lists**: `get_industry_peers()` uses fixed mappings
   - **Impact**: Won't find new entrants or updated industry leaders
   - **Severity**: Maintenance burden
   - **Fix**: Add ability to query industry dynamically or expand mappings

3. **Web Scraping Fragility**: Seeking Alpha scraping (line 547) uses brittle CSS selectors
   - **Impact**: Breaks when website updates HTML
   - **Severity**: HIGH (fallback feature unreliable)
   - **Fix**: Use alternative scraping or API

### **MEDIUM**
4. **NewsAPI Silently Fails**: Exceptions caught but not logged (line 530)
   - **Impact**: Users don't know if enhanced news is working
   - **Severity**: MEDIUM (fallback still works)
   - **Fix**: Add logging or warning if NewsAPI fails

5. **Null Value Handling**: Many functions don't properly handle missing data
   - **Impact**: Potential crashes with certain tickers
   - **Severity**: MEDIUM
   - **Example**: `fetch_stock_data()` line 392 has partial fallback

### **LOW**
6. **Limited Error Messages**: Generic exception catches don't provide context
7. **No Rate Limiting**: Could hit Yahoo Finance rate limits with many requests
8. **P/E Ratio Edge Cases**: Negative P/E for unprofitable companies not handled

---

## 🔗 Data Flow Architecture

```
User Input (Ticker Search)
    ↓
search_ticker() [Streamlit search results]
    ↓
User selects ticker
    ↓
fetch_stock_data() [Basic Info]
    ├→ fetch_index_data() [Performance]
    ├→ fetch_history() [Charts]
    ├→ fetch_enhanced_news() [Multi-source News]
    ├→ fetch_recommendations() [Analyst Ratings]
    ├→ fetch_financials() [Income/Balance/Cashflow]
    ├→ fetch_actions() [Dividends/Splits]
    └→ generate_research_pdf() [Report Export]

Peer Comparison Tab
    ↓
get_industry_peers() OR get_intelligent_peers() OR custom selection
    ↓
fetch_peer_data() ❌ [MISSING - SHOULD BE HERE]
    ↓
Display comparison table, charts, metrics
```

---

## 📌 Summary Table

| Category | Status | Count | Notes |
|----------|--------|-------|-------|
| **Files** | ✅ | 7 | app.py, debug_app.py, requirements.txt, .env, test_enhancements.py, README.md, set_news_api.sh |
| **Defined Functions** | ✅ | 14 | search_ticker, get_industry_peers, get_intelligent_peers, fetch_stock_data, fetch_history, fetch_index_data, fetch_recommendations, fetch_actions, fetch_financials, fetch_news, fetch_enhanced_news, analyze_sentiment, categorize_news, generate_research_pdf |
| **Missing Functions** | ❌ | 1 | **fetch_peer_data** (CRITICAL) |
| **News Sources** | ✅ | 3 | Yahoo Finance (primary), NewsAPI (optional), Seeking Alpha (fallback/fragile) |
| **Critical Issues** | ❌ | 1 | fetch_peer_data undefined |
| **High Issues** | ⚠️ | 2 | Hard-coded peers, fragile web scraping |

---

## 🚀 Next Steps to Fix

1. **Implement `fetch_peer_data()` function** - URGENT
2. **Add error handling for missing data** - Important
3. **Improve Seeking Alpha scraping** or replace with reliable alternative
4. **Optimize peer matching algorithm** for better results
5. **Add logging for debugging** news source failures
6. **Consider caching strategy** for peer data

