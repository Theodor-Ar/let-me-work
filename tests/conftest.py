from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.survey import Survey
from tests.utils import TEST_USER, TEST_USER_CHAT

TEST_QUESTIONS = [
    "Question 1",
    "Question 2",
    "Question 3",
]


@pytest_asyncio.fixture
async def callback():
    return AsyncMock()


@pytest_asyncio.fixture
async def message():
    return AsyncMock(
        text="Test",
        message_id=123,
    )


@pytest_asyncio.fixture
async def bot():
    return AsyncMock()


@pytest.fixture
def router():
    return Router()


@pytest_asyncio.fixture
async def storage():
    tmp_storage = MemoryStorage()
    try:
        yield tmp_storage
    finally:
        await tmp_storage.close()


@pytest.fixture
def state(storage):
    state = FSMContext(
        storage=storage,
        key=StorageKey(
            bot_id=1,
            chat_id=TEST_USER_CHAT.id,
            user_id=TEST_USER.id,
        ),
    )
    return state


@pytest.fixture
def survey(bot, router):
    survey = Survey(
        bot=bot,
        router=router,
        chat_id=TEST_USER_CHAT.id,
        questions=TEST_QUESTIONS,
    )
    return survey
