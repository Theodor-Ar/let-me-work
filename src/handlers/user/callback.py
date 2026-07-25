from collections.abc import Callable

from aiogram import F, Router
from aiogram.filters import Command as Cmd
from aiogram.types import CallbackQuery
from aiogram.types import Message as Msg

from ...keyboards import start_keyboard
from ...phrases import (
    NOT_WORKING_FUNC_TEXT,
    job_survey_questions,
    resume_survey_questions,
)
from ..survey import Survey

router = Router()


@router.message(Cmd('start'))
async def start(message: Msg):
    first_name = message.from_user.first_name
    start_text = (
        f'Привет, {first_name}!\n\n'
        f'Спасибо, что запустил меня,\n'
        'я помогу тебе с поиском вакансий'
    )
    await message.answer(text=start_text, reply_markup=start_keyboard())


@router.callback_query(F.data == 'help')
async def help(callback: CallbackQuery):
    help_text = 'Вот доступные функции'
    await callback.message.answer(
        text=help_text,
    )
    await callback.message.delete()


@router.callback_query(F.data == 'job_survey')
async def job_survey(callback: CallbackQuery):
    await create_survey(callback, job_survey_questions, handle_job_answers)


async def handle_job_answers(callback: CallbackQuery, answers: dict) -> None:
    await callback.message.answer(text=NOT_WORKING_FUNC_TEXT)


@router.callback_query(F.data == 'resume_survey')
async def resume_survey(callback: CallbackQuery):
    await create_survey(callback, resume_survey_questions, handle_resume_answers)


async def handle_resume_answers(callback: CallbackQuery, answers: dict) -> None:
    await callback.message.answer(text=NOT_WORKING_FUNC_TEXT)


async def create_survey(
    callback: CallbackQuery, questions: list, func: Callable
) -> dict:
    await callback.message.delete()
    chat_id = callback.message.chat.id
    survey = Survey(
        router=router, questions=questions, chat_id=chat_id, on_complete=func
    )
    await survey.start()
