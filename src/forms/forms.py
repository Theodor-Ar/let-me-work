
from aiogram.fsm.state import State, StatesGroup 


class JobForm(StatesGroup):
     first_q = State()
     second_q = State()
     third_q = State()
     fourth_q = State()
     fifth_q = State()
