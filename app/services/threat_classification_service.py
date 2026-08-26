def classify_threats(reasons):

    threats = []

    for reason in reasons:

        if "Location changed" in reason:
            threats.append("Impossible Travel")

        if "Device changed" in reason:
            threats.append("Suspicious Device")

        if "Login hour deviated" in reason:
            threats.append("Off-Hours Access")

    return list(set(threats))