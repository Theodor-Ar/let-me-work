"""Точка входа: инициализация бота, запуск поллинга"""

from src.config.config import BOT_TOKEN
from src.handlers import router as main_router

from aiogram import Bot, Dispatcher
import asyncio


async def main():
    dp = Dispatcher()
    bot = Bot(token=BOT_TOKEN)
    dp.include_router(main_router)

    try: 
        await dp.start_polling(bot)
    except ValueError as e:
        print(e)
    except KeyError as e:
        print(e)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())