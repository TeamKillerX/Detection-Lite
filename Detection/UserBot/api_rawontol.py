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

from pyrogram import Client
import logging
from Detection import assistant
from . import IGNORE_CHANNEL_DEV_LIST
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from pyrogram.raw.types import (
    UpdateNewMessage,
    UpdatePrivacy,
    UpdateUserName,
    UpdatePinnedMessages,
    PeerUser,
    MessageService,
    PrivacyKeyProfilePhoto,
    PrivacyValueDisallowAll,
    PrivacyValueAllowAll,
    PrivacyKeyChatInvite,
    Username,
    Channel,
    ChatForbidden,
    ChannelForbidden,
)

LOGS = logging.getLogger(__name__)

async def send_log(client, text):
    return await assistant.send_message(
        client.me.id,
        text,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("View User", url=f"tg://openmessage?user_id={client.me.id}")]
            ])
        )

@Client.on_raw_update()
async def check_raw(client: Client, update, users, chats):
    if isinstance(update, UpdatePinnedMessages):
        if not update:
            return
        peer = update.peer
        if isinstance(peer, PeerUser):
            if getattr(update, "pinned", False):
                message_ids = ", ".join(str(msg_id) for msg_id in update.messages)
                return await assistant.send_message(
                    client.me.id,
                    "#PINNED_MESSAGE_PM_ALERT\n\n"
                    f"**User ID:** `{peer.user_id}`\n",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("View User PM", url=f"tg://openmessage?user_id={peer.user_id}&message_id={message_ids}")]
                    ])
                )

    elif isinstance(update, UpdatePrivacy):
        if not update:
            return
        if isinstance(update.key, PrivacyKeyChatInvite):
            for rule in update.rules:
                if isinstance(rule, PrivacyValueDisallowAll):
                    return await send_log(
                        client,
                        "#PRIVACY_CHANGED_ALERT\n\n"
                        "**Reason:** 🔒 Does not allow anyone to accept group invitations."
                    )
                elif isinstance(rule, PrivacyValueAllowAll):
                    return await send_log(
                        client,
                        "#PRIVACY_CHANGED_ALERT\n\n"
                        "**Reason:** ✅ Allows everyone to receive group invitations."
                    )
        elif isinstance(update.key, PrivacyKeyProfilePhoto):
            for rule in update.rules:
                if isinstance(rule, PrivacyValueDisallowAll):
                    return await send_log(
                        client,
                        "#PRIVACY_CHANGED_ALERT\n\n"
                        "**Reason:** 🔒 Does not allow anyone to accept Profile Photo"
                    )
                elif isinstance(rule, PrivacyValueAllowAll):
                    return await send_log(
                        client,
                        "#PRIVACY_CHANGED_ALERT\n\n"
                        "**Reason:** ✅ Allows everyone to receive Profile Photo"
                    )

    elif isinstance(update, UpdateUserName):
        if not update:
            return
        first_name = update.first_name
        user_id = update.user_id
        usernames = update.usernames
        for username in usernames:
            if isinstance(username, Username):
                return await assistant.send_message(
                    client.me.id,
                    "#NAME_CHANGED_ALERT\n\n"
                    f"**First Name:** `{first_name}`\n"
                    f"**User ID:** `{user_id}`\n"
                    f"**Username:** <spoiler>{username.username}</spoiler>\n"
                    f"**Editable:** {username.editable}\n",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("View User", url=f"tg://openmessage?user_id={user_id}")]
                    ])
                )
    elif isinstance(update, UpdateNewMessage):
        message = update.message
        if isinstance(message, MessageService):
            return
        if not message:
            return
        peer = message.peer_id
        if not hasattr(peer, "user_id"):
            return
        user_id = peer.user_id
        if user_id == client.me.id:
            return
        user = users.get(user_id)
        if user and getattr(user, "bot", False):
            return
        return await assistant.send_message(
            client.me.id,
            f"#NEW_MESSAGE_PM_ALERT\n\n"
            f"**User:** `{user_id}`\n"
            f"**Message ID:** {message.id}\n"
            f"**Message:** `{message.message}`\n",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(
                        "View Message",
                        url=f"tg://openmessage?user_id={user_id}&message_id={message.id}"
                    )
                ]]
            )
        )
    for cid, chat in chats.items():
        if isinstance(chat, ChannelForbidden):
            await assistant.send_message(
                client.me.id,
                f"#BANNED_ALERT\n"
                f"**Channel:** {chat.title}\n"
                f"**ID:** `{cid}`\n"
                f"**Access hash:** <spoiler>{chat.access_hash}</spoiler>\n"
                f"**Type:** Channel\n"
                f"**Reason:** Banned from channel",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "View Channel",
                            url=f"https://t.me/c/{cid}/1"
                        )
                    ]]
                )
            )
        elif isinstance(chat, ChatForbidden):
            if cid in IGNORE_CHANNEL_DEV_LIST:
                return
            await assistant.send_message(
                client.me.id,
                f"#BANNED_ALERT\n"
                f"**Chat:** {chat.title}\n"
                f"**ID:** `{cid}`\n"
                f"**Access hash:** <spoiler>{chat.access_hash}</spoiler>\n"
                f"**Type:** Group\n"
                f"**Reason:** Banned from group",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "View Group",
                            url=f"https://t.me/c/{cid}/1"
                        )
                    ]]
                )
            )
        elif isinstance(chat, Channel) and getattr(chat, "left", False):
            if cid in IGNORE_CHANNEL_DEV_LIST:
                return
            await assistant.send_message(
                client.me.id,
                f"#UNBANNED #LEFT_ALERT\n"
                f"**Channel:** {chat.title}\n"
                f"**Date:** {chat.date}\n"
                f"**ID:** `{cid}`\n"
                f"**Username:** <spoiler>{chat.username if chat else None}</spoiler>\n"
                f"**Access hash:** <spoiler>{chat.access_hash}</spoiler>\n",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "View Channel",
                            url=f"https://t.me/c/{cid}/1"
                        )
                    ]]
                )
            )
        elif isinstance(chat, Channel) and getattr(chat, "restricted", False):
            await assistant.send_message(
                client.me.id,
                f"#RESTRICTED_ALERT\n"
                f"**Channel:** {chat.title}\n"
                f"**Date:** {chat.date}\n"
                f"**ID:** `{cid}`\n"
                f"**Username:** <spoiler>{chat.username if chat else None}</spoiler>\n"
                f"**Access hash:** {chat.access_hash}\n",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "View Channel",
                            url=f"https://t.me/c/{cid}/1"
                        )
                    ]]
                )
            )
        elif isinstance(chat, Channel) and getattr(chat, "scam", False):
            await assistant.send_message(
                client.me.id,
                f"#SCAM_ALERT\n"
                f"**Channel:** {chat.title}\n"
                f"**Date:** {chat.date}\n"
                f"**ID:** `{cid}`\n"
                f"**Username:** <spoiler>{chat.username if chat else None}</spoiler>\n"
                f"**Access hash:** {chat.access_hash}\n",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "View Channel",
                            url=f"https://t.me/c/{cid}/1"
                        )
                    ]]
                )
            )
