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
