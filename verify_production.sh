#!/bin/bash
# FinScope Production Deployment Verification Script
# This script validates all changes are correctly implemented

set -e

echo "🔍 FinScope Production Deployment Verification"
echo "=============================================="
echo ""

FAILED=0

# Test 1: Python Syntax
echo "✓ Test 1: Python Syntax Validation"
if python3 -m py_compile app.py 2>/dev/null; then
    echo "  ✅ PASS: No syntax errors"
else
    echo "  ❌ FAIL: Syntax errors found"
    FAILED=$((FAILED+1))
fi
echo ""

# Test 2: Check file modifications
echo "✓ Test 2: Code Changes Verification"

changes_ok=true

if ! grep -q "from newsapi import NewsApiClient" app.py; then
    echo "  ✅ NewsAPI import removed"
else
    echo "  ❌ NewsAPI import still present"
    changes_ok=false
fi

if ! grep -q "from bs4 import BeautifulSoup" app.py; then
    echo "  ✅ BeautifulSoup import removed"
else
    echo "  ❌ BeautifulSoup import still present"
    changes_ok=false
fi

if grep -q "INDUSTRY_DOMAIN_MAP" app.py; then
    echo "  ✅ INDUSTRY_DOMAIN_MAP defined"
else
    echo "  ❌ INDUSTRY_DOMAIN_MAP not found"
    changes_ok=false
fi

if grep -q "def fetch_peer_data" app.py; then
    echo "  ✅ fetch_peer_data function added"
else
    echo "  ❌ fetch_peer_data function not found"
    changes_ok=false
fi

if ! grep -q "seekingalpha.com" app.py; then
    echo "  ✅ Web scraping code removed"
else
    echo "  ❌ Web scraping code still present"
    changes_ok=false
fi

if ! grep -q "newsapi_response = newsapi.get_everything" app.py; then
    echo "  ✅ NewsAPI instantiation removed"
else
    echo "  ❌ NewsAPI instantiation still present"
    changes_ok=false
fi

if [ "$changes_ok" = false ]; then
    FAILED=$((FAILED+1))
fi
echo ""

# Test 3: Requirements file
echo "✓ Test 3: Requirements File Check"

if ! grep -q "newsapi-python" requirements.txt; then
    echo "  ✅ newsapi-python removed from requirements.txt"
else
    echo "  ❌ newsapi-python still in requirements.txt"
    FAILED=$((FAILED+1))
fi

if ! grep -q "beautifulsoup4" requirements.txt; then
    echo "  ✅ beautifulsoup4 removed from requirements.txt"
else
    echo "  ❌ beautifulsoup4 still in requirements.txt"
    FAILED=$((FAILED+1))
fi

if grep -q "yfinance" requirements.txt; then
    echo "  ✅ yfinance still in requirements.txt"
else
    echo "  ❌ yfinance missing from requirements.txt"
    FAILED=$((FAILED+1))
fi
echo ""

# Test 4: Function structure
echo "✓ Test 4: Function Structure Verification"

if grep -q "def get_industry_peers" app.py; then
    echo "  ✅ get_industry_peers function present"
else
    echo "  ❌ get_industry_peers function missing"
    FAILED=$((FAILED+1))
fi

if grep -q "def get_intelligent_peers" app.py; then
    echo "  ✅ get_intelligent_peers function present"
else
    echo "  ❌ get_intelligent_peers function missing"
    FAILED=$((FAILED+1))
fi

if grep -q "def fetch_enhanced_news" app.py; then
    echo "  ✅ fetch_enhanced_news function present"
else
    echo "  ❌ fetch_enhanced_news function missing"
    FAILED=$((FAILED+1))
fi

if grep -q "def analyze_sentiment" app.py; then
    echo "  ✅ analyze_sentiment function present"
else
    echo "  ❌ analyze_sentiment function missing"
    FAILED=$((FAILED+1))
fi

if grep -q "def categorize_news" app.py; then
    echo "  ✅ categorize_news function present"
else
    echo "  ❌ categorize_news function missing"
    FAILED=$((FAILED+1))
fi
echo ""

# Test 5: Domain classifications
echo "✓ Test 5: Domain Classification Coverage"

if grep -q '"Technology"' app.py; then
    echo "  ✅ Technology domain defined"
else
    echo "  ❌ Technology domain missing"
    FAILED=$((FAILED+1))
fi

if grep -q '"Finance"' app.py; then
    echo "  ✅ Finance domain defined"
else
    echo "  ❌ Finance domain missing"
    FAILED=$((FAILED+1))
fi

if grep -q '"Healthcare"' app.py; then
    echo "  ✅ Healthcare domain defined"
else
    echo "  ❌ Healthcare domain missing"
    FAILED=$((FAILED+1))
fi

if grep -q '"Consumer"' app.py; then
    echo "  ✅ Consumer domain defined"
else
    echo "  ❌ Consumer domain missing"
    FAILED=$((FAILED+1))
fi
echo ""

# Results
echo "=============================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ ALL TESTS PASSED - READY FOR PRODUCTION"
    echo ""
    echo "Deployment Steps:"
    echo "1. pip install -r requirements.txt --upgrade"
    echo "2. streamlit run app.py  (for local testing)"
    echo "3. Deploy to production server"
    exit 0
else
    echo "❌ $FAILED TEST(S) FAILED - DO NOT DEPLOY"
    echo ""
    echo "Please fix the issues above before deploying to production."
    exit 1
fi
