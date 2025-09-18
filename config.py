# -------------------------------------------------

# -------------------------------------------------
import os

from dotenv import load_dotenv

from utils.database.services.user import get_user_by_tg_id
from utils.schemas.user_db import NamecheapDataForApiSchema, NamecheapDataSchema

load_dotenv()

MODE = 'prod'  # 'dev' or 'prod'

ADMIN_TG_ID = int(os.getenv("ADMIN_TG_ID", "0"))
BOT_TOKEN_DEV = os.getenv("BOT_TOKEN_DEV")
BOT_TOKEN_PROD = os.getenv("BOT_TOKEN_PROD")
CLIENT_IP = os.getenv("CLIENT_IP")

VULTR_API_KEY = os.getenv("VULTR_API_KEY")

BOT_TOKEN = BOT_TOKEN_DEV if MODE == "dev" else BOT_TOKEN_PROD

API_USER_NAMECHEAP = "JmpDigi"
API_KEY_NAMECHEAP = "bd980edee2874294bb25e661c6f078c4"
USERNAME_NAMECHEAP = "JmpDigi"


# -------------------------------------------------

# Namecheap API configuration
NAMECHEAP_CLIENT_IP = os.getenv("NAMECHEAP_CLIENT_IP")

async def get_namecheap_config_data(tg_id: int) -> NamecheapDataForApiSchema | None:
    user_data = await get_user_by_tg_id(tg_id)
    if user_data is None:
        return None
    api_user = user_data.namecheap_api_user
    api_key = user_data.namecheap_api_key
    username = user_data.namecheap_api_user
    return NamecheapDataForApiSchema(
        api_user=api_user,
        api_key=api_key,
        username=username,
        client_ip=CLIENT_IP
    )

# Данные для регистрации домена
FIRST_NAME = os.getenv("FIRST_NAME")
LAST_NAME = os.getenv("LAST_NAME")
ADDRESS1 = os.getenv("ADDRESS1")      
CITY = os.getenv("CITY")
STATE_PROVINCE = os.getenv("STATE_PROVINCE")
POSTAL_CODE = os.getenv("POSTAL_CODE")
COUNTRY = os.getenv("COUNTRY")
PHONE = os.getenv("PHONE")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")


# -------------------------------------------------

HESTIA_USERNAME = os.getenv("HESTIA_USERNAME")
FTP_USERNAME = os.getenv("FTP_USERNAME")

# -------------------------------------------------
# Vultr API configuration

VULTR_API_KEY = os.getenv("VULTR_API_KEY")

OS_ID_FOR_VULTR = 1743  # Ubuntu 22.04 x64
PLAN_FOR_VULTR = "vc2-1c-1gb"  # 1 CPU, 1 GB RAM, 25 GB SSD, 1 TB Bandwidth

# -------------------------------------------------
# Hestia\FTP configuration
EMAIL = os.getenv("EMAIL")  # For Hestia


 # Dynadot API configuration
DYNADOT_API_KEY = os.getenv("DYNADOT_API_KEY")