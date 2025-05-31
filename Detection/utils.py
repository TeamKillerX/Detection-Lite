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

from pyrogram import idle

from database import db

from . import assistant
from .multi_start import start_user


class DetectionManager:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("detection.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        logging.getLogger("pyrogram").setLevel(logging.WARNING)

    async def _start_services(self):
        logging.info("🟡 Starting Detection Manager...")
        await assistant.start()
        logging.info(f"🟢 Assistant {assistant.me.mention} [ID: {assistant.me.id}] started")
        await db.connect()
        logging.info("🟢 Database connection established")
        await start_user()
        logging.info("🟢 All user sessions initialized")

    async def _shutdown(self):
        logging.info("🟡 Shutting down Detection Manager...")
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await assistant.stop()
        logging.info("🟢 All services stopped gracefully")

    async def run(self):
        try:
            await self._start_services()
            await idle()
        except asyncio.CancelledError:
            logging.warning("🟠 Received shutdown signal")
        except Exception as e:
            logging.critical(f"🔴 Fatal error: {e}", exc_info=True)
        finally:
            await self._shutdown()
