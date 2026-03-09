import yfinance as yf
import json

def test_search(query):
    print(f"Searching for: {query}")
    try:
        search = yf.Search(query, max_results=5)
        print("Search Results:")
        for res in search.quotes:
            print(f"- {res['symbol']}: {res['shortname']} ({res['quoteType']})")
    except Exception as e:
        print(f"Search failed: {e}")

def test_peers(ticker):
    print(f"\nChecking peers for: {ticker}")
    try:
        t = yf.Ticker(ticker)
        # Some versions or forks might have this, but standard yfinance usually doesn't.
        # Let's see what's in 'info' or other attributes.
        info = t.info
        print(f"Industry: {info.get('industry')}")
        print(f"Sector: {info.get('sector')}")
        
        # Check if there's any 'peers' or 'related' data
        # Often yfinance 'news' or 'recommendations' might have clues, but not direct peers.
    except Exception as e:
        print(f"Peer check failed: {e}")

if __name__ == "__main__":
    test_search("Apple")
    test_search("Reliance Industries")
    test_peers("AAPL")
