import logging

from motor import motor_asyncio
from motor.core import AgnosticClient

LOGS = logging.getLogger(__name__)

from config import *


class Database:
    def __init__(self, uri: str) -> None:
        self.client: AgnosticClient = motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client["Akeno"]
        self.users_detection = self.db["users_detection"]

    async def connect(self):
        try:
            await self.client.admin.command("ping")
            LOGS.info(f"Database Connection Established!")
        except Exception as e:
            LOGS.info(f"DatabaseErr: {e} ")
            quit(1)

    async def _close(self):
        await self.client.close()

db = Database(MONGO_URI)
