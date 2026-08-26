def calculate_risk_score(login_hour: int, location: str):

    score = 0

    if login_hour < 6 or login_hour > 22:
        score += 50

    if location not in ["Bangalore", "Mumbai", "Delhi"]:
        score += 30

    return score