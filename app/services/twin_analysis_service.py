from app.services.digital_twin_service import user_digital_twins


def analyze_against_twin(log):

    reasons = []

    twin = user_digital_twins.get(log.user_id)

    if not twin:
        return ["No behavioral baseline available"]

    # Location Check
    if log.location != twin["normal_location"]:
        reasons.append(
            f"Location changed from {twin['normal_location']} to {log.location}"
        )

    # Device Check
    if log.device != twin["normal_device"]:
        reasons.append(
            f"Device changed from {twin['normal_device']} to {log.device}"
        )

    # Login Hour Check
    if abs(log.login_hour - twin["normal_login_hour"]) > 2:
        reasons.append(
            f"Login hour deviated from normal behavior ({twin['normal_login_hour']}:00)"
        )

    return reasons