def generate_security_explanation(threats):

    if not threats:
        return "No suspicious behavior detected."

    return (
        "User activity indicates potential security risks including: "
        + ", ".join(threats)
        + "."
    )