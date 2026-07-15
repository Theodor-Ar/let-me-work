
from aiogram import Router
from aiogram.types import Message as Msg
from aiogram.fsm.context import FSMContext

from src.forms.job_survey import JobSurvey
from src.handlers.job_survey.job_questions import job_servey_questions as questions


router = Router()

@router.message(JobSurvey.active_survey)
async def saving_answer(message: Msg, state: FSMContext):
    data = await state.get_data()

    question_index: int = data.get("question_index", 0)
    answers: list = data.get("answers", [])

    answers.append(
        {
            "question": questions[question_index],
            "answer": message.text
        }
    )

    await state.update_data(answers=answers)
