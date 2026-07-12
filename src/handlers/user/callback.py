
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command as Cmd
from aiogram.types import (
    Message as Msg, 
    CallbackQuery
)

from fluentogram import TranslatorRunner

from src.phrases.job_questions import *
from src.forms.forms import JobForm
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
async def find_job(callback: CallbackQuery, state: FSMContext):
     await callback.message.answer(FIRST_QUESTION)
     await state.set_state(JobForm.first_q)
     
@router.message(JobForm.first_q, F.text)
async def job_first_question(message: Msg, state: FSMContext):
     await state.update_data(first_q=message.text)
     await message.answer(SECOND_QUESTION)
     await state.set_state(JobForm.second_q)

@router.message(JobForm.second_q, F.text)
async def job_second_question(message: Msg, state: FSMContext):
     await state.update_data(second_q=message.text)
     await message.answer(THIRD_QUESTION)
     await state.set_state(JobForm.third_q)

@router.message(JobForm.third_q, F.text)
async def job_thirt_question(message: Msg, state: FSMContext):
     await state.update_data(third_q=message.text)
     await message.answer(FOURTH_QUESTION)
     await state.set_state(JobForm.fourth_q)

@router.message(JobForm.fourth_q, F.text)
async def job_fourth_question(message: Msg, state: FSMContext):
     await state.update_data(fourth_q=message.text)
     await message.answer(FIFTH_QUESTION)
     await state.set_state(JobForm.fifth_q)

@router.message(JobForm.fifth_q, F.text)
async def job_fifth_question(message: Msg, state: FSMContext):
     await state.update_data(fifth_q=message.text)
     
     data = await state.get_data()
     for v in data.values():
          await message.answer(v)

     await state.clear()