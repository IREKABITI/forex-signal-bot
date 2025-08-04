import logging
from signal_generator import generate_signal_with_ml
from alert_manager import send_signal_alert

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_full_scan():
    # Example assets and dummy feature inputs; replace with your actual data fetching logic
    assets = [
        {
            "asset": "EURUSD",
            "technical_score": 0.7,
            "sentiment_score": 0.6,
            "news_score": 0.5,
            "combined_confidence": 0.65,
            "tp": 1.1050,
            "sl": 1.0950,
            "session": "London"
        },
        {
            "asset": "USDJPY",
            "technical_score": 0.8,
            "sentiment_score": 0.7,
            "news_score": 0.6,
            "combined_confidence": 0.75,
            "tp": 145.50,
            "sl": 144.50,
            "session": "NY"
        }
        # Add more assets here as needed
    ]

    logging.info("🔍 Running full signal scan...")

    for asset_data in assets:
        signal = generate_signal_with_ml(asset_data)
        signal_data = {
            "asset": asset_data["asset"],
            "signal": signal["signal"],
            "final_confidence": signal["final_confidence"],
            "ml_confidence": signal["ml_confidence"],
            "base_confidence": signal["base_confidence"],
            "tp": asset_data.get("tp"),
            "sl": asset_data.get("sl"),
            "session": asset_data.get("session")
        }

        if signal_data["final_confidence"] >= 0.5:  # Example threshold to send alerts
            logging.info(f"✅ Sending alert for {signal_data['asset']} with confidence {signal_data['final_confidence']:.2f}")
            send_signal_alert(signal_data)
        else:
            logging.info(f"❌ Signal '{signal_data['asset']}' rejected due to low confidence ({signal_data['final_confidence']:.2f})")

if __name__ == "__main__":
    logging.info("🚀 Forex Signal Bot Started")
    run_full_scan()
