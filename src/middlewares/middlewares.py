
from typing import Any, Awaitable, Callable

from fluentogram import TranslatorHub
from aiogram import BaseMiddleware
from aiogram.types import Update


class TranslateMiddleware(BaseMiddleware):  # pylint: disable=too-few-public-methods
    """
    Fluentogram translation middleware
    """

    async def __call__(
            self,
            handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ) -> Any:
        language = data['user'].language_code if 'user' in data else 'ru'

        hub: TranslatorHub = data.get('t_hub')

        data['locale'] = hub.get_translator_by_locale(language)

        return await handler(event, data)
