import os

from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
BLACKLIST_CHANNEL_NOPOST = [1558215042] # e.g [1558215042, 123456] take another channel
PRIVATE_GROUP_ID = -100 # add bot to your channel/group as admin
OWNER_ID = 0 # your owner ID
