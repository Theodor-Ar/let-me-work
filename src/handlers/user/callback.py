import logging
from collections.abc import Callable

from aiogram import F, Router
from aiogram.filters import Command as Cmd
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message as Msg

from handlers.survey import Survey
from keyboards import start_keyboard
from phrases import (
    NOT_WORKING_FUNC_TEXT,
    job_survey_questions,
    resume_survey_questions,
)

router = Router()
logger = logging.getLogger(__name__)


@router.message(Cmd('start'))
async def start(message: Msg):
    first_name = message.from_user.first_name
    start_text = (
        f'Привет, {first_name}!\n\n'
        f'Спасибо, что запустил меня,\n'
        'я помогу тебе с поиском вакансий'
    )
    await message.answer(text=start_text, reply_markup=start_keyboard())
    logger.info("User started the bot | user_id=%s", message.from_user.id)


@router.callback_query(F.data == 'help')
async def help(callback: CallbackQuery):
    help_text = 'Вот доступные функции'
    await callback.message.answer(
        text=help_text,
    )
    await callback.message.delete()


survey = Survey(router=router)


async def handle_job_answers(callback: CallbackQuery, answers: dict) -> None:
    await callback.message.answer(text=NOT_WORKING_FUNC_TEXT)


async def handle_resume_answers(callback: CallbackQuery, answers: dict) -> None:
    await callback.message.answer(text=NOT_WORKING_FUNC_TEXT)


@router.callback_query(F.data == 'job_survey')
async def job_survey(callback: CallbackQuery, state: FSMContext):
    await create_survey(
        callback=callback,
        state=state,
        questions=job_survey_questions,
        survey_type='job_survey',
        func=handle_job_answers,
    )


@router.callback_query(F.data == 'resume_survey')
async def resume_survey(callback: CallbackQuery, state: FSMContext):
    await create_survey(
        callback=callback,
        state=state,
        questions=resume_survey_questions,
        survey_type='resume_survey',
        func=handle_resume_answers,
    )


async def create_survey(
    callback: CallbackQuery,
    state: FSMContext,
    questions: list,
    survey_type: str,
    func: Callable,
    survey: Survey = survey,
) -> dict:
    if survey.bot is None:
        survey.bot = callback.bot
    await callback.message.delete()
    survey.register_completion_handler(survey_type, func)
    await survey.start(
        state=state,
        chat_id=callback.message.chat.id,
        questions=questions,
        survey_type=survey_type,
    )
