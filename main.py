"""Точка входа: инициализация бота, запуск поллинга"""

import asyncio
import logging

from aiogram import Bot, Dispatcher

from src.config import settings
from src.handlers import router as main_router

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    dp = Dispatcher()
    dp.include_router(main_router)
    bot = Bot(token=settings.bot_token.get_secret_value())

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical("Polling failed | %s", e, exc_info=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
