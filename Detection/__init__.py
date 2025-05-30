from pyrogram import Client
import pyromod
from pyromod import listen
from config import API_ID, API_HASH, BOT_TOKEN

assistant = Client(
    "Detection",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=300,
    plugins=dict(root="Detection.manager"),
    sleep_threshold=180
)
