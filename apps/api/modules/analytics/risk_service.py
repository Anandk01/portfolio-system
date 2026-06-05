import numpy as np
import pandas as pd
from typing import List, Dict, Any

class RiskService:
    def calculate_risk_metrics(self, returns_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates Institutional-grade risk metrics.
        Input: DataFrame of Daily Returns (Prices are converted to log returns inside).
        NOTE: Input `returns_df` here is expected to be simple % returns from previous service.
        To be strictly correct for correlation, we should recalculate using Log Returns 
        if we had raw prices. 
        
        However, for correlation, log returns vs simple returns are very similar for daily data.
        We will convert the INPUT simple returns to log returns approximation: r_log = ln(1 + r_simple).
        """
        if returns_df.empty or len(returns_df.columns) < 2:
            return self._empty_risk()

        # 1. Convert Simple Returns to Log Returns for Correlation
        # r_simple = (P_t / P_t-1) - 1  => P_t / P_t-1 = 1 + r_simple
        # r_log = ln(P_t / P_t-1) = ln(1 + r_simple)
        log_returns = np.log1p(returns_df)

        # 2. Correlation Matrix
        corr_matrix = log_returns.corr()
        
        # 3. Average Correlation (Off-diagonal)
        # We need the lower triangle or just all off-diagonal elements
        corr_values = corr_matrix.values
        n = len(corr_values)
        if n > 1:
            off_diag = corr_values[~np.eye(n, dtype=bool)]
            avg_corr = np.nanmean(off_diag)
        else:
            avg_corr = 1.0

        diversification_score = max(0, 1 - avg_corr) # Higher is better

        # 4. Max Drawdown (Global Portfolio Level if weights provided, else per asset)
        # We will calculate "Portfolio Drawdown" assuming the returns_df IS the weighted portfolio return?
        # Actually, returns_df passed here usually contains MULTIPLE assets (for correlation).
        # So we return the matrix, and maybe the drawdown of the *Equal Weighted* version 
        # or just the correlation data for the Heatmap. 
        # Let's return the matrix structure for the UI.
        
        # Structure for Heatmap
        symbols = corr_matrix.columns.tolist()
        matrix_data = []
        for i, row_sym in enumerate(symbols):
            row_data = []
            for j, col_sym in enumerate(symbols):
                row_data.append(round(corr_matrix.iloc[i, j], 2))
            matrix_data.append(row_data)

        return {
            "symbols": symbols,
            "matrix": matrix_data,
            "average_correlation": round(float(avg_corr), 2),
            "diversification_score": round(float(diversification_score), 2)
        }

    def calculate_portfolio_drawdown(self, portfolio_returns: pd.Series) -> Dict[str, Any]:
        """
        Calculates Max Drawdown for the aggregated portfolio returns.
        Input: Series of portfolio daily returns.
        """
        if portfolio_returns.empty:
            return {"max_drawdown": 0.0, "drawdown_series": []}

        # Cumulative Returns (Wealth Index)
        # Start at 1.0
        wealth_index = (1 + portfolio_returns).cumprod()
        
        # Rolling Max
        peak = wealth_index.cummax()
        
        # Drawdown
        drawdown = (wealth_index - peak) / peak
        
        max_drawdown = drawdown.min()
        
        # Format series for chart (last 100 points to save bandwidth)
        series_data = []
        # Downsample if too large? For now just take last year (~252)
        recent_dd = drawdown
        
        for date, val in recent_dd.items():
            series_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "drawdown": round(val * 100, 2) # %
            })
            
        return {
            "max_drawdown": round(float(max_drawdown), 4),
            "drawdown_series": series_data
        }

    def _empty_risk(self):
        return {
            "symbols": [],
            "matrix": [],
            "average_correlation": 0,
            "diversification_score": 0
        }

risk_service = RiskService()
