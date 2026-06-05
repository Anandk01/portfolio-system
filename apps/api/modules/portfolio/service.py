from core.database import get_engine
from core.models import Portfolio
import logging

logger = logging.getLogger(__name__)

class PortfolioService:
    async def get_portfolio(self, user_id):
        """
        Fetch portfolio by User ID.
        """
        engine = get_engine()
        portfolio = await engine.find_one(Portfolio, Portfolio.user_id == str(user_id))
        return portfolio

portfolio_service = PortfolioService()
