#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROPRIETARY SOFTWARE - STRICTLY CONFIDENTIAL
© 2025 Randy Dev. All Rights Reserved.

This source code is licensed under proprietary terms and may NOT be:
- Copied
- Modified
- Distributed
- Reverse-engineered
- Used as derivative work

Violators will be prosecuted under DMCA § 1201 and applicable copyright laws.

Authorized use only permitted with express written consent from TeamKillerX.
Contact: killerx@randydev.my.id
"""

from datetime import datetime as dt

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
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
