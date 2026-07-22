"""Точка входа: инициализация бота, запуск поллинга"""

from src.config.config import settings
from src.handlers import router as main_router

from aiogram import Bot, Dispatcher
import asyncio


async def main():
    dp = Dispatcher()
    dp.include_router(main_router)
    bot = Bot(token=settings.bot_token.get_secret_value())

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