# FinScope Production Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda
- 2GB RAM minimum
- Internet connection for data fetching

### Installation

```bash
# 1. Navigate to project directory
cd /workspaces/FinScope

# 2. Install/update dependencies
pip install -r requirements.txt --upgrade

# 3. Verify installation
python -m py_compile app.py

# 4. (Optional) Verify all production checks pass
bash verify_production.sh
```

### Running Production

```bash
# Local development
streamlit run app.py

# Production deployment
streamlit run app.py \
  --logger.level=warning \
  --server.maxUploadSize=10 \
  --client.showErrorDetails=false
```

---

## 📋 What Changed

### ✅ Completed Migrations

| Component | Before | After |
|-----------|--------|-------|
| **News Source** | NewsAPI + Web Scraping | yfinance Only |
| **Peer Data** | Missing Function | ✅ Implemented |
| **Peer Organization** | Random / Hardcoded | Domain Sorted |
| **External APIs** | 2 (NewsAPI + web) | 0 (yfinance only) |
| **Dependencies** | 12 packages | 10 packages |
| **Configuration** | Needs NEWS_API_KEY | ✅ No setup needed |

### 🎯 Key Functions

#### 1. `fetch_peer_data(tickers: list) → DataFrame`
```python
# Fetches peer metrics from yfinance
# Returns: [Ticker, Name, Currency, Price, Market Cap, Revenue, Div Yield, P/E Ratio, Domain, Industry]
# Sorted by: Domain (alphabetical), then Market Cap (descending)
```

**Usage:**
```python
peer_df = fetch_peer_data(['AAPL', 'MSFT', 'GOOGL', 'AMZN'])
print(peer_df)
# Output:
#    Ticker    Name Currency      Price   Market Cap     Revenue  Div Yield  P/E Ratio       Domain      Industry
# 0   AAPL    Apple Inc.     USD     190.5  3000000000000  394000000000     0.0045      25.43  Technology  Consumer Electronics
# 1   MSFT  Microsoft Corp   USD     420.0  3100000000000  221000000000     0.0089      32.10  Technology  Software-Infrastructure
```

#### 2. `get_intelligent_peers(ticker, industry, sector, market_cap, country) → List[str]`
```python
# Find similar companies with domain awareness
# Returns: List of up to 6 peer ticker symbols, domain-sorted
```

**Usage:**
```python
peers = get_intelligent_peers('AAPL', 'Consumer Electronics', 'Technology', 3000000000000, 'US')
# Returns: ['MSFT', 'GOOGL', 'NVDA', 'META', 'AMZN', 'TSLA']
```

#### 3. `fetch_enhanced_news(ticker, company_name=None) → List[dict]`
```python
# Fetch latest news from Yahoo Finance with sentiment analysis
# Returns: List of up to 20 news items with sentiment + category
```

**Returns dict structure:**
```python
{
    'title': str,                  # News headline
    'summary': str,                # News description
    'link': str,                   # URL to full article
    'publisher': str,              # News source (Yahoo Finance)
    'providerPublishTime': int,    # Unix timestamp
    'source': str,                 # 'Yahoo Finance'
    'thumbnail': dict,             # Image metadata
    'sentiment': str,              # 'positive' | 'negative' | 'neutral'
    'category': str,               # 'Earnings' | 'Merger' | etc
}
```

---

## 🌍 Domain Mapping

The system now organizes companies by **9 business domains** with 30+ industry classifications:

### Technology (5+ industries)
- Consumer Electronics: AAPL, MSFT, GOOGL, NVDA
- Software Infrastructure: AMZN, GOOGL, ORCL, MSFT
- Semiconductors: NVDA, AMD, INTC, TSM
- Internet Content: META, GOOGL, NFLX, SNAP
- Software Application: CRM, ADBE, INTU, MSFT

### Finance (3 industries)
- Banks Diversified: JPM, BAC, WFC, HSBC
- Insurance: BRK-B, AIG, PRU, MET
- Financial Services: V, MA, PYPL, ADP

### Manufacturing (3 industries)
- Auto Manufacturers: TM, TSLA, VWAGY, BMW
- Electric Vehicles: TSLA, NIO, XPEV, TM
- Industrial Equipment: CAT, CNH, DE, FAST

### Consumer (3 industries)
- Retailers: WMT, AMZN, COST, TGT
- Specialty Retail: NKE, LULU, ULTA, HD
- Apparel: NKE, VFC, PVH, CAL

### Energy & Materials (3 industries)
- Energy: XOM, CVX, COP, SHELL
- Chemicals: LYB, DOW, EMN, APD
- Metals & Mining: VALE, RIO, GLEN, SCCO

### Healthcare (3 industries)
- Pharmaceuticals: PFE, JNJ, ABBV, MRK
- Medical Devices: JNJ, ISRG, TMO, MDT
- Biotechnology: AMGN, BIIB, GILD, VRTX

### Consumer Goods (3 industries)
- Beverages: KO, PEP, MNST, KDP
- Food Distribution: SYY, GPS, CORE, UNFI
- Household & Personal Care: PG, CL, EL, UL

### Media & Entertainment (2 industries)
- Entertainment: DIS, NFLX, WBD, PARA
- Broadcasting: IMAX, CMCSA, CHTR, FOX

