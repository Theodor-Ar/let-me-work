from unittest.mock import AsyncMock, Mock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from handlers.survey import Survey
from handlers.user.callback import (
    create_survey,
    handle_job_answers,
    handle_resume_answers,
    help,
    job_survey,
    resume_survey,
    start,
)
from keyboards import start_keyboard
from phrases import job_survey_questions, resume_survey_questions
from tests.conftest import TEST_QUESTIONS


@pytest.mark.asyncio
async def test_start_handler(message: Message):
    message.from_user.first_name = "TestUserName"
    first_name = message.from_user.first_name
    start_text = (
        f'Привет, {first_name}!\n\n'
        f'Спасибо, что запустил меня,\n'
        'я помогу тебе с поиском вакансий'
    )

    await start(message)

    message.answer.assert_awaited_once_with(
        text=start_text, reply_markup=start_keyboard()
    )


@pytest.mark.asyncio
async def test_help_handler(callback: CallbackQuery):
    callback.data = "help"
    help_text = 'Вот доступные функции'

    await help(callback)

    callback.message.answer.assert_awaited_once_with(text=help_text)
    callback.message.delete.assert_awaited_once()


@pytest.mark.asyncio
@patch("handlers.user.callback.create_survey", new_callable=AsyncMock)
async def test_job_survey(
    mock_create_survey: AsyncMock, callback: CallbackQuery, state: FSMContext
):
    await job_survey(callback, state)

    mock_create_survey.assert_awaited_once_with(
        callback=callback,
        state=state,
        questions=job_survey_questions,
        survey_type='job_survey',
        func=handle_job_answers,
    )


@pytest.mark.asyncio
@patch("handlers.user.callback.create_survey", new_callable=AsyncMock)
async def test_resume_survey(
    mock_create_survey: AsyncMock, callback: CallbackQuery, state: FSMContext
):
    await resume_survey(callback, state)

    mock_create_survey.assert_awaited_once_with(
        callback=callback,
        state=state,
        questions=resume_survey_questions,
        survey_type='resume_survey',
        func=handle_resume_answers,
    )


@pytest.mark.asyncio
async def test_create_survey(
    callback: CallbackQuery,
    survey: Survey,
    state: FSMContext,
) -> dict:
    callback.message.delete = AsyncMock()
    survey.register_completion_handler = Mock()
    survey.start = AsyncMock()
    func = AsyncMock()
    survey.bot = None

    await create_survey(
        callback=callback,
        state=state,
        questions=TEST_QUESTIONS,
        survey_type='TEST',
        func=func,
        survey=survey,
    )

    assert survey.bot is not None
    callback.message.delete.assert_awaited_once()
    survey.register_completion_handler.assert_called_once_with('TEST', func)
    survey.start.assert_awaited_once_with(
        state=state,
        chat_id=callback.message.chat.id,
        questions=TEST_QUESTIONS,
        survey_type='TEST',
    )
