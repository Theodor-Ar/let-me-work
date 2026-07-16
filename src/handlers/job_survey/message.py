
from aiogram import Router
from aiogram.types import Message as Msg
from aiogram.fsm.context import FSMContext

from src.forms.job_survey import JobSurvey
from src.handlers.job_survey.job_questions import job_servey_questions as questions


router = Router()

@router.message(JobSurvey.active_survey)
async def saving_answer(message: Msg, state: FSMContext):
    if not (message.text and message.text.strip()):
        return

    data = await state.get_data()

    question_index: int = data.get("question_index", 0)
    answers: dict = data.get("answers", {})

    question = questions[question_index]
    answer = message.text

    if question in answers:
        answers[question] += f"\n{answer}"
    else:
        answers.update({question: answer})

    await state.update_data(answers=answers)

    last_user_messages_id: list = data.get("last_user_messages_id", [])
    last_user_messages_id.append(message.message_id)
    await state.update_data(last_user_messages_id=last_user_messages_id)
