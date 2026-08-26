import logging

from app.core.settings import settings

logger = logging.getLogger(__name__)

INSECURE_JWT_SECRETS = {
    "change-me-in-production-use-openssl-rand-hex-32",
    "secret",
    "dev",
}

INSECURE_ADMIN_PASSWORDS = {
    "Admin123!",
    "admin123!",
    "password",
    "admin",
}


def validate_security_config():
    """
    Enforce secure defaults when AUTH_REQUIRED=true.
    Warn (but allow) insecure defaults in development mode.
    """
    if settings.AUTH_REQUIRED:
        if settings.JWT_SECRET_KEY in INSECURE_JWT_SECRETS or settings.JWT_SECRET_KEY.startswith("change-me"):
            raise RuntimeError(
                "Refusing to start: JWT_SECRET_KEY is insecure. "
                "Set a strong random secret when AUTH_REQUIRED=true."
            )
        if settings.ADMIN_PASSWORD in INSECURE_ADMIN_PASSWORDS:
            raise RuntimeError(
                "Refusing to start: ADMIN_PASSWORD is a known insecure default. "
                "Set a strong password when AUTH_REQUIRED=true."
            )
    else:
        if settings.ADMIN_PASSWORD in INSECURE_ADMIN_PASSWORDS:
            logger.warning(
                "ADMIN_PASSWORD is a known default for user '%s'. Change before production.",
                settings.ADMIN_USERNAME,
            )
        if settings.JWT_SECRET_KEY in INSECURE_JWT_SECRETS or settings.JWT_SECRET_KEY.startswith("change-me"):
            logger.warning(
                "JWT_SECRET_KEY is a placeholder. Change before enabling AUTH_REQUIRED=true."
            )


def warn_if_default_admin_active():
    """Log a warning if the bootstrap admin still uses a known default password."""
    from app.auth.password import verify_password
    from app.auth.user_service import get_user_by_username

    if settings.ADMIN_PASSWORD not in INSECURE_ADMIN_PASSWORDS:
        return

    user = get_user_by_username(settings.ADMIN_USERNAME)
    if not user:
        return

    if verify_password(settings.ADMIN_PASSWORD, user["password_hash"]):
        logger.warning(
            "Default admin password still active for user '%s'. Rotate credentials.",
            settings.ADMIN_USERNAME,
        )
