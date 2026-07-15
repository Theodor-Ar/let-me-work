
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command as Cmd
from aiogram.types import (
    Message as Msg, 
    CallbackQuery
)

from fluentogram import TranslatorRunner

from src.phrases.phrases import *
from src.keyboards.keyboards import *


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
