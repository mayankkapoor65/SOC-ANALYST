from app.services.digital_twin_service import user_digital_twins


def update_user_baseline(log):

    user_id = log.user_id

    if user_id not in user_digital_twins:

        user_digital_twins[user_id] = {
            "normal_login_hour": log.login_hour,
            "normal_location": log.location,
            "normal_device": log.device
        }

        return

    twin = user_digital_twins[user_id]

    twin["normal_login_hour"] = log.login_hour
    twin["normal_location"] = log.location
    twin["normal_device"] = log.device