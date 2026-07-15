
from aiogram.fsm.state import State, StatesGroup 
from aiogram.filters.callback_data import CallbackData


class JobSurvey(StatesGroup):
    active_survey = State()

class JobSurveyBar(CallbackData, prefix="job_survey"):
    action: str
