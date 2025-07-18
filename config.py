from dotenv import load_dotenv
import logging
import os

load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "username": os.getenv("EMAIL_USERNAME"),
    "password": os.getenv("EMAIL_PASSWORD"),
    "use_tls": os.getenv("USE_TLS", "true").lower() == "true",
}

SETTINGS = {
    "api_key": os.getenv("API_KEY"),
    "site_key": os.getenv("SITE_KEY"),
    "site_url": os.getenv("SITE_URL"),
    "directus_url": os.getenv("DIRECTUS_URL"),
}
