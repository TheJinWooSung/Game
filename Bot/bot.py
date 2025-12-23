import asyncio
import logging
import signal

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from .config import settings
from .db import connect_db, close_db
from .handlers import core, trivia, tictactoe, economy


logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING
)
logger = logging.getLogger(__name__)


shutdown_event = asyncio.Event()


def _shutdown():
    shutdown_event.set()


async def main():
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _shutdown)

    logger.info("🚀 Bot starting...")

    await connect_db()
    logger.info("🗄️ Database connected")

    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(core.router)
    dp.include_router(trivia.router)
    dp.include_router(tictactoe.router)
    dp.include_router(economy.router)

    polling = asyncio.create_task(dp.start_polling(bot))
    logger.info("🤖 Bot is running")

    await shutdown_event.wait()

    logger.warning("🛑 Shutdown signal received")

    polling.cancel()

    await close_db()
    logger.info("✅ Database closed")

    await bot.session.close()
    logger.info("👋 Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())