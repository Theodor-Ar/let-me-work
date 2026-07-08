
from aiogram import Router, F
from aiogram.filters import Command as Cmd
from aiogram.types import (
    Message as Msg, 
    InlineKeyboardMarkup, 
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    CallbackQuery
)


router = Router()

def back_next_keyboard():
     keyboard = ReplyKeyboardMarkup(
          keyboard=[
               [
                    KeyboardButton(text='назад'), 
                    KeyboardButton(text='выйти'), 
                    KeyboardButton(text='далее')
               ]
          ],
          resize_keyboard=True
     )
     return keyboard

def help_keyboard():   
     keyboard = InlineKeyboardMarkup(
          inline_keyboard=[
               [InlineKeyboardButton(text='Начать потбор вакансий', callback_data='find_job')],
               [InlineKeyboardButton(text='Помощь', callback_data='help')]
          ],
          resize_keyboard=True
     )
     return keyboard

@router.message(Cmd('start'))
async def start(message: Msg):
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