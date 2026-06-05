from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum

class FeedType(str, Enum):
    PRICE = "price"
    SENTIMENT = "sentiment"
    RISK = "risk"
    INSIGHT = "insight"

class ImpactLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class FeedItem(BaseModel):
    id: str  # Unique ID for keying
    type: FeedType
    title: str
    description: str
    asset_symbol: Optional[str] = None
    impact_score: float  # 0 to 100 used for sorting
    impact_level: ImpactLevel
    timestamp: datetime
    url: Optional[str] = None  # For news links
    sentiment_score: Optional[float] = None # -1 to 1

class FeedResponse(BaseModel):
    items: List[FeedItem]
    generated_at: datetime
