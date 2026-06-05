import feedparser
import time
from typing import List, Dict
from modules.analytics.service import sentiment_service

class NewsService:
    def __init__(self):
        self.cache = {} # {symbol: {"data": [...], "timestamp": 12345}}
        self.CACHE_DURATION = 1800 # 30 minutes
        self.RSS_URLS = {
            "general": "https://news.google.com/rss/search?q=Indian+Stock+Market&hl=en-IN&gl=IN&ceid=IN:en",
            "symbol": "https://news.google.com/rss/search?q={}+Stock+India&hl=en-IN&gl=IN&ceid=IN:en"
        }

    def fetch_news_for_portfolio(self, symbols: List[str]) -> List[Dict]:
        """
        Fetch news for a list of symbols + general market news.
        Returns a flat list of news items with sentiment score.
        """
        all_news = []
        
        # 1. Fetch General Market News (Once)
        market_news = self._fetch_rss(self.RSS_URLS["general"], "MARKET")
        all_news.extend(market_news)

        # 2. Fetch specific symbol news (Limit to top 5 holdings to avoid rate limits if needed)
        # For Phase 1, we'll try all, but rely on caching.
        for symbol in symbols:
            # Clean symbol for search (remove .NS)
            search_term = symbol.replace(".NS", "").replace(".BO", "")
            url = self.RSS_URLS["symbol"].format(search_term)
            
            symbol_news = self._fetch_rss(url, symbol)
            all_news.extend(symbol_news)

        return all_news

    def _fetch_rss(self, url: str, asset_tag: str) -> List[Dict]:
        # Check Cache
        now = time.time()
        if url in self.cache:
            if now - self.cache[url]["timestamp"] < self.CACHE_DURATION:
                print(f"DEBUG: Using cached news for {asset_tag}")
                return self.cache[url]["data"]

        try:
            print(f"DEBUG: Fetching RSS for {asset_tag}...")
            feed = feedparser.parse(url)
            items = []
            
            # Process top 3 items per feed to reduce noise
            for entry in feed.entries[:3]:
                # Analyze Sentiment
                analysis = sentiment_service.analyze([entry.title])
                sentiment_score = analysis["sentiment_score"]
                if analysis["sentiment"] == "NEGATIVE":
                    sentiment_score *= -1
                elif analysis["sentiment"] == "NEUTRAL":
                    sentiment_score = 0

                items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", ""),
                    "asset": asset_tag,
                    "sentiment": sentiment_score
                })
            
            # Update Cache
            self.cache[url] = {
                "data": items,
                "timestamp": now
            }
            return items
            
        except Exception as e:
            print(f"ERROR fetching RSS {url}: {e}")
            return []

news_service = NewsService()
