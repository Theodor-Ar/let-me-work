
from aiogram.types import (
    InlineKeyboardMarkup, 
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton
)

from src.forms.job_survey import JobSurveyBar


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
               [InlineKeyboardButton(text='Начать потбор вакансий', callback_data='start_job_survey')],
               [InlineKeyboardButton(text='Помощь', callback_data='help')]
          ],
          resize_keyboard=True
     )
     return keyboard

def job_stop_next_kb() -> InlineKeyboardMarkup:
     keyboard = InlineKeyboardMarkup(
          inline_keyboard=[
               [
                    InlineKeyboardButton(
                         text="стоп",
                         callback_data=JobSurveyBar(action="stop").pack()
                    ),
                    InlineKeyboardButton(
                         text="далее",
                         callback_data=JobSurveyBar(action="next").pack()
                    )
               ]
          ]
     )
     return keyboard

def job_prev_stop_next_kb() -> InlineKeyboardMarkup:
     keyboard = InlineKeyboardMarkup(
          inline_keyboard=[
               [
                    InlineKeyboardButton(
                         text="назад",
                         callback_data=JobSurveyBar(action="prev").pack()
                    ),
                    InlineKeyboardButton(
                         text="стоп",
                         callback_data=JobSurveyBar(action="stop").pack()
                    ),
                    InlineKeyboardButton(
                         text="далее",
                         callback_data=JobSurveyBar(action="next").pack()
                    )
               ]
          ]
     )
     return keyboard

def job_prev_stop_done_kb() -> InlineKeyboardMarkup:
     keyboard = InlineKeyboardMarkup(
          inline_keyboard=[
               [
                    InlineKeyboardButton(
                         text="назад",
                         callback_data=JobSurveyBar(action="prev").pack()
                    ),
                    InlineKeyboardButton(
                         text="стоп",
                         callback_data=JobSurveyBar(action="stop").pack()
                    ),
                    InlineKeyboardButton(
                         text="готово",
                         callback_data=JobSurveyBar(action="done").pack()
                    )
               ]
          ]
     )
     return keyboard