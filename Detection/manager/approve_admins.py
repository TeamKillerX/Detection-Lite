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

import logging
from datetime import datetime as dt

from pyrogram import Client, filters
from pyrogram.errors import AuthKeyUnregistered
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import API_HASH, API_ID, OWNER_ID, PRIVATE_GROUP_ID, SUPPORT_CHANNEL
from database import db
from Detection.manager.builder_session import generate_random_string

LOGS = logging.getLogger(__name__)

def initial_client_user(session: str, plugins: str = "UserBot"):
    client_name = generate_random_string(12)
    return Client(
        "{}".format(client_name),
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=session,
        plugins={"root": f"Detection.{plugins}"}
    )

@Client.on_callback_query(filters.regex(r"^statusub_(\d+)$"))
async def check_request(bot: Client, cb: CallbackQuery):
    user_id = int(cb.matches[0].group(1))
    request = await db.users_detection.find_one({"user_id": user_id})
    if not request:
        await cb.answer("No active requests found", show_alert=True)
        return

    status_icon = (
        "🟢"
        if request["user_client"][0]["status"] == "approved"
        else "🔴"
        if request["user_client"][0]["status"] == "rejected"
        else "⚠️"
        if request["user_client"][0]["status"] == "stopped"
        else "🟡"
    )
    await cb.answer(
        f"Request Status: {status_icon} {request['user_client'][0]['status'].capitalize()}\n"
        f"Submitted: {request['user_client'][0].get('timestamp', 'Not available')}\n",
        show_alert=True
    )

@Client.on_callback_query(filters.regex(r"^(rejected_ub|pending_ub|approved_ub)_(\d+)$"))
async def admins_callback(client: Client, callback: CallbackQuery):
    try:
        action, user_id = callback.matches[0].groups()
        action_type = action.split('_')[0]
        admin_id = callback.from_user.id
        admin_mention = callback.from_user.mention
        if admin_id != OWNER_ID:
            return await callback.answer("❌ Only Developer", show_alert=True)
        request = await db.users_detection.find_one({"user_id": int(user_id)})
        if not request:
            await callback.answer("❌ User request not found!", show_alert=True)
            await callback.message.edit_text(f"{callback.message.text}\n\n⚠️ Failed: Request not found")
            return

        if action_type == "rejected":
            await callback.answer("❌ Update failed", show_alert=True)
            return

        if action_type == "approved":
            await handle_approvalub(client, callback, request, user_id, admin_id, admin_mention)

        status_icon = {
            "approved": "✅",
            "rejected": "❌",
            "pending": "🕒"
        }.get(action_type, "ℹ️")

        await callback.message.edit_text(
            f"{callback.message.text}\n\n"
            f"{status_icon} Status: {action_type.capitalize()}ed by {admin_mention}\n"
            f"⏰ {dt.now().strftime('%Y-%m-%d %H:%M:%S')}",
            reply_markup=None
        )
        await callback.answer(f"Request {action_type}d successfully!")

    except Exception as e:
        LOGS.error(f"Admin action error: {str(e)}")
        await handle_errorub(client, callback, e, action, admin_mention)

async def handle_approvalub(client, callback, request, user_id, admin_id, admin_mention):
    try:
        string_session = request["user_client"][0]["session_string"]
        user_bots = initial_client_user(string_session)
        try:
            await user_bots.start()
            bot_user = await user_bots.get_me()
        except AuthKeyUnregistered as e:
            await client.send_message(
                PRIVATE_GROUP_ID,
                f"Error reason: AuthKeyUnregistered `{user_id}`"
            )
            await client.send_message(user_id, "Error reason: AuthKeyUnregistered")
            return
        except Exception as e:
            LOGS.error(f"Error handle_approvalub: {str(e)}")
            await client.send_message(
                user_id,
                "⚠️ Userbot approval failed due to technical reasons.\n"
                "Our team has been notified. Please try again later."
            )
            return
        await db.users_detection.update_one(
            {"_id": request["_id"]},
            {
                "$set": {
                    "user_client.$[target].user_id": bot_user.id,
                    "user_client.$[target].status": "approved",
                    "user_client.$[target].is_active": True,
                    "user_client.$[target].username": bot_user.username or "N/A",
                    "user_client.$[target].started_at": dt.now().isoformat(),
                    "user_client.$[target].admin_action": {
                        "by": admin_id,
                        "at": dt.now().isoformat()
                    }
                }
            },
            array_filters=[{"target.user_id": int(user_id)}]
        )
        await notify_userub(client, user_id, bot_user)
        await client.send_message(
            PRIVATE_GROUP_ID,
            f"✅ Approved Successfully\n\n"
            f"👤 User: {request.get('username', 'N/A')} ({user_id})\n"
            f"⭐ Username: {bot_user.username}\n"
            f"🛠 Approved by: {admin_mention}\n"
            f"⏰ Time: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    except Exception as e:
        LOGS.error(f"Approval error: {str(e)}")

async def handle_errorub(client, callback, error, action, admin_mention):
    await callback.answer("⚠️ Error", show_alert=True)
    await callback.message.edit_text(
        f"{callback.message.text}\n\n❌ Error: {str(error)}"
    )
    await client.send_message(
        PRIVATE_GROUP_ID,
        f"🚨 Admin Action Error\n\n"
        f"Action: {action}\n"
        f"Admin: {admin_mention}\n"
        f"Error: {str(error)}"
    )

async def notify_userub(client, user_id, bot_user):
    caption = (
        "**Your Detection Has Been Approved!**\n\n"
        f"Name: {bot_user.first_name}\n"
        f"Username: @{bot_user.username or 'N/A'}\n"
        f"User ID: `{bot_user.id}`\n\n"

    )
    await client.send_photo(
        user_id,
        photo="https://telegra.ph//file/586a3867c3e16ca6bb4fa.jpg",
        caption=caption,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Channel", url=f"https://t.me/{SUPPORT_CHANNEL}")]
        ])
    )
