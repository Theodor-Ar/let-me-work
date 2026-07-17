
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from src.forms.job_survey import JobSurvey, JobSurveyBar
from src.phrases.phrases import (
    job_servey_questions as questions,
    INTRODUCTION_TEXT
)
from src.keyboards.keyboards import (
    job_stop_next_kb,
    job_prev_stop_next_kb,
    job_prev_stop_done_kb,
    job_introduction_kb
)


router = Router()

async def get_progress_bar(state: FSMContext) -> str:
    data = await state.get_data()
    cur_question_index = data.get("question_index", 0) + 1
    all_questions = len(questions)
    text = f"Вопрос {cur_question_index} из {all_questions}\n\n"
    return text


async def get_keyboard(state: FSMContext):
    data = await state.get_data()
    question_index = data.get("question_index", 0)
    if question_index == 0: return job_stop_next_kb()
    elif question_index == len(questions) - 1: return job_prev_stop_done_kb()
    return job_prev_stop_next_kb()


async def get_cur_question(state: FSMContext) -> str:
    data = await state.get_data()
    question_index = data.get("question_index", 0)
    question = questions[question_index]
    return question


async def get_previous_answer(state: FSMContext) -> str | None:
    data = await state.get_data()
    answers: dict = data.get("answers", {})
    cur_question = await get_cur_question(state)

    if cur_question in answers.keys():
        return answers[cur_question]
    return


async def previous_answer_label(state: FSMContext) -> str:
    previous_answer = await get_previous_answer(state)
    if previous_answer:
        return f"\n\nВаш предыдущий ответ:\n{previous_answer}"
    return ""


async def send_question(
        callback: CallbackQuery,
        state: FSMContext,
        notification: str | None = None
):
    progress_bar = await get_progress_bar(state)
    question = await get_cur_question(state)
    previous_answer = await previous_answer_label(state)

    text = progress_bar + question + previous_answer
    keyboard = await get_keyboard(state)

    await callback.message.answer(
        text=text,
        reply_markup=keyboard
    )
    await callback.answer(notification)


async def delete_messages(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    last_user_messages_id = data.get("last_user_messages_id")

    if last_user_messages_id:
        try:
            for id in last_user_messages_id:
                await callback.bot.delete_message(
                    chat_id=callback.message.chat.id,
                    message_id=id
                )
        except TelegramBadRequest:
            pass
        finally:
            await state.update_data(last_user_messages_id=[])

    await callback.message.delete()

@router.callback_query(F.data == "job_survey_introduction")
async def introduction(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        text=INTRODUCTION_TEXT,
        reply_markup=job_introduction_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "start_job_survey")
async def start_survey(callback: CallbackQuery, state: FSMContext):
    await state.set_state(JobSurvey.active_survey)
    await state.update_data(
        question_index = 0,
        answers = {},
    )
    await delete_messages(callback, state)
    await send_question(callback, state)


@router.callback_query(
        JobSurvey.active_survey,
        JobSurveyBar.filter(F.action == "next")
)
async def next_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    question_index = data.get("question_index", 0)
    answers = data.get("answers")

    if len(answers) <= question_index:
        await callback.answer("Ответ не может быть пустым сообщением", show_alert=True)
        return

    question_index += 1
    await state.update_data(question_index=question_index)
    await delete_messages(callback, state)
    await send_question(callback, state, notification="Ответ сохранён")


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
    await delete_messages(callback, state)
    await send_question(callback, state, notification="Ответ сохранён")


@router.callback_query(
        JobSurvey.active_survey,
        JobSurveyBar.filter(F.action == "done")
)
async def completed_survey(callback: CallbackQuery, state: FSMContext):
    await delete_messages(callback, state)

    data = await state.get_data()
    answers: dict = data.get("answers")
    for question, answer in answers.items():
        await callback.message.answer(f"Вопрос: {question}\nОтвет: \n{answer}")

    await state.clear()
    await callback.answer()
    return

