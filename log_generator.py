import os
import random
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
LOG_ENDPOINT = f"{API_URL.rstrip('/')}/log"
INTERVAL_SECONDS = float(os.getenv("LOG_INTERVAL", "2"))
MAX_LOGS = int(os.getenv("MAX_LOGS", "0"))  # 0 = run forever

locations = ["India", "USA", "Russia", "China"]
devices = ["Laptop", "Mobile", "Unknown Device"]
users = ["Pragna", "Rahul", "John", "Alice", "David"]


def send_log(payload):
    response = requests.post(LOG_ENDPOINT, json=payload, timeout=10)

    if not response.ok:
        raise RuntimeError(
            f"HTTP {response.status_code}: {response.text[:200] or '(empty body)'}"
        )

    if not response.text.strip():
        raise RuntimeError("Empty response body — is the API running?")

    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"Non-JSON response: {response.text[:200]}"
        ) from exc


def main():
    print(f"Log generator targeting {LOG_ENDPOINT}")
    sent = 0
    errors = 0

    while True:
        payload = {
            "user_id": random.choice(users),
            "event_type": "login",
            "location": random.choice(locations),
            "device": random.choice(devices),
        }

        try:
            data = send_log(payload)
            sent += 1
            print(
                f"[{sent}] Sent: {payload['user_id']} | "
                f"risk={data.get('risk_score')} | "
                f"anomaly={data.get('anomaly_detected')}"
            )
        except requests.ConnectionError:
            errors += 1
            print(
                f"Error: Cannot connect to {API_URL}. "
                "Start the API with: python3 -m uvicorn main:app --host 127.0.0.1 --port 8000"
            )
        except Exception as exc:
            errors += 1
            print(f"Error: {exc}")

        if MAX_LOGS and sent >= MAX_LOGS:
            print(f"\nDone. Sent={sent}, Errors={errors}")
            sys.exit(0 if errors == 0 else 1)

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
