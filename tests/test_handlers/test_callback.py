from unittest.mock import AsyncMock, patch

import pytest
from aiogram.types import CallbackQuery, Message

from handlers.user.callback import (
    handle_job_answers,
    handle_resume_answers,
    help,
    job_survey,
    resume_survey,
    start,
)
from keyboards import start_keyboard
from phrases import job_survey_questions, resume_survey_questions


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
async def test_job_survey(mock_create_survey: AsyncMock, callback: CallbackQuery):
    await job_survey(callback)

    mock_create_survey.assert_awaited_once_with(
        callback, job_survey_questions, handle_job_answers
    )


@pytest.mark.asyncio
@patch("handlers.user.callback.create_survey", new_callable=AsyncMock)
async def test_resume_survey(mock_create_survey: AsyncMock, callback: CallbackQuery):
    await resume_survey(callback)

    mock_create_survey.assert_awaited_once_with(
        callback, resume_survey_questions, handle_resume_answers
    )
