
from aiogram import Router, F
from aiogram.types import Message as Msg


router = Router()

@router.message(F.text.lower() == 'далее')
async def next(message: Msg):
     await message.answer(
          text='Следующий вопрос'
     )

@router.message(F.text.lower() == 'выйти')
async def exit(message: Msg):
     await message.answer(
          text='Выход'
     )

@router.message(F.text.lower() == 'назад')
async def back(message: Msg):
     await message.answer(
          text='Предыдущий вопрос'
     )