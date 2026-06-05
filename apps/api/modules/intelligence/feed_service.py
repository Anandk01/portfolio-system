import uuid
from datetime import datetime
from typing import List, Dict
from modules.intelligence.schemas import FeedItem, FeedType, ImpactLevel
from modules.intelligence.news_service import news_service
from modules.market_data.service import market_data_service
from core.models import NormalizedHolding
from modules.analytics.service import analytics_engine

class FeedService:
    
    async def generate_feed(self, portfolio) -> List[FeedItem]:
        """
        Aggregates Price, Sentiment, and Risk signals into a single feed.
        """
        items: List[FeedItem] = []
        holdings = portfolio.holdings
        if not holdings:
            return []

        # 1. Price Signals
        # TODO: Batch fetch current prices to optimize
        for h in holdings:
            if h.asset_type in ["STOCK", "ETF"] and h.symbol:
                try:
                    current_price = market_data_service.get_latest_price(h.symbol)
                    invested_price = (h.invested_value / h.quantity) if h.quantity > 0 else 0
                    
                    if invested_price > 0 and current_price > 0:
                        change_pct = ((current_price - invested_price) / invested_price) * 100
                        
                        # Trigger if huge absolute movement (stub logic - real logic needs daily change)
                        # For Phase 1 demo, we use total pnl > 10% or < -10% as a "Signal" 
                        # OR if we had daily change data.
                        pass 
                except Exception:
                    pass

        # 2. Sentiment Signals (News)
        symbols = [h.symbol for h in holdings if h.symbol]
        news_items = news_service.fetch_news_for_portfolio(symbols)
        
        for news in news_items:
            # Filter distinct/high impact news
            if abs(news["sentiment"]) > 0.5: # Only strong sentiment
                type_ = FeedType.SENTIMENT
                impact_level = ImpactLevel.HIGH if abs(news["sentiment"]) > 0.8 else ImpactLevel.MEDIUM
                
                items.append(FeedItem(
                    id=str(uuid.uuid4()),
                    type=type_,
                    title=news["title"],
                    description=f"Sentiment Analysis: {news['sentiment']:.2f}",
                    asset_symbol=news["asset"],
                    impact_score=abs(news["sentiment"]) * 100,
                    impact_level=impact_level,
                    timestamp=datetime.now(), # In real app use published date
                    url=news["link"],
                    sentiment_score=news["sentiment"]
                ))

        # 3. Risk Signals (Concentration)
        # Check assets > 30% allocation
        total_value = sum(h.current_value for h in holdings)
        if total_value > 0:
            for h in holdings:
                allocation = (h.current_value / total_value) * 100
                if allocation > 30:
                    items.append(FeedItem(
                        id=str(uuid.uuid4()),
                        type=FeedType.RISK,
                        title=f"High Concentration: {h.asset_name}",
                        description=f"This asset makes up {allocation:.1f}% of your portfolio.",
                        asset_symbol=h.symbol,
                        impact_score=80,
                        impact_level=ImpactLevel.HIGH,
                        timestamp=datetime.now()
                    ))

        # 4. Sort by Impact
        items.sort(key=lambda x: x.impact_score, reverse=True)
        return items

feed_service = FeedService()
