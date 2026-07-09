"""Точка входа: инициализация бота, запуск поллинга"""

from src.config.config import BOT_TOKEN
from src.forms.job_questions import router as user_router
from src.handlers import router as main_router
from src.middlewares.middlewares import TranslateMiddleware

from aiogram import Bot, Dispatcher
import asyncio

from fluentogram import TranslatorHub, FluentTranslator
from fluent_compiler.bundle import FluentBundle


async def main():
    dp = Dispatcher()
    bot = Bot(token=BOT_TOKEN)
    dp.include_router(main_router)

    t_hub = TranslatorHub(
        {
            "ru": ("ru", )
        },
        translators=[
            FluentTranslator(
                "ru",
                translator=FluentBundle.from_files(
                    "ru-RU",
                    filenames=[
                        "src/i18n/ru/text.ftl",
                        "src/i18n/ru/button.ftl"
                    ]
                ),
            )
        ],
        root_locale="ru"
    )
    dp.message.middleware(TranslateMiddleware())
    dp.callback_query.middleware(TranslateMiddleware())

    try: 
        await dp.start_polling(
            bot,
            t_hub=t_hub
        )
    except ValueError as e:
        print(e)
    except KeyError as e:
        print(e)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())