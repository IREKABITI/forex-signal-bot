import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def fetch_price_data(ticker: str, interval: str = "1h", period: str = "7d") -> pd.DataFrame:
    """
    Fetch price data for a given ticker using yfinance.
    Defaults to 1-hour candles for the past 7 days.
    """
    try:
        logger.info(f"📊 Fetching price data for {ticker} ({interval}, {period})")
        df = yf.download(ticker, interval=interval, period=period)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        logger.error(f"❌ Failed to fetch price data for {ticker}: {e}")
        return pd.DataFrame()

def prepare_ml_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare ML-compatible feature set from price DataFrame.
    Computes common indicators and normalizes.
    """
    try:
        df = df.copy()
        df["returns"] = df["Close"].pct_change()
        df["sma_10"] = df["Close"].rolling(window=10).mean()
        df["sma_50"] = df["Close"].rolling(window=50).mean()
        df["volatility"] = df["Close"].rolling(window=10).std()
        df["momentum"] = df["Close"] - df["Close"].shift(10)
        df.dropna(inplace=True)
        logger.info("✅ ML features prepared.")
        return df
    except Exception as e:
        logger.error(f"❌ Failed to prepare ML features: {e}")
        return pd.DataFrame()
