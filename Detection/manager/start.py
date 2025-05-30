"""
MIT License

Copyright (c) 2025 Randy Dev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from pyrogram import Client, filters
from datetime import datetime as dt
from pyrogram.types import (
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from config import PRIVATE_GROUP_ID

force_reply = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Create Detection", request_contact=True)],
        [KeyboardButton("Cancel")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

@Client.on_message(
    filters.private
    & filters.regex(r"^Cancel$")
)
async def robot(client: Client, message: Message):
    await message.reply_text(
        "❌ **Cancelled**\n\n"
        "You can start over by sending your contact again.",
        reply_markup=ReplyKeyboardRemove()
    )

@Client.on_message(
    filters.private
    & filters.command("freedeploy")
)
async def show_menu(client, message):
    await client.send_message(
        message.chat.id,
        text="You can deploy your own version of the Auto Detection Lite Bot for free!\n\n",
        reply_markup=force_reply
    )

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    welcome_msg = (
        "👋 **Welcome to Auto Detection Lite Bot**\n\n"
        "🔐 _Your personal guard for detecting silent bans and unbans on Telegram._\n\n"
        "✨ **Features:**\n"
        "• 🔎 Real-time Ban & Unban Detection\n"
        "• 👥 Multi-Account Session Support\n"
        "• 📩 Instant Notifications Without Any Commands\n"
        "• ♾️ Lifetime Free Access\n\n"
        "💡 Use `/freedeploy` to deploy your own version for free!"
    )
    await message.reply_text(
        welcome_msg,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Official Channel", url="https://t.me/RendyProjects")]
        ])
    )

    log_msg = (
        f"📥 **New User Started Bot**\n\n"
        f"👤 User: {message.from_user.mention}\n"
        f"🆔 ID: `{message.from_user.id}`\n"
        f"🕒 Date: `{dt.now().strftime('%Y-%m-%d %H:%M')}`"
    )
    await client.send_message(PRIVATE_GROUP_ID, log_msg)
