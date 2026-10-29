import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def get_odbc_connection_string():
    setting_names = (
        "DB_DRIVER",
        "DB_SERVER",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    )
    settings = {name: os.getenv(name) for name in setting_names}
    if any(value is None for value in settings.values()):
        return None

    return ";".join(
        (
            f"DRIVER={{{settings['DB_DRIVER']}}}",
            f"SERVER={settings['DB_SERVER']}",
            f"DATABASE={settings['DB_NAME']}",
            f"UID={settings['DB_USER']}",
            f"PWD={settings['DB_PASSWORD']}",
            f"Encrypt={os.getenv('DB_ENCRYPT', 'yes')}",
            "TrustServerCertificate="
            f"{os.getenv('DB_TRUST_SERVER_CERTIFICATE', 'no')}",
        )
    )
