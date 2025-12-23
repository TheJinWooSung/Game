from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

from .config import settings

logger = logging.getLogger(__name__)

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_db() -> AsyncIOMotorDatabase:
    global _client, _db

    if _client is not None and _db is not None:
        return _db

    _client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        maxPoolSize=50,
        minPoolSize=5,
        retryWrites=True,
    )

    _db = _client[settings.DB_NAME]

    await _client.admin.command("ping")

    await _db.players.create_index("user_id", unique=True)
    await _db.games.create_index("game_id", unique=True)
    await _db.leaderboard.create_index(
        [("score", -1), ("updated_at", -1)]
    )

    return _db


async def close_db():
    global _client, _db

    if _client:
        _client.close()
        _client = None
        _db = None


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not connected")
    return _db


def players_collection():
    return get_db().players


def games_collection():
    return get_db().games


def leaderboard_collection():
    return get_db().leaderboard