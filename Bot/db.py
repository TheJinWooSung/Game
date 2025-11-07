from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import asyncio
import logging
from .config import settings

logger = logging.getLogger(__name__)

client: Optional[AsyncIOMotorClient] = None
_db = None

async def connect_db():
    global client, _db
    if client is None:
        logger.info("Connecting to MongoDB: %s", settings.MONGODB_URI)
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        _db = client[settings.DB_NAME]
        # Ensure indexes on startup
        await _db.players.create_index("user_id", unique=True)
        await _db.games.create_index("game_id", unique=True)
    return _db

async def close_db():
    global client
    if client:
        logger.info("Closing MongoDB connection")
        client.close()
        client = None

def db():
    if _db is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return _db

# Convenience accessors

def players_collection():
    return db().players

def games_collection():
    return db().games

def leaderboard_collection():
    return db().leaderboard
