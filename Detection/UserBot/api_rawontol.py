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

import asyncio
import logging

from pyrogram import Client
from pyrogram.raw.types import (
    Channel,
    ChannelForbidden,
    ChatForbidden,
    MessageService,
    PeerUser,
    PrivacyKeyChatInvite,
    PrivacyKeyProfilePhoto,
    PrivacyValueAllowAll,
    PrivacyValueDisallowAll,
    UpdateNewMessage,
    UpdatePinnedMessages,
    UpdatePrivacy,
    UpdateUserName,
    Username,
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions

from config import BLACKLIST_CHANNEL_NOPOST, ADD_UNBANNED_RAW_BOOL, ADD_BROADCAST_RAW_BOOL
from Detection import assistant

from . import IGNORE_CHANNEL_DEV_LIST

LOGS = logging.getLogger(__name__)

async def send_log(client, text):
    return await assistant.send_message(
        client.me.id,
        text,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
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
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
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
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
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
            link_preview_options=LinkPreviewOptions(is_disabled=True),
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
            if cid in IGNORE_CHANNEL_DEV_LIST:
                return
            return await assistant.send_message(
                client.me.id,
                f"#BANNED_ALERT\n"
                f"**Channel:** {chat.title}\n"
                f"**ID:** `{cid}`\n"
                f"**Access hash:** <spoiler>{chat.access_hash}</spoiler>\n"
                f"**Type:** Channel\n"
                f"**Reason:** Banned from channel",
                link_preview_options=LinkPreviewOptions(is_disabled=True),
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "View Channel",
                            url=f"https://t.me/c/{cid}/-1"
                        )
                    ]]
                )
            )

        elif isinstance(chat, ChatForbidden):
            if cid in IGNORE_CHANNEL_DEV_LIST:
                return
            return await assistant.send_message(
                client.me.id,
                f"#BANNED_ALERT\n"
                f"**Chat:** {chat.title}\n"
                f"**ID:** `{cid}`\n"
                f"**Access hash:** <spoiler>{chat.access_hash}</spoiler>\n"
                f"**Type:** Group\n"
                f"**Reason:** Banned from group",
                link_preview_options=LinkPreviewOptions(is_disabled=True),
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "View Group",
                            url=f"https://t.me/c/{cid}/-1"
                        )
                    ]]
                )
            )

        elif isinstance(chat, Channel) and chat.left:
            if not ADD_UNBANNED_RAW_BOOL:
                return
            if cid in IGNORE_CHANNEL_DEV_LIST:
                return
            await asyncio.sleep(1.5)
            username = f"<spoiler>{chat.username}</spoiler>" if chat.username else "N/A"
            return await assistant.send_message(
                client.me.id,
                f"#UNBANNED #LEFT_ALERT\n"
                f"**Channel:** {chat.title}\n"
                f"**Date:** {chat.date}\n"
                f"**ID:** `{cid}`\n"
                f"**Username:** {username}\n"
                f"**Access hash:** <spoiler>{chat.access_hash}</spoiler>\n",
                link_preview_options=LinkPreviewOptions(is_disabled=True),
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "View Channel",
                            url=f"https://t.me/c/{cid}/-1"
                        )
                    ]]
                )
            )

        elif isinstance(chat, Channel) and chat.restricted:
            username = f"<spoiler>{chat.username}</spoiler>" if chat.username else "N/A"
            return await assistant.send_message(
                client.me.id,
                f"#RESTRICTED_ALERT\n"
                f"**Channel:** {chat.title}\n"
                f"**Date:** {chat.date}\n"
                f"**ID:** `{cid}`\n"
                f"**Username:** {username}\n"
                f"**Access hash:** {chat.access_hash}\n",
                link_preview_options=LinkPreviewOptions(is_disabled=True),
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "View Channel",
                            url=f"https://t.me/c/{cid}/-1"
                        )
                    ]]
                )
            )

        elif isinstance(chat, Channel) and chat.scam:
            username = f"<spoiler>{chat.username}</spoiler>" if chat.username else "N/A"
            return await assistant.send_message(
                client.me.id,
                f"#SCAM_ALERT\n"
                f"**Channel:** {chat.title}\n"
                f"**Date:** {chat.date}\n"
                f"**ID:** `{cid}`\n"
                f"**Username:** {username}\n"
                f"**Access hash:** {chat.access_hash}\n",
                link_preview_options=LinkPreviewOptions(is_disabled=True),
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "View Channel",
                            url=f"https://t.me/c/{cid}/-1"
                        )
                    ]]
                )
            )

        elif isinstance(chat, Channel) and chat.fake:
            username = f"<spoiler>{chat.username}</spoiler>" if chat.username else "N/A"
            return await assistant.send_message(
                client.me.id,
                f"#FAKE_ALERT\n"
                f"**Channel:** {chat.title}\n"
                f"**Date:** {chat.date}\n"
                f"**ID:** `{cid}`\n"
                f"**Username:** {username}\n"
                f"**Access hash:** {chat.access_hash}\n",
                link_preview_options=LinkPreviewOptions(is_disabled=True),
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "View Channel",
                            url=f"https://t.me/c/{cid}/-1"
                        )
                    ]]
                )
            )

        elif isinstance(chat, Channel) and chat.broadcast:
            if not ADD_BROADCAST_RAW_BOOL:
                return
            if cid in BLACKLIST_CHANNEL_NOPOST:
                return
            await asyncio.sleep(1.5)
            username = f"<spoiler>{chat.username}</spoiler>" if chat.username else "N/A"
            return await assistant.send_message(
                client.me.id,
                f"#BROADCAST_ALERT\n"
                f"**Channel:** {chat.title}\n"
                f"**Date:** {chat.date}\n"
                f"**ID:** `{cid}`\n"
                f"**Username:** {username}\n"
                f"**Access hash:** {chat.access_hash}\n",
                link_preview_options=LinkPreviewOptions(is_disabled=True),
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "View Channel",
                            url=f"https://t.me/c/{cid}/-1"
                        )
                    ]]
                )
            )
