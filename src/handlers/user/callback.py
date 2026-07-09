
from aiogram import Router
from aiogram.filters import Command as Cmd
from aiogram.types import (
    Message as Msg, 
    CallbackQuery
)

from fluentogram import TranslatorRunner

from src.keyboards.keyboards import (
     back_next_keyboard,
     help_keyboard
)


router = Router()

@router.message(Cmd('start'))
async def start(message: Msg, locale: TranslatorRunner):
    first_name = message.from_user.first_name
    start_text = (
        f"Привет, {first_name}!\n\n"
        f"Спасибо, что запустил меня,\n"
        "я помогу тебе с поиском вакансий"
    )
    await message.answer(
         text=start_text,
         reply_markup=help_keyboard()
    )

@router.callback_query(lambda c: c.data == 'help')
async def help(callback: CallbackQuery):
     help_text = 'Вот доступные функции'
     await callback.message.answer(
        text=help_text, 
        reply_markup=back_next_keyboard()
     )
     await callback.message.delete()

@router.callback_query(lambda c: c.data == 'find_job')
async def find_job(callback: CallbackQuery):
     await callback.message.answer(
        text='Вам будет необходимо ответить на несколько вопросов', 
        reply_markup=back_next_keyboard()
     )
     await callback.message.delete()