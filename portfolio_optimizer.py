import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def calculate_portfolio_return(weights, returns):
    return np.sum(weights * returns.mean()) * 252  # Annualized

def calculate_portfolio_volatility(weights, cov_matrix):
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)

def calculate_sharpe_ratio(weights, returns, cov_matrix, risk_free_rate=0.01):
    port_return = calculate_portfolio_return(weights, returns)
    port_volatility = calculate_portfolio_volatility(weights, cov_matrix)
    return (port_return - risk_free_rate) / port_volatility

def optimize_portfolio(returns_df, method='sharpe'):
    """
    Optimize portfolio using specified method: 'sharpe' or 'risk_parity'.
    """
    try:
        num_assets = len(returns_df.columns)
        returns = returns_df.pct_change().dropna()
        cov_matrix = returns.cov()

        if method == 'sharpe':
            from scipy.optimize import minimize

            def neg_sharpe(weights):
                return -calculate_sharpe_ratio(weights, returns, cov_matrix)

            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            bounds = tuple((0, 1) for _ in range(num_assets))
            init_guess = num_assets * [1. / num_assets]

            result = minimize(neg_sharpe, init_guess, method='SLSQP',
                              bounds=bounds, constraints=constraints)

            optimized_weights = result.x
            logger.info("✅ Portfolio optimized using Sharpe ratio.")
            return optimized_weights

        elif method == 'risk_parity':
            inv_vol = 1 / np.sqrt(np.diag(cov_matrix))
            weights = inv_vol / np.sum(inv_vol)
            logger.info("✅ Portfolio optimized using Risk Parity.")
            return weights

    except Exception as e:
        logger.error(f"❌ Portfolio optimization failed: {e}")
        return np.ones(num_assets) / num_assets  # Equal weight fallback

def monte_carlo_simulation(returns_df, num_simulations=5000):
    """
    Run Monte Carlo simulation for portfolio returns.
    """
    try:
        num_assets = len(returns_df.columns)
        results = np.zeros((3, num_simulations))
        returns = returns_df.pct_change().dropna()
        cov_matrix = returns.cov()

        for i in range(num_simulations):
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)

            port_return = calculate_portfolio_return(weights, returns)
            port_volatility = calculate_portfolio_volatility(weights, cov_matrix)
            sharpe_ratio = calculate_sharpe_ratio(weights, returns, cov_matrix)

            results[0, i] = port_return
            results[1, i] = port_volatility
            results[2, i] = sharpe_ratio

        max_sharpe_idx = np.argmax(results[2])
        logger.info("✅ Monte Carlo simulation completed.")
        return {
            'returns': results[0],
            'volatility': results[1],
            'sharpe': results[2],
            'optimal_index': max_sharpe_idx
        }
    except Exception as e:
        logger.error(f"❌ Monte Carlo simulation failed: {e}")
        return None
