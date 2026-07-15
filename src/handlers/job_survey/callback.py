
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from src.forms.job_survey import JobSurvey, JobSurveyBar
from src.handlers.job_survey.job_questions import job_servey_questions as questions
from src.keyboards.keyboards import (
    job_stop_next_kb,
    job_prev_stop_next_kb,
    job_prev_stop_done_kb
)

router = Router()

async def delete_messages(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    last_user_message_id = data.get("last_user_message_id")

    if last_user_message_id is not None:
        try:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=last_user_message_id
            )
        except TelegramBadRequest:
            pass
        finally:
            await state.update_data(last_user_message_id=None)

    await callback.message.delete()


@router.callback_query(F.data == "start_job_survey")
async def start_survey(callback: CallbackQuery, state: FSMContext):
    await state.set_state(JobSurvey.active_survey)

    await state.update_data(
        question_index = 0,
        answers = [],
    )

    await delete_messages(callback, state)
    
    await callback.message.answer(
        text=questions[0],
        reply_markup=job_stop_next_kb()
    )
    await callback.answer("Ответ сохранён")


@router.callback_query(
        JobSurvey.active_survey,
        JobSurveyBar.filter(F.action == "next")
)
async def next_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    question_index = data.get("question_index", 0) + 1
    await state.update_data(question_index=question_index)

    keyboard = job_prev_stop_next_kb if question_index < len(questions) - 1 else job_prev_stop_done_kb
    
    await delete_messages(callback, state)

    await callback.message.answer(
        text=questions[question_index],
        reply_markup=keyboard()
    )
    await callback.answer("Ответ сохранён")


@router.callback_query(
        JobSurvey.active_survey,
        JobSurveyBar.filter(F.action == "stop")
)
async def stop_survey(callback: CallbackQuery, state: FSMContext):
    await delete_messages(callback, state)
    await state.clear()
    await callback.answer('Опрос завершён')
    return


@router.callback_query(
        JobSurvey.active_survey,
        JobSurveyBar.filter(F.action == "prev")
)
async def previous_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    question_index = data.get("question_index", 0) - 1
    await state.update_data(question_index=question_index)

    keyboard = job_stop_next_kb if question_index == 0 else job_prev_stop_next_kb
    
    await delete_messages(callback, state)
    
    await callback.message.answer(
        text=questions[question_index],
        reply_markup=keyboard()
    )
    await callback.answer("Ответ сохранён")


@router.callback_query(
        JobSurvey.active_survey,
        JobSurveyBar.filter(F.action == "done")
)
async def completed_survey(callback: CallbackQuery, state: FSMContext):
    await delete_messages(callback, state)

    data = await state.get_data()
    answers = data.get("answers", [])
    for answer in answers:
        await callback.message.answer(f"Вопрос: {answer['question']}\nОтвет: \n{answer['answer']}")

    await state.clear()
    await callback.answer()
    return

