#!/bin/bash
# FinScope - Streamlit Cloud Deployment Verification
# Run this before deploying to ensure everything is production-ready

set -e

echo "╔═════════════════════════════════════════════════════════════╗"
echo "║   FinScope - Streamlit Cloud Pre-Deployment Verification   ║"
echo "╚═════════════════════════════════════════════════════════════╝"
echo ""

FAILED=0
WARNINGS=0

# Test 1: Python Syntax
echo "🔍 Test 1: Python Syntax Check"
if python3 -m py_compile app.py 2>/dev/null; then
    echo "  ✅ PASS: No syntax errors"
else
    echo "  ❌ FAIL: Syntax errors found"
    FAILED=$((FAILED+1))
fi
echo ""

# Test 2: Required Files
echo "🔍 Test 2: Required Files"
files_ok=true

if [ -f "requirements.txt" ]; then
    echo "  ✅ requirements.txt exists"
else
    echo "  ❌ requirements.txt missing"
    files_ok=false
fi

if [ -f ".streamlit/config.toml" ]; then
    echo "  ✅ .streamlit/config.toml exists"
else
    echo "  ❌ .streamlit/config.toml missing"
    files_ok=false
fi

if [ -f ".gitignore" ]; then
    echo "  ✅ .gitignore exists"
else
    echo "  ⚠️  WARNING: .gitignore missing (not critical)"
    WARNINGS=$((WARNINGS+1))
fi

if [ -f "README.md" ]; then
    echo "  ✅ README.md exists"
else
    echo "  ⚠️  WARNING: README.md missing"
    WARNINGS=$((WARNINGS+1))
fi

if [ "$files_ok" = false ]; then
    FAILED=$((FAILED+1))
fi
echo ""

# Test 3: Git Status
echo "🔍 Test 3: Git Repository Status"
if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "  ✅ Git repository initialized"
    
    # Check if .env is not tracked
    if git check-ignore -q .env 2>/dev/null || [ ! -f ".env" ]; then
        echo "  ✅ .env is properly ignored"
    else
        echo "  ⚠️  WARNING: .env tracked in git (should be ignored)"
        WARNINGS=$((WARNINGS+1))
    fi
else
    echo "  ❌ Not a git repository"
    FAILED=$((FAILED+1))
fi
echo ""

# Test 4: Dependencies
echo "🔍 Test 4: Critical Dependencies"
deps_ok=true

if grep -q "streamlit" requirements.txt; then
    echo "  ✅ streamlit in requirements.txt"
else
    echo "  ❌ streamlit missing from requirements.txt"
    deps_ok=false
fi

if grep -q "yfinance" requirements.txt; then
    echo "  ✅ yfinance in requirements.txt"
else
    echo "  ❌ yfinance missing from requirements.txt"
    deps_ok=false
fi

if grep -q "plotly" requirements.txt; then
    echo "  ✅ plotly in requirements.txt"
else
    echo "  ❌ plotly missing from requirements.txt"
    deps_ok=false
fi

if grep -q "pandas" requirements.txt; then
    echo "  ✅ pandas in requirements.txt"
else
    echo "  ❌ pandas missing from requirements.txt"
    deps_ok=false
fi

if [ "$deps_ok" = false ]; then
    FAILED=$((FAILED+1))
fi
echo ""

# Test 5: Mobile CSS
echo "🔍 Test 5: Mobile Responsive CSS"
mobile_ok=true

if grep -q "@media (max-width: 768px)" app.py; then
    echo "  ✅ Tablet breakpoint (768px) defined"
else
    echo "  ❌ Tablet breakpoint missing"
    mobile_ok=false
fi

if grep -q "@media (max-width: 480px)" app.py; then
    echo "  ✅ Mobile breakpoint (480px) defined"
else
    echo "  ❌ Mobile breakpoint missing"
    mobile_ok=false
fi

if grep -q "hover: none" app.py; then
    echo "  ✅ Touch device detection included"
else
    echo "  ⚠️  WARNING: Touch device detection missing"
    WARNINGS=$((WARNINGS+1))
fi

if [ "$mobile_ok" = false ]; then
    FAILED=$((FAILED+1))
fi
echo ""

