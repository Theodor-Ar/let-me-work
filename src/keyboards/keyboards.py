
from aiogram.types import (
    InlineKeyboardMarkup, 
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton
)

from src.forms.job_survey import JobSurveyBar
from src.phrases.phrases import (
     BACK_BUTTON_TEXT,
     NEXT_BUTTON_TEXT,
     STOP_BUTTON_TEXT,
     DONE_BUTTON_TEXT,
     START_SURVEY_BUTTON_TEXT
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
               [InlineKeyboardButton(text='Начать потбор вакансий', callback_data='job_survey_introduction')],
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
                         text=STOP_BUTTON_TEXT,
                         callback_data=JobSurveyBar(action="stop").pack()
                    ),
                    InlineKeyboardButton(
                         text=NEXT_BUTTON_TEXT,
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
                         text=BACK_BUTTON_TEXT,
                         callback_data=JobSurveyBar(action="prev").pack()
                    ),
                    InlineKeyboardButton(
                         text=STOP_BUTTON_TEXT,
                         callback_data=JobSurveyBar(action="stop").pack()
                    ),
                    InlineKeyboardButton(
                         text=NEXT_BUTTON_TEXT,
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
                         text=BACK_BUTTON_TEXT,
                         callback_data=JobSurveyBar(action="prev").pack()
                    ),
                    InlineKeyboardButton(
                         text=STOP_BUTTON_TEXT,
                         callback_data=JobSurveyBar(action="stop").pack()
                    ),
                    InlineKeyboardButton(
                         text=DONE_BUTTON_TEXT,
                         callback_data=JobSurveyBar(action="done").pack()
                    )
               ]
          ]
     )
     return keyboard

def job_introduction_kb():
     keyboard = InlineKeyboardMarkup(
          inline_keyboard=[
               [
                    InlineKeyboardButton(
                         text=START_SURVEY_BUTTON_TEXT,
                         callback_data="start_job_survey"
                    )
               ]
          ]
     )
     return keyboard