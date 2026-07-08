"""Точка входа: инициализация бота, запуск поллинга"""

from config.config import BOT_TOKEN
from handlers.routes import router

from aiogram import Bot, Dispatcher
import asyncio


dp = Dispatcher()
dp.include_router(router)

async def main():
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())