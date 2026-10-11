import os

from dotenv import load_dotenv


load_dotenv(override=True)


class Settings:

    PROJECT_NAME = "Network Monitoring and Visualization System"
    DEVICE_MONITOR_INTERVAL = int(os.getenv("DEVICE_MONITOR_INTERVAL", "30"))

    SECRET_KEY = os.getenv(
        "NMVS_SECRET_KEY",
        "change-this-secret-key"
    )

    ALGORITHM = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES = 60

    SMTP_HOST = os.getenv(
        "SMTP_HOST",
        "smtp.gmail.com"
    )

    SMTP_PORT = int(
        os.getenv("SMTP_PORT", "587")
    )

    @property
    def SMTP_USERNAME(self) -> str:
        load_dotenv(override=True)
        return os.getenv("SMTP_USERNAME", "nmvs2027@gmail.com").strip()

    @property
    def SMTP_PASSWORD(self) -> str:
        load_dotenv(override=True)
        return os.getenv("SMTP_PASSWORD", "").replace(" ", "").strip()

    @property
    def SMTP_FROM_EMAIL(self) -> str:
        load_dotenv(override=True)
        return os.getenv("SMTP_FROM_EMAIL", "nmvs2027@gmail.com").strip()


settings = Settings()