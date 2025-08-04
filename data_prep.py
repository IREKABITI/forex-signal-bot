import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "path_to_your_database.db"  # Update with your actual DB file path
OUTPUT_CSV = "ml_training_data.csv"

def fetch_signal_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Example query: adjust columns/tables based on your DB schema
    query = """
    SELECT 
        timestamp,
        asset,
        timeframe,
        technical_score,
        sentiment_score,
        news_score,
        combined_confidence,
        signal_type  -- e.g., Buy/Sell/Hold label for classification
    FROM trading_signals
    WHERE timestamp >= date('now', '-6 months')
    ORDER BY timestamp ASC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def preprocess(df):
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Example: create target column as numerical label (Buy=1, Sell=0, Hold=2)
    df['target'] = df['signal_type'].map({'Buy': 1, 'Sell': 0, 'Hold': 2})

    # Drop rows with missing values
    df = df.dropna()

    # Drop non-feature columns
    df = df.drop(columns=['timestamp', 'asset', 'timeframe', 'signal_type'])

    return df

def save_to_csv(df):
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved prepared data to {OUTPUT_CSV}")

if __name__ == "__main__":
    df_raw = fetch_signal_data()
    df_prepared = preprocess(df_raw)
    save_to_csv(df_prepared)
