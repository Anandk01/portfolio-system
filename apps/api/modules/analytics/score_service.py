from typing import Dict, List, Any
import numpy as np
from core.models import NormalizedHolding, Portfolio
from modules.analytics.service import analytics_engine, sentiment_service

class ScoreService:
    def calculate_health_score(self, portfolio: Portfolio, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates a composite AI Health Score (0-100) for the portfolio.
        Breakdown:
        - Diversification (30 points): Based on HHI
        - Risk Efficiency (30 points): Sharpe Ratio + Volatility
        - Sentiment Outlook (20 points): Weighted news sentiment
        - Portfolio Quality (20 points): Data integrity & asset classification
        """
        if not portfolio.holdings:
            return self._empty_score()

        # 1. Diversification Score (0-30)
        # metrics['diversification_score'] is (1 - HHI), range 0-1
        # We want to map 0.0 -> 0, 1.0 -> 30
        div_raw = metrics.get("diversification_score", 0.0)
        score_div = round(div_raw * 30, 1)

        # 2. Risk Efficiency (0-30)
        # Sharpe (0-15): Target 2.0+ is max points
        sharpe = metrics.get("sharpe_ratio", 0.0)
        score_sharpe = min(max(sharpe, 0) / 2.0, 1.0) * 15
        
        # Volatility (0-15): Target < 15% is max points, > 40% is 0 points
        vol = metrics.get("annual_volatility", 0.0)
        # map 0.15 -> 1.0, 0.40 -> 0.0
        if vol <= 0.15:
            vol_factor = 1.0
        elif vol >= 0.40:
            vol_factor = 0.0
        else:
            vol_factor = 1.0 - ((vol - 0.15) / (0.40 - 0.15))
        
        score_vol = vol_factor * 15
        score_risk = round(score_sharpe + score_vol, 1)

        # 3. Sentiment Outlook (0-20)
        # This requires fetching sentiment for holdings. For now, we simulate or use cached values.
        # In a real flow, this would be pre-calculated by the Intelligence Feed logic.
        # Check if sentiments are attached to holdings (if we add that field later) or fallback.
        # For Phase 1, we will default to Neutral (10/20) if no data, or calculate if enabled.
        score_sentiment = 10.0 # Neutral default

        # 4. Quality Score (0-20)
        # Penalize for "Unknown" assets or missing metadata
        quality_deductions = 0
        total_assets = len(portfolio.holdings)
        
        unknown_sectors = sum(1 for h in portfolio.holdings if h.sector in ["Others", None])
        unknown_types = sum(1 for h in portfolio.holdings if h.asset_type == "UNKNOWN")
        
        # Penalty: -2 for each unknown sector (max -10)
        quality_deductions += min(unknown_sectors * 2, 10)
        # Penalty: -5 for each unknown asset type (max -10)
        quality_deductions += min(unknown_types * 5, 10)
        
        score_quality = max(0, 20 - quality_deductions)

        # Final Sum
        total_score = int(score_div + score_risk + score_sentiment + score_quality)
        
        return {
            "total_score": total_score,
            "grade": self._get_grade(total_score),
            "breakdown": {
                "diversification": score_div,
                "risk": score_risk,
                "sentiment": score_sentiment,
                "quality": score_quality
            },
            "summary": self._generate_summary(score_div, score_risk, score_sentiment, score_quality)
        }

    def _get_grade(self, score: int) -> str:
        if score >= 85: return "A"
        if score >= 70: return "B"
        if score >= 55: return "C"
        if score >= 40: return "D"
        return "F"
        
    def _generate_summary(self, div, risk, sent, qual) -> str:
        strengths = []
        weaknesses = []
        
        if div >= 20: strengths.append("Well Diversified")
        elif div < 10: weaknesses.append("High Concentration")
        
        if risk >= 20: strengths.append("Risk Efficient")
        elif risk < 10: weaknesses.append("Volatile Profile")
        
        if qual < 15: weaknesses.append("Data Quality Issues")
        
        if not strengths and not weaknesses:
            return "Balanced Portfolio"
            
        summary = ""
        if strengths: summary += f"Strengths: {', '.join(strengths)}. "
        if weaknesses: summary += f"Attention needed: {', '.join(weaknesses)}."
        return summary

    def _empty_score(self):
        return {
            "total_score": 0, 
            "grade": "-", 
            "breakdown": {"diversification":0, "risk":0, "sentiment":0, "quality":0},
            "summary": "No assets found."
        }

score_service = ScoreService()
