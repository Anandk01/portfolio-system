from typing import List, Dict
import numpy as np
from core.models import NormalizedHolding

class AIInsightsEngine:
    def __init__(self):
        # In production, load pre-trained RL agents or GPT models here
        pass

    def optimize_portfolio_rl(self, holdings: List[NormalizedHolding]) -> Dict:
        """
        Simulate RL-based portfolio optimization using dynamic heuristic rules.
        """
        if not holdings:
            return {"suggestions": [], "expected_alpha": 0.0}

        total_value = sum(h.current_value for h in holdings)
        if total_value == 0:
            return {"suggestions": [], "expected_alpha": 0.0}

        suggestions = []
        high_risk_exposure = 0.0
        
        for h in holdings:
            weight = h.current_value / total_value
            
            # Rule 1: High Risk Reduction
            if h.risk_category == "HIGH":
                high_risk_exposure += weight
                if weight > 0.15: # Threshold for high risk single asset
                    suggestions.append({
                        "symbol": h.symbol or h.asset_name,
                        "action": "REDUCE",
                        "reason": f"High dominance ({weight:.1%}) of volatile asset",
                        "delta": -0.05
                    })
            
            # Rule 2: Diversification into Stable Assets
            elif h.asset_type == "STOCK" and h.risk_category == "LOW" and weight < 0.05:
                suggestions.append({
                    "symbol": h.symbol or h.asset_name,
                    "action": "INCREASE",
                    "reason": "Under-allocated to stable momentum stock",
                    "delta": 0.05
                })

        # Dynamic Alpha Calculation (Simplified Sharpe Proxy)
        # Base market return 10% + Active management bonus based on risk reduction
        efficiency_score = max(0.0, 1.0 - high_risk_exposure) 
        expected_ret = 0.10 + (efficiency_score * 0.05)
        
        return {
            "suggestions": suggestions[:3], # Top 3 suggestions
            "expected_alpha": round(expected_ret - 0.10, 4), # Alpha over benchmark
            "model_version": "RL-Dynamic-v2.2"
        }

    def generate_explainable_insights(self, performance_data: Dict) -> List[str]:
        """
        Generate dynamic insights based on actual portfolio metrics.
        Includes data quality guards to prevent misleading advice.
        """
        insights = []
        
        volatility = performance_data.get("annual_volatility", 0)
        sharpe = performance_data.get("sharpe_ratio", 0)
        diversification = performance_data.get("diversification_score", 0)
        total_value = performance_data.get("total_value", 0)

        # 1️⃣ DATA QUALITY GUARD
        # If volatility and sharpe are exactly 0 but total value > 0, 
        # it usually means missing historical data, not a "stable" portfolio.
        is_data_sparse = (volatility == 0 and sharpe == 0 and total_value > 0)

        if is_data_sparse:
            insights.append("⚠️ Limited historical data available for performance analysis. Metrics like Volatility and Sharpe are currently estimated at zero.")
            insights.append("Consider adding more recognized Stocks/ETFs to enable deep AI risk analysis.")
        
        # 2️⃣ DIVERSIFICATION
        if diversification < 0.3:
            insights.append("🔴 Critical Concentration Risk: Your portfolio is heavily dependent on 1-2 assets.")
        elif diversification < 0.6:
            insights.append("🟠 Moderate Concentration: Expansion into uncorrelated sectors could improve stability.")
        else:
            insights.append("🟢 Good Diversification: Risk is spread across multiple holdings.")

        # 3️⃣ RISK ADJUSTED RETURNS (Only if data isn't sparse)
        if not is_data_sparse:
            if volatility > 0.25:
                insights.append(f"⚠️ High Volatility detected ({volatility:.1%}). Ensure this matches your risk appetite.")
            
            if sharpe > 1.2:
                insights.append(f"✅ Strong Efficiency: You are receiving good returns for the risk taken.")
            elif sharpe < 0.5:
                insights.append("📉 Inefficient Profile: Consider rebalancing away from low-performing volatile assets.")

        if not insights:
            insights.append("Portfolio is balanced. Continue monitoring quarterly.")
            
        return insights

ai_insights_engine = AIInsightsEngine()
