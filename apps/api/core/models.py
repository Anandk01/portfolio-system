from datetime import datetime
from typing import List, Optional
from odmantic import Model, EmbeddedModel, Field
from pydantic import field_validator
from enum import Enum

class AssetType(str, Enum):
    STOCK = "STOCK"
    MF = "MF"
    ETF = "ETF"
    COMMODITY = "COMMODITY"
    CASH = "CASH"
    UNKNOWN = "UNKNOWN"

class AccountType(str, Enum):
    DEMAT = "DEMAT"
    SOA = "SOA"
    UNKNOWN = "UNKNOWN"

class AssetClass(str, Enum):
    MUTUAL_FUNDS = "Mutual Funds"
    EQUITY_SHARES = "Equity Shares"
    PREFERENCE_SHARES = "Preference Shares"
    BONDS = "Bonds / Debt"
    GOLD = "Gold"
    NPS = "NPS"
    OTHERS = "Others"

class RiskCategory(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"

class ParsedHolding(EmbeddedModel):
    raw_name: str
    isin: Optional[str] = None
    quantity: float
    invested_value: float

class NormalizedHolding(EmbeddedModel):
    symbol: Optional[str] = None
    isin: Optional[str] = None
    asset_name: str
    asset_type: AssetType
    account_type: AccountType = AccountType.UNKNOWN
    asset_class: AssetClass = AssetClass.EQUITY_SHARES
    sector: Optional[str] = None
    risk_category: RiskCategory = RiskCategory.MODERATE
    quantity: float
    invested_value: float
    current_value: float

    @field_validator('quantity', 'invested_value', 'current_value')
    @classmethod
    def round_financials(cls, v: float) -> float:
        return round(v, 4)

class Portfolio(Model):
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    holdings: List[NormalizedHolding] = Field(default_factory=list)
    
    # Persisted Analytics and Insights
    metrics: Optional[dict] = Field(default=None)
    allocation: Optional[List[dict]] = Field(default=None)
    ai_strategy: Optional[dict] = Field(default=None)
    
    model_config = {
        "collection": "portfolios"
    }

class ParsedPortfolio(Model):
    """Temporary storage for parsed holdings before processing"""
    user_id: str
    holdings: List[NormalizedHolding] = Field(default_factory=list)
    cas_total: float = 0.0  # Total value from CAS header
    extracted_total: float = 0.0  # Sum of extracted holdings
    confidence: float = 0.0  # Parsing confidence score (0-1)
    format_type: str = "UNKNOWN"  # "NSDL", "CDSL", "CAMS", etc.
    status: str = "parsed"  # "parsed", "processing", "completed", "failed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "collection": "parsed_portfolios"
    }

class User(Model):
    email: str = Field(unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    model_config = {
        "collection": "users"
    }
