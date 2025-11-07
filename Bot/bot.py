import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from .config import settings
from .db import connect_db, close_db
from .handlers import core, trivia, tictactoe, economy

logging.basicConfig(level=logging.INFO if settings.DEBUG else logging.WARNING)
logger = logging.getLogger(__name__)

async def main():
    await connect_db()
    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(core.router)
    dp.include_router(trivia.router)
    dp.include_router(tictactoe.router)
    dp.include_router(economy.router)

    try:
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    finally:
        await close_db()
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