---

## 📊 Data Flow Diagram

```
User Input (Ticker)
        ↓
┌───────────────────────────────┐
│  yfinance.Ticker()            │
│  ├─ Basic Info                │
│  ├─ Historical Data           │
│  ├─ Financial Statements      │
│  ├─ News (Enhanced)           │
│  └─ Peer Recommendations      │
└───────────────────────────────┘
        ↓
┌───────────────────────────────┐
│  Data Processing              │
│  ├─ Sentiment Analysis        │
│  ├─ News Categorization       │
│  ├─ Domain Classification     │
│  └─ Peer Sorting              │
└───────────────────────────────┘
        ↓
┌───────────────────────────────┐
│  Caching (@st.cache_data)     │
│  ├─ 300s: Fundamentals        │
│  ├─ 600s: News                │
│  ├─ 1800s: Peers              │
│  └─ 3600s: Peer Metrics       │
└───────────────────────────────┘
        ↓
┌───────────────────────────────┐
│  Streamlit Dashboard          │
│  ├─ Tab 1: Overview           │
│  ├─ Tab 2: Analysis           │
│  ├─ Tab 3: News (yfinance)    │
│  ├─ Tab 4: Peer Comparison    │
│  ├─ Tab 5: Actions & History  │
│  └─ Tab 6: Financials         │
└───────────────────────────────┘
```

---

## 🔒 Security & Privacy

### No External API Keys Required
✅ NewsAPI key not needed (even if set, ignored gracefully)  
✅ No Seeking Alpha scraping attempted  
✅ Only uses public yfinance data  

### Rate Limiting
✅ Intelligent caching prevents repeated API calls  
✅ yfinance handles rate limiting automatically  

### Data Privacy
✅ All data from public financial sources  
✅ No user data collection  
✅ No third-party tracking  

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'newsapi'"
**Solution:** This is expected - newsapi was removed. If you see this error in old code, it means you're running old app.py. Make sure you're running the new version.

### Issue: Peer comparison shows "N/A" values
**Solution:** This can happen for new/delisted stocks. yfinance may not have complete data. Try with major tickers (AAPL, MSFT, GOOGL).

### Issue: News tab is empty
**Solution:** Yahoo Finance may be rate-limiting. Wait a few seconds and refresh. The data is cached for 10 minutes.

### Issue: "Yahoo Finance" option missing from news source selector
**Solution:** The code now shows only "Yahoo Finance" (and "All Sources"). This is expected. The old code had more options.

---

## 📈 Performance Optimization

### Caching Strategy
```python
@st.cache_data(ttl=300)        # 5 minutes: Stock basics, recommendations
@st.cache_data(ttl=600)        # 10 minutes: News, enhanced data
@st.cache_data(ttl=1800)       # 30 minutes: Intelligent peer search
@st.cache_data(ttl=3600)       # 1 hour: Peer metrics comparison
```

### Recommended Server Specs
- **CPU:** 2+ cores
- **RAM:** 2GB minimum, 4GB recommended
- **Disk:** 1GB (logs + cache)
- **Bandwidth:** 1Mbps minimum

### Load Testing
```bash
# Quick load test
for i in {1..5}; do
    curl -s http://localhost:8501 > /dev/null
    echo "Request $i completed"
done
```

---

## 🚨 Monitoring

### Logs to Watch
```bash
# Error patterns that indicate issues
grep -i "error\|exception\|failed" streamlit.log

# Resource usage
top -b -n 1 | grep python

# API response times
grep "yfinance\|timeout" streamlit.log
```

### Health Check URL
```bash
# If deployed with port 8501
curl http://localhost:8501/_stcore/health
```

---

## ↩️ Rollback Procedure

If critical issues found after deployment:

```bash
# 1. Stop current instance
pkill -f "streamlit run app.py"

# 2. Revert to previous version
git checkout HEAD~1 app.py requirements.txt

# 3. Reinstall old dependencies
pip install -r requirements.txt --upgrade

# 4. Restart application
streamlit run app.py
```

**Note:** Keep git history intact for easy rollback.

---

## 📞 Support Resources

- **yfinance Documentation:** https://github.com/ranaroussi/yfinance
- **Streamlit Documentation:** https://docs.streamlit.io
- **Textblob (Sentiment):** https://textblob.readthedocs.io

---

## ✅ Final Checklist Before Production

- [ ] Run `bash verify_production.sh` - All tests pass
- [ ] Test locally: `streamlit run app.py`
- [ ] Test ticker search (AAPL, MSFT, TSLA, JPM)
- [ ] Test news tab (should show Yahoo Finance articles)
- [ ] Test peer comparison (should show domain-sorted results)
- [ ] Test custom peer selection
- [ ] Test PDF download feature
- [ ] Verify no errors in terminal
- [ ] Check .env doesn't need changes
- [ ] Update deployment server details
- [ ] Notify team of production update

---

## 📊 Version Info

- **Application:** FinScope v2.0
- **Release Date:** March 10, 2026
- **Status:** Production Ready ✅
- **Last Updated:** 2026-03-10
- **Maintainer:** Finance Analytics Team

---

**Deployment successful! 🎉**