# Test 6: No API Keys in Code
echo "🔍 Test 6: Security - No Hardcoded API Keys"
security_ok=true

if ! grep -r "NEWS_API_KEY=" app.py 2>/dev/null | grep -v "os.getenv"; then
    echo "  ✅ No hardcoded NewsAPI keys found"
else
    echo "  ❌ Hardcoded API key found in app.py"
    security_ok=false
fi

if ! grep -q 'api_key = "' app.py; then
    echo "  ✅ No string API keys in code"
else
    echo "  ⚠️  WARNING: String API keys found (check they're from .env)"
    WARNINGS=$((WARNINGS+1))
fi

if [ "$security_ok" = false ]; then
    FAILED=$((FAILED+1))
fi
echo ""

# Test 7: Documentation
echo "🔍 Test 7: Documentation Files"
docs_ok=true

if [ -f "STREAMLIT_CLOUD_DEPLOYMENT.md" ]; then
    echo "  ✅ STREAMLIT_CLOUD_DEPLOYMENT.md exists"
else
    echo "  ⚠️  WARNING: Deployment guide missing"
    WARNINGS=$((WARNINGS+1))
fi

if [ -f "STREAMLIT_DEPLOYMENT_CHECKLIST.md" ]; then
    echo "  ✅ STREAMLIT_DEPLOYMENT_CHECKLIST.md exists"
else
    echo "  ⚠️  WARNING: Deployment checklist missing"
    docs_ok=false
fi

if [ -f ".env.example" ]; then
    echo "  ✅ .env.example provided"
else
    echo "  ⚠️  WARNING: .env.example missing"
    WARNINGS=$((WARNINGS+1))
fi
echo ""

# Test 8: Streamlit Config

echo ""
# Test 9: Index Data Resilience
# ensure fetch_index_data won't crash when invalid symbol or missing data occurs
echo "🔍 Test 9: Index Data Resilience"
if python3 - <<'PYTHON'
from app import fetch_index_data
# invalid symbol should return tuple with None change and not raise
res = fetch_index_data('INVALID')
if res is None or res[1] is None:
    print("  ✅ fetch_index_data handles missing data gracefully")
    exit(0)
else:
    print("  ❌ Unexpected data returned", res)
    exit(1)
PYTHON
then
    echo "  ✅ PASS"
else
    echo "  ❌ FAIL: fetch_index_data crashed or returned bad values"
    FAILED=$((FAILED+1))
fi
echo "🔍 Test 8: Streamlit Configuration"
if [ -f ".streamlit/config.toml" ]; then
    if grep -q "primaryColor" .streamlit/config.toml; then
        echo "  ✅ Theme configuration present"
    else
        echo "  ⚠️  WARNING: Theme configuration missing"
        WARNINGS=$((WARNINGS+1))
    fi
    
    if grep -q "maxUploadSize" .streamlit/config.toml; then
        echo "  ✅ Upload size limit configured"
    else
        echo "  ⚠️  WARNING: Upload size not configured"
        WARNINGS=$((WARNINGS+1))
    fi
else
    echo "  ❌ .streamlit/config.toml missing"
    FAILED=$((FAILED+1))
fi
echo ""

# Final Results
echo "═══════════════════════════════════════════════════════════"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ ALL CRITICAL CHECKS PASSED"
    echo ""
    if [ $WARNINGS -gt 0 ]; then
        echo "⚠️  $WARNINGS warnings found (but not critical)"
    fi
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "🚀 READY FOR DEPLOYMENT ON STREAMLIT CLOUD"
    echo ""
    echo "Next Steps:"
    echo "1. Push to GitHub (if not already done):"
    echo "   git add . && git commit -m 'Ready for Streamlit Cloud'"
    echo "   git push origin main"
    echo ""
    echo "2. Go to https://share.streamlit.io/"
    echo "   Click 'New app' and deploy from:"
    echo "   Repository: shreyashgreen/FinScope"
    echo "   Branch: main"
    echo "   Main file: app.py"
    echo ""
    echo "3. Your app will be live at:"
    echo "   https://finscope.streamlit.app"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    exit 0
else
    echo "❌ $FAILED CRITICAL ISSUES FOUND"
    echo ""
    echo "Please fix the errors above before deploying."
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    exit 1
fi
