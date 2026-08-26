"""
Behavioral Digital Twin Service

Stores baseline behavior for users.
In production this would come from a database.
For Phase 3 we use an in-memory baseline.
"""

user_digital_twins = {
    "user001": {
        "normal_login_hour": 9,
        "normal_location": "Bangalore",
        "normal_device": "Laptop"
    },
    "user002": {
        "normal_login_hour": 10,
        "normal_location": "Mumbai",
        "normal_device": "Desktop"
    }
}