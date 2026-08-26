def calculate_confidence(reasons):

    reason_count = len(reasons)

    if reason_count == 0:
        return 0

    if reason_count == 1:
        return 60

    if reason_count == 2:
        return 80

    if reason_count >= 3:
        return 95

    return 50