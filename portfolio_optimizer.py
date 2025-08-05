# portfolio_optimizer.py

import numpy as np
import pandas as pd
import yfinance as yf
import logging

logging.basicConfig(level=logging.INFO)

def fetch_price_data(tickers, period="3mo", interval="1d"):
    price_data = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, period=period, interval=interval, progress=False)
            price_data[ticker] = df["Close"]
        except Exception as e:
            logging.warning(f"⚠️ Could not fetch data for {ticker}: {e}")
    return pd.DataFrame(price_data)

def mean_variance_optimizer(price_df):
    returns = price_df.pct_change().dropna()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    
    weights = np.linalg.inv(cov_matrix).dot(mean_returns)
    weights /= np.sum(weights)
    
    portfolio = dict(zip(price_df.columns, np.round(weights, 3)))
    logging.info(f"📊 Optimized Weights (Mean-Variance): {portfolio}")
    return portfolio

def risk_parity_optimizer(price_df):
    returns = price_df.pct_change().dropna()
    vol = returns.std()
    inv_vol = 1 / vol
    weights = inv_vol / np.sum(inv_vol)
    
    portfolio = dict(zip(price_df.columns, np.round(weights, 3)))
    logging.info(f"⚖️ Risk Parity Weights: {portfolio}")
    return portfolio

def monte_carlo_simulation(price_df, num_simulations=5000):
    returns = price_df.pct_change().dropna()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    
    results = np.zeros((3, num_simulations))
    weights_record = []
    
    for i in range(num_simulations):
        weights = np.random.random(len(price_df.columns))
        weights /= np.sum(weights)
        weights_record.append(weights)
        
        portfolio_return = np.sum(mean_returns * weights)
        portfolio_vol = np.sqrt(weights.T @ cov_matrix @ weights)
        sharpe_ratio = portfolio_return / portfolio_vol
        
        results[0,i] = portfolio_return
        results[1,i] = portfolio_vol
        results[2,i] = sharpe_ratio
    
    max_sharpe_idx = np.argmax(results[2])
    best_weights = weights_record[max_sharpe_idx]
    
    portfolio = dict(zip(price_df.columns, np.round(best_weights, 3)))
    logging.info(f"🎲 Monte Carlo Optimal Weights: {portfolio}")
    return portfolio

def optimize_portfolio(tickers, method="mean_variance"):
    df = fetch_price_data(tickers)
    if df.empty:
        logging.error("❌ No data for optimization.")
        return {}
    
    if method == "mean_variance":
        return mean_variance_optimizer(df)
    elif method == "risk_parity":
        return risk_parity_optimizer(df)
    elif method == "monte_carlo":
        return monte_carlo_simulation(df)
    else:
        logging.error(f"❌ Unknown optimization method: {method}")
        return {}
