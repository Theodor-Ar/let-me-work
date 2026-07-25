from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..phrases import (
    BACK_BUTTON_TEXT,
    DONE_BUTTON_TEXT,
    NEXT_BUTTON_TEXT,
    START_SURVEY_BUTTON_TEXT,
    STOP_BUTTON_TEXT,
)


def start_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Начать потбор вакансий', callback_data='job_survey'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Создать резюме', callback_data='resume_survey'
                )
            ],
            [InlineKeyboardButton(text='Помощь', callback_data='help')],
        ],
        resize_keyboard=True,
    )
    return keyboard


def survey_intro_kb():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=START_SURVEY_BUTTON_TEXT, callback_data='survey_start'
                )
            ]
        ]
    )
    return keyboard


def survey_start_kb():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=STOP_BUTTON_TEXT, callback_data='survey_stop'
                ),
                InlineKeyboardButton(
                    text=NEXT_BUTTON_TEXT, callback_data='survey_next'
                ),
            ]
        ]
    )
    return keyboard


def survey_base_kb():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=BACK_BUTTON_TEXT, callback_data='survey_back'
                ),
                InlineKeyboardButton(
                    text=STOP_BUTTON_TEXT, callback_data='survey_stop'
                ),
                InlineKeyboardButton(
                    text=NEXT_BUTTON_TEXT, callback_data='survey_next'
                ),
            ]
        ]
    )
    return keyboard


def survey_done_kb():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=BACK_BUTTON_TEXT, callback_data='survey_back'
                ),
                InlineKeyboardButton(
                    text=STOP_BUTTON_TEXT, callback_data='survey_stop'
                ),
                InlineKeyboardButton(
                    text=DONE_BUTTON_TEXT, callback_data='survey_done'
                ),
            ]
        ]
    )
    return keyboard
