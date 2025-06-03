import os

from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
BLACKLIST_CHANNEL_NOPOST = [1558215042]
ENABLE_UNBANNED_ALERTS = False
ENABLE_BROADCAST_ALERTS = False
SUPPORT_CHANNEL = "RendyProjects"
PRIVATE_GROUP_ID = 0
OWNER_ID = 6477856957
