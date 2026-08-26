#!/usr/bin/env python3
"""
Train Isolation Forest model on historical security logs.

Usage:
    python3 train_model.py

Output:
    models/isolation_forest.pkl
    models/scaler.pkl
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database.database import initialize_database
from app.services.ml_anomaly_service import train_isolation_forest, load_training_data, MODEL_PATH, SCALER_PATH


def main():
    initialize_database()
    print("Loading training data from security_logs...")
    data = load_training_data()
    print(f"Found {len(data)} log records for training.")

    if len(data) < 10:
        print("WARNING: Insufficient data. Need at least 10 records.")
        print("Run log_generator.py to generate more data, then retry.")
        sys.exit(1)

    model = train_isolation_forest(data)
    if model:
        print(f"Model saved to: {MODEL_PATH}")
        print(f"Scaler saved to: {SCALER_PATH}")
        print("Training complete.")
    else:
        print("Training failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
