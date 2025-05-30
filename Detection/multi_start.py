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

import logging
import asyncio
import pyromod
from Detection import assistant
from database import db
from config import API_ID, API_HASH
from pyrogram import Client

from pyrogram.errors import (
    UserDeactivatedBan,
    AuthKeyDuplicated,
    AuthKeyInvalid,
    UserDeactivated,
    AuthKeyUnregistered,
    SessionRevoked
)
LOGS = logging.getLogger(__name__)

async def start_user() -> None:
    try:
        sessions = await db.users_detection.find({
            "user_client": {
                "$elemMatch": {
                    "is_active": True,
                    "status": "approved"
                }
            }
        }).to_list(length=None)

        if not sessions:
            LOGS.warning("No approved and active user sessions found.")
            return

        active_clients = []

        for i, session_data in enumerate(sessions, 1):
            user_client = session_data.get("user_client", [])
            for user in user_client:
                if not (user.get("status") == "approved" and user.get("is_active")):
                    continue

                session_str = user.get("session_string")
                user_id = user.get("user_id")
                api_id = user.get("api_id", API_ID)
                api_hash = user.get("api_hash", API_HASH)

                if not (session_str and user_id):
                    continue

                try:
                    client = Client(
                        name=f"Detection_{i}_{user_id}",
                        api_id=api_id,
                        api_hash=api_hash,
                        session_string=session_str,
                        plugins=dict(root="Detection.UserBot"),
                        app_version="Detection/latest",
                        device_model="Anonymous",
                        system_version="Linux/Kernel-6.5",
                        sleep_threshold=60
                    )
                    await client.start()
                    me = await client.get_me()
                    if me.id != user_id:
                        raise ValueError(f"Session user_id mismatch (expected {user_id}, got {me.id})")

                    LOGS.info(f"✅ Started User #{i}: Name: {me.first_name}")
                    active_clients.append(client)

                    asyncio.create_task(
                        _check_session_health(client, user_id),
                        name=f"health_monitor_{user_id}"
                    )

                except (
                    UserDeactivatedBan,
                    AuthKeyDuplicated,
                    UserDeactivated,
                    AuthKeyUnregistered,
                    SessionRevoked
                ) as e:
                    await _handle_dead_session(user_id, e)
                    continue

                except Exception as e:
                    LOGS.error(f"⚠️ User #{i} failed: {type(e).__name__}: {str(e)}")
                    continue

    except Exception as err:
        LOGS.error(f"start_user() crashed: {type(err).__name__}: {err}")

async def _handle_dead_session(user_id: int, error: Exception) -> None:
    request = await db.users_detection.find_one({"user_id": user_id})
    if not request:
        return

    for user in request["user_client"]:
        if user.get("user_id") == user_id:
            await db.users_detection.update_one(
                {
                    "_id": request["_id"],
                    "user_client.user_id": user_id
                },
                {
                    "$set": {
                        "user_client.$.is_active": False,
                        "user_client.$.status": "stopped"
                    },
                    "$unset": {
                        "user_client.$.session_string": None
                    }
                }
            )
            break
    await _send_message_warning(
        user_id,
        f"🚨 Session terminated\n"
        f"User: {user_id}\n"
        f"Reason: Error: {type(error).__name__}"
    )
    LOGS.warning(
        f"🚨 Session terminated\n"
        f"User: {user_id}\n"
        f"Reason: {type(error).__name__}"
    )

async def check_connection(client: Client) -> bool:
    try:
        return await client.get_me() is not None
    except:
        return False

async def connection_watchdog(client: Client):
    while True:
        if not await check_connection(client):
            LOGS.warning("Reconnecting...")
            await client.disconnect()
            await client.connect()
        await asyncio.sleep(300)

async def _send_message_warning(user_id, text):
    try:
        await assistant.send_message(user_id, text)
    except:
        pass

async def _check_session_health(client: Client, user_id: int, interval: int = 300) -> None:
    while True:
        try:
            await asyncio.wait_for(client.get_me(), timeout=10)
            
            if not client.is_connected:
                raise ConnectionError("Client disconnected")
                
            LOGS.debug(f"Session health OK: User {user_id}")
            await asyncio.sleep(interval)
            
        except (UserDeactivated, AuthKeyInvalid) as e:
            LOGS.warning(f"💀 Session dead for {user_id}: {type(e).__name__}")
            await _handle_dead_session(user_id, e)
            break
        except Exception as e:
            LOGS.error(f"Health check failed for {user_id}: {type(e).__name__}: {str(e)}")
            await asyncio.sleep(60)
