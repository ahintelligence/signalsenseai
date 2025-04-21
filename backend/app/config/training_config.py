import os
import time
from datetime import datetime
from app.model.train import train_model

# Basic retraining scheduler (manual or future cron-compatible)

def auto_retrain(ticker: str, interval_hours: int = 24):
    while True:
        print(f"[{datetime.now().isoformat()}] Retraining model for: {ticker}")
        try:
            train_model(ticker)
        except Exception as e:
            print(f"[!] Error during retrain: {e}")
        print(f"Sleeping for {interval_hours}h...")
        time.sleep(interval_hours * 3600)

if __name__ == "__main__":
    auto_retrain("AAPL", interval_hours=24)
