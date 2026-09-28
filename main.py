"""Точка входа: инициализация бота, запуск поллинга"""

import asyncio
import logging

from aiogram import Bot, Dispatcher

from src.config import settings
from src.handlers import router as main_router

logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | [%(levelname)s] %(name)s: %(message)s",
    )


async def main():
    setup_logging()

    dp = Dispatcher()
    dp.include_router(main_router)
    bot = Bot(token=settings.bot_token.get_secret_value())

    try:
        await dp.start_polling(bot)
        logger.info("Starting the bot...")
    except Exception:
        logger.critical("Polling failed | %s", exc_info=True)
        raise
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == '__main__':
    asyncio.run(main())
