import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, Any, List

class OptimizationService:
    def optimize_portfolio(self, returns_df: pd.DataFrame, current_weights: Dict[str, float], strategy: str = "aggressive") -> Dict[str, Any]:
        """
        Optimizes portfolio weights using Modern Portfolio Theory (MPT).
        
        Strategies:
        - "aggressive": Maximize Sharpe Ratio
        - "conservative": Minimize Volatility
        """
        if returns_df.empty or len(returns_df.columns) < 2:
            return {"status": "failed", "reason": "Insufficient data"}

        assets = returns_df.columns.tolist()
        num_assets = len(assets)

        # 1. Calculate Annualized Inputs
        # Annualized Mean Returns
        mu = returns_df.mean() * 252
        
        # Annualized Covariance Matrix
        # Regularization for stability: Add 1e-6 to diagonal
        cov = returns_df.cov() * 252
        cov += np.eye(num_assets) * 1e-6

        # 2. Define Objective Functions
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov, weights)))

        def negative_sharpe(weights):
            p_ret = np.dot(weights.T, mu)
            p_vol = portfolio_volatility(weights)
            # Assume 5% risk free rate for consistency
            return -((p_ret - 0.05) / p_vol)

        # 3. Constraints & Bounds
        # Sum of weights = 1
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        # Long only: 0 <= w <= 1
        bounds = tuple((0.0, 1.0) for _ in range(num_assets))

        # 4. Run Optimization
        # Initial Guess: Equal weights
        init_guess = num_assets * [1. / num_assets,]
        
        objective_func = negative_sharpe if strategy == "aggressive" else portfolio_volatility
        
        result = minimize(
            objective_func,
            init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        if not result.success:
            return {"status": "failed", "reason": result.message}

        # 5. Format Output
        optimized_weights = result.x
        
        # Calculate Metrics for New Portfolio
        new_ret = np.dot(optimized_weights.T, mu)
        new_vol = np.sqrt(np.dot(optimized_weights.T, np.dot(cov, optimized_weights)))
        new_sharpe = (new_ret - 0.05) / new_vol

        # Calculate Metrics for Current Portfolio (for comparison)
        curr_vec = np.array([current_weights.get(a, 0) for a in assets])
        # Validate current sum
        if curr_vec.sum() == 0: curr_vec = np.array(init_guess)
        else: curr_vec = curr_vec / curr_vec.sum() # Normalize

        curr_ret = np.dot(curr_vec.T, mu)
        curr_vol = np.sqrt(np.dot(curr_vec.T, np.dot(cov, curr_vec)))
        curr_sharpe = (curr_ret - 0.05) / curr_vol

        weight_map = {assets[i]: round(optimized_weights[i], 3) for i in range(num_assets)}
        
        # Filter out tiny weights
        weight_map = {k: v for k, v in weight_map.items() if v > 0.01}

        return {
            "strategy": strategy,
            "status": "success",
            "weights": weight_map,
            "metrics": {
                "expected_return": round(float(new_ret), 4),
                "volatility": round(float(new_vol), 4),
                "sharpe": round(float(new_sharpe), 2)
            },
            "improvement": {
                "return_delta": round(float(new_ret - curr_ret), 4),
                "volatility_delta": round(float(new_vol - curr_vol), 4),
                "sharpe_delta": round(float(new_sharpe - curr_sharpe), 2)
            }
        }

    def generate_efficient_frontier(self, returns_df: pd.DataFrame, current_weights: Dict[str, float], num_portfolios: int = 1000) -> Dict[str, Any]:
        """
        Generates Efficient Frontier using Monte Carlo simulation.
        Returns cloud of portfolios and key points (Current, Max Sharpe).
        """
        if returns_df.empty or len(returns_df.columns) < 2:
            return {}

        assets = returns_df.columns.tolist()
        num_assets = len(assets)

        # 1. Annualized Inputs
        mu = returns_df.mean() * 252
        cov = returns_df.cov() * 252
        cov += np.eye(num_assets) * 1e-6 # Regularization

        # 2. Monte Carlo Simulation
        cloud = []
        
        # Vectorized generation is faster but loop is clearer for now
        # We can do a small loop or vectorized. Let's do a loop for MVP clarity.
        for _ in range(num_portfolios):
            w = np.random.random(num_assets)
            w /= np.sum(w) # Normalize
            
            p_ret = np.dot(w.T, mu)
            p_vol = np.sqrt(np.dot(w.T, np.dot(cov, w)))
            p_sharpe = (p_ret - 0.05) / p_vol
            
            cloud.append({
                "volatility": round(float(p_vol), 4),
                "return": round(float(p_ret), 4),
                "sharpe": round(float(p_sharpe), 2)
            })

        # 3. Calculate Current Portfolio Point
        curr_vec = np.array([current_weights.get(a, 0) for a in assets])
        if curr_vec.sum() == 0: curr_vec = np.array([1./num_assets]*num_assets)
        else: curr_vec = curr_vec / curr_vec.sum()
        
        curr_ret = np.dot(curr_vec.T, mu)
        curr_vol = np.sqrt(np.dot(curr_vec.T, np.dot(cov, curr_vec)))
        curr_sharpe = (curr_ret - 0.05) / curr_vol
        
        current_point = {
            "volatility": round(float(curr_vol), 4),
            "return": round(float(curr_ret), 4),
            "sharpe": round(float(curr_sharpe), 2)
        }

        # 4. Calculate Max Sharpe Point (Recalculate or reuse if passed, but simpler to recalc here)
        # Reuse optimize logic internally? Or just quick solve.
        # Let's do a quick solve to ensure the star is accurate.
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0.0, 1.0) for _ in range(num_assets))
        init_guess = num_assets * [1. / num_assets,]
        
        def obj(weights):
            p_ret = np.dot(weights.T, mu)
            p_vol = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))
            return -((p_ret - 0.05) / p_vol)
            
        opt_res = minimize(obj, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if opt_res.success:
            w_opt = opt_res.x
            opt_ret = np.dot(w_opt.T, mu)
            opt_vol = np.sqrt(np.dot(w_opt.T, np.dot(cov, w_opt)))
            opt_sharpe = (opt_ret - 0.05) / opt_vol
            
            optimized_point = {
                "volatility": round(float(opt_vol), 4),
                "return": round(float(opt_ret), 4),
                "sharpe": round(float(opt_sharpe), 2)
            }
        else:
            optimized_point = None

        return {
            "cloud": cloud,
            "current": current_point,
            "optimized": optimized_point
        }


optimization_service = OptimizationService()
