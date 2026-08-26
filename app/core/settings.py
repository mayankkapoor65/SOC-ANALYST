import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = os.getenv(
        "PROJECT_NAME", "Security Log Anomaly Detection System"
    )
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")
    DB_NAME: str = os.getenv("DB_NAME", "security_logs.db")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

    # JWT / Auth (Phase 12)
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "change-me-in-production-use-openssl-rand-hex-32"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    AUTH_REQUIRED: bool = os.getenv("AUTH_REQUIRED", "false").lower() == "true"

    # Bootstrap admin (Phase 12.1 — prefer ADMIN_* env vars)
    ADMIN_USERNAME: str = os.getenv(
        "ADMIN_USERNAME",
        os.getenv("DEFAULT_ADMIN_USERNAME", "admin"),
    )
    ADMIN_EMAIL: str = os.getenv(
        "ADMIN_EMAIL",
        os.getenv("DEFAULT_ADMIN_EMAIL", "admin@sentinelai.local"),
    )
    ADMIN_PASSWORD: str = os.getenv(
        "ADMIN_PASSWORD",
        os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin123!"),
    )

    # Threat Intelligence (Phase 13)
    THREAT_FEED_TYPE: str = os.getenv("THREAT_FEED_TYPE", "json")
    THREAT_FEED_PATH: str = os.getenv("THREAT_FEED_PATH", "")


settings = Settings()
