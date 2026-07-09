
from aiogram.types import (
    InlineKeyboardMarkup, 
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton
)


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
