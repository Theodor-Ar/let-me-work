
from aiogram.fsm.state import State, StatesGroup 
from aiogram import Router


router = Router()

class JobQuestions(StatesGroup):
     first_q = State()
     second_q = State()
     third_q = State()

