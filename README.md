# FinScope - Global Financial Intelligence Dashboard

A comprehensive financial analysis dashboard built with Streamlit, featuring real-time stock data, intelligent peer comparison, and advanced news analysis. **Fully optimized for desktop and mobile devices.**

## 🚀 Quick Start - Live Demo

**Access the live app here:** https://finscope.streamlit.app

The app is deployed on Streamlit Cloud and works perfectly on:
- 💻 Desktop browsers (Chrome, Safari, Firefox)
- 📱 iOS (Safari, Chrome)
- 🤖 Android (Chrome, Firefox, Samsung Internet)
- 📲 Tablets (iPad, Android tablets)

## Features

- 📊 **Real-time Stock Data**: Live prices, charts, and key metrics from Yahoo Finance
- 📰 **Advanced News Analysis**: Yahoo Finance news with sentiment analysis and categorization
- ⚖️ **Intelligent Peer Comparison**: Global peer discovery based on market cap and industry
- 📈 **Interactive Charts**: Candlestick, line, area charts with technical indicators
- 🎯 **Analyst Recommendations**: Price targets and consensus ratings
- 📄 **Research Reports**: Generate comprehensive PDF equity research reports
- 📱 **Mobile Optimized**: Fully responsive design for all screen sizes

## 🌐 Deployment

### Option 1: Live on Streamlit Cloud (Recommended)
The app is already deployed and live at:
```
https://finscope.streamlit.app
```

**Recent Updates (v2.1)**:
- ✅ Enhanced error handling for cloud environments
- ✅ Manual ticker input fallback when search fails
- ✅ Improved network resilience and retry logic
- ✅ Better mobile responsiveness

No setup needed! Just open the URL on any device.

### Option 2: Local Development

1. **Clone the Repository**
   ```bash
   git clone https://github.com/shreyashgreen/FinScope.git
   cd FinScope
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Locally**
   ```bash
   streamlit run app.py
   ```
   
   Then open: http://localhost:8501

### Option 3: Deploy Your Own Instance

1. **Fork the Repository** on GitHub
2. **Go to https://share.streamlit.io/**
3. Click "New app" and select your forked repo
4. Set main file as `app.py`
5. Click Deploy!

See [STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md) for detailed instructions.

## 📱 Mobile Features

### ✅ Fully Responsive Design
- **Breakpoint 1:** Desktop (>768px) - Full layout with sidebars
- **Breakpoint 2:** Tablet (481-768px) - Optimized columns
- **Breakpoint 3:** Mobile (≤480px) - Single column layout
- **Breakpoint 4:** Extra small (<480px) - Compact view

### ✅ Touch-Optimized
- Large buttons and inputs (48px minimum)
- Appropriate spacing for touch targets
- Auto-adjusting font sizes
- No hover-only interactions

### ✅ Performance
- Responsive charts remain readable on all sizes
- Intelligent caching reduces data usage
- Optimized for 3G/4G/5G networks

## Setup & Configuration

### Basic Setup (No Configuration)
Simply run:
```bash
pip install -r requirements.txt
streamlit run app.py
```

The app works out-of-the-box with zero configuration!

### Optional: NewsAPI Key (Not Required)
The app now uses yfinance exclusively for news, so no API key is needed. However, if you want to add other news sources in the future:

1. Get a free API key from [NewsAPI.org](https://newsapi.org/register) (100 requests/day)
2. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Add your key:
   ```
   NEWS_API_KEY=your_api_key_here
   ```

## News Sources

- **Yahoo Finance**: Primary news source (always available) ✅
- All data is real-time and reliable

## Technical Stack

- **Frontend:** Streamlit (Python)
- **Data Source:** yfinance (free, no API key required)
- **Visualizations:** Plotly
- **Data Processing:** Pandas, NumPy
- **Sentiment Analysis:** TextBlob
- **PDF Generation:** FPDF2
- **Deployment:** Streamlit Cloud

## Data Privacy

✅ No personal data collected  
✅ No tracking cookies  
✅ HTTPS encrypted connection  
✅ Session-based state management  
✅ All data from public APIs
3. Analyze news with sentiment indicators
4. Compare with intelligent global peers
5. Generate comprehensive research reports

## Disclaimer

This application is for informational and educational purposes only. Not financial advice. Always conduct your own research before making investment decisions.
