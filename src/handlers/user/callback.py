
from aiogram import Router, F
from aiogram.filters import Command as Cmd
from aiogram.types import (
    Message as Msg, 
    CallbackQuery
)

from typing import Callable

from src.phrases.phrases import (
    job_servey_questions,
    resume_survey_questions,
    NOT_WORKONG_FUNC_TEXT
)
from src.keyboards.keyboards import start_keyboard
from src.handlers.survey import Survey


router = Router()

@router.message(Cmd('start'))
async def start(message: Msg):
    first_name = message.from_user.first_name
    start_text = (
        f"Привет, {first_name}!\n\n"
        f"Спасибо, что запустил меня,\n"
        "я помогу тебе с поиском вакансий"
    )
    await message.answer(
         text=start_text,
         reply_markup=start_keyboard()
    )

@router.callback_query(F.data == 'help')
async def help(callback: CallbackQuery):
    help_text = 'Вот доступные функции'
    await callback.message.answer(
        text=help_text, 
    )
    await callback.message.delete()

@router.callback_query(F.data == 'job_survey')
async def job_survey(callback: CallbackQuery):
    job_survey = await create_survey(
        callback,
        job_servey_questions,
        handle_job_answers
    )

async def handle_job_answers(callback: CallbackQuery, answers: dict) -> None:
    await callback.message.answer(text=NOT_WORKONG_FUNC_TEXT)

@router.callback_query(F.data == 'resume_survey')
async def resume_survey(callback: CallbackQuery):
    resume_survey = await create_survey(
        callback,
        resume_survey_questions,
        handle_resume_answers
    )

async def handle_resume_answers(callback: CallbackQuery, answers: dict) -> None:
    await callback.message.answer(text=NOT_WORKONG_FUNC_TEXT)
    # for q, a in answers.items():
    #     await callback.message.answer(f"{q}\n\n{a}")

async def create_survey(callback: CallbackQuery, questions: list, func: Callable) -> dict:
    await callback.message.delete()
    chat_id = callback.message.chat.id
    survey = Survey(
        router=router,
        questions=questions,
        chat_id=chat_id,
        on_complete=func
    )
    await survey.start()

