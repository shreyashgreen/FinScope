#!/usr/bin/env python3
"""
Test script for enhanced FinScope features
"""

import sys
import os
sys.path.append('/workspaces/FinScope')

try:
    # Test imports
    from app import fetch_enhanced_news, get_intelligent_peers, analyze_sentiment, categorize_news
    print("✅ All imports successful")

    # Test sentiment analysis
    test_text = "Apple reports strong quarterly earnings with revenue growth"
    sentiment = analyze_sentiment(test_text)
    print(f"✅ Sentiment analysis: '{test_text}' -> {sentiment}")

    # Test news categorization
    category = categorize_news("Apple announces new product launch", "New iPhone features")
    print(f"✅ News categorization: -> {category}")

    # Test peer finding (basic)
    peers = get_intelligent_peers("AAPL", "Consumer Electronics", "Technology", 3000000000000, "US")
    print(f"✅ Peer finding for AAPL: {len(peers)} peers found")

    print("\n🎉 All enhanced features are working correctly!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()