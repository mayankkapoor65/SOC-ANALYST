from sklearn.ensemble import IsolationForest
import numpy as np

training_data = np.array([
    [9, 0],
    [10, 0],
    [8, 0],
    [9, 0],
    [10, 0],
    [8, 0]
])

model = IsolationForest(
    contamination=0.2,
    random_state=42
)

model.fit(training_data)


def detect_ai_anomaly(login_hour, location_flag):

    if login_hour < 6 or login_hour > 22 or location_flag == 1:
        return {
            "ai_anomaly": True,
            "ai_score": 90
        }

    return {
        "ai_anomaly": False,
        "ai_score": 10
    }