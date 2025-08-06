import logging
import yfinance as yf
from assets.eurusd_signal import generate_eurusd_signal_with_score
from assets.usdjpy_signal import generate_usdjpy_signal_with_score
from assets.gold_signal import generate_gold_signal_with_score

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def fetch_data(ticker, period='1mo', interval='1h'):
    """
    Fetch historical market data for a given ticker symbol.
    """
    try:
        data = yf.download(ticker, period=period, interval=interval)
        if data.empty:
            logger.warning(f"No data fetched for {ticker}")
            return None
        return data
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        return None

def run_full_scan():
    """
    Run signal generation for all assets.
    """
    signals = {}

    # EURUSD
    eurusd_data = fetch_data('EURUSD=X')
    if eurusd_data is not None:
        try:
            signals['EURUSD'] = generate_eurusd_signal_with_score(eurusd_data)
            logger.info(f"EURUSD signal: {signals['EURUSD']}")
        except Exception as e:
            logger.error(f"Error generating signal for EURUSD: {e}")

    # USDJPY
    usdjpy_data = fetch_data('JPY=X')
    if usdjpy_data is not None:
        try:
            signals['USDJPY'] = generate_usdjpy_signal_with_score(usdjpy_data)
            logger.info(f"USDJPY signal: {signals['USDJPY']}")
        except Exception as e:
            logger.error(f"Error generating signal for USDJPY: {e}")

    # GOLD
    gold_data = fetch_data('GC=F')
    if gold_data is not None:
        try:
            signals['GOLD'] = generate_gold_signal_with_score(gold_data)
            logger.info(f"GOLD signal: {signals['GOLD']}")
        except Exception as e:
            logger.error(f"Error generating signal for GOLD: {e}")

    return signals
