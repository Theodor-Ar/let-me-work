
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.forms.job_survey import JobSurvey, JobSurveyBar
from src.handlers.job_survey.job_questions import job_servey_questions as questions
from src.keyboards.keyboards import (
    job_stop_next_kb,
    job_prev_stop_next_kb,
    job_prev_stop_done_kb
)

router = Router()

@router.callback_query(F.data == "start_job_survey")
async def start_survey(callback: CallbackQuery, state: FSMContext):
    await state.set_state(JobSurvey.active_survey)

    await state.update_data(
        question_index = 0,
        answers = [],
    )

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

    keyboard = job_prev_stop_next_kb if question_index < len(questions) - 1 else job_prev_stop_done_kb
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
    data = await state.get_data()
    answers = data.get("answers", [])
    for answer in answers:
        await callback.message.answer(f"Вопрос: {answer['question']}\nОтвет: {answer['answer']}")

    await state.clear()
    await callback.answer()
    return

