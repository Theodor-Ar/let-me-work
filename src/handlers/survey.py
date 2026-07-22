
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State, StatesGroup 
from aiogram.types import (
    Message as Msg, 
    CallbackQuery
)

from src.phrases.phrases import INTRODUCTION_TEXT
from src.config.config import settings
from src.keyboards.keyboards import (
    survey_intro_kb,
    survey_start_kb,
    survey_base_kb,
    survey_done_kb
)


class SurveyFSM(StatesGroup):
    active_survey = State()

class Survey:
    def __init__(self, router: Router, questions: list, chat_id: int, on_complete=None) -> None:
        self.router = router
        self.questions = questions
        self.chat_id = chat_id
        self.bot = Bot(token=settings.bot_token.get_secret_value())
        self.data: dict | None = None 
        self.on_complete = on_complete

        self.__handler()
    
    async def start(self):
        bot = self.bot

        await bot.send_message(
            chat_id=self.chat_id,
            text=INTRODUCTION_TEXT,
            reply_markup=survey_intro_kb()
        )
    
    async def __get_keyboard(self, state: FSMContext):
        data = await state.get_data()
        question_index = data.get("question_index", 0)
        if question_index == 0: return survey_start_kb()
        elif question_index == len(self.questions) - 1: return survey_done_kb()
        return survey_base_kb()
    
    async def __get_cur_question(self, state: FSMContext) -> str:
        data = await state.get_data()
        question_index = data.get("question_index", 0)
        question = self.questions[question_index]
        return question
    
    async def __get_previous_answer(self, state: FSMContext) -> str | None:
        data = await state.get_data()
        answers: dict = data.get("answers", {})
        cur_question = await self.__get_cur_question(state)

        if cur_question in answers.keys():
            return answers[cur_question]
        return
    
    async def __progress_bar(self, state: FSMContext) -> str:
        data = await state.get_data()
        cur_question_index = data.get("question_index", 0) + 1
        all_questions = len(self.questions)
        text = f"Вопрос {cur_question_index} из {all_questions}\n\n"
        return text
    
    async def __previous_answer_label(self, state: FSMContext) -> str:
        previous_answer = await self.__get_previous_answer(state)
        if previous_answer:
            return f"\n\nВаш предыдущий ответ:\n{previous_answer}"
        return ""
    
    async def __send_question(
            self,
            callback: CallbackQuery,
            state: FSMContext,
            notification: str | None = None
    ):
        progress_bar = await self.__progress_bar(state)
        question = await self.__get_cur_question(state)
        previous_answer = await self.__previous_answer_label(state)

        text = progress_bar + question + previous_answer
        keyboard = await self.__get_keyboard(state)

        await callback.message.answer(
            text=text,
            reply_markup=keyboard
        )
        await callback.answer(notification)

    async def __delete_messages(self, callback: CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        last_user_messages_id = data.get("last_user_messages_id")

        if last_user_messages_id:
            try:
                for id in last_user_messages_id:
                    await callback.bot.delete_message(
                        chat_id=callback.message.chat.id,
                        message_id=id
                    )
            except TelegramBadRequest:
                pass
            finally:
                await state.update_data(last_user_messages_id=[])

        await callback.message.delete()
    
    # -- Обработчики --
    
    def __handler(self):
        router = self.router

        @router.callback_query(F.data == "survey_intro")
        async def intro(callback: CallbackQuery, state: FSMContext):
            await callback.message.delete()
            await callback.message.answer(
                text=INTRODUCTION_TEXT,
                reply_markup=survey_intro_kb()
            )
            await callback.answer()
        

        @router.callback_query(F.data == "survey_start")
        async def start(callback: CallbackQuery, state: FSMContext):
            await state.set_state(SurveyFSM.active_survey)
            await state.update_data(
                question_index = 0,
                answers = {},
            )
            await self.__delete_messages(callback, state)
            await self.__send_question(callback, state)


        @router.callback_query(F.data == "survey_next")
        async def next(callback: CallbackQuery, state: FSMContext):
            data = await state.get_data()
            question_index = data.get("question_index", 0)
            answers = data.get("answers")

            if len(answers) <= question_index:
                await callback.answer("Ответ не может быть пустым сообщением", show_alert=True)
                return

            question_index += 1
            await state.update_data(question_index=question_index)
            await self.__delete_messages(callback, state)
            await self.__send_question(callback, state, notification="Ответ сохранён")


        @router.callback_query(F.data == "survey_back")
        async def back(callback: CallbackQuery, state: FSMContext):
            data = await state.get_data()
            question_index = data.get("question_index", 0) - 1

            await state.update_data(question_index=max(0, question_index))
            await self.__delete_messages(callback, state)
            await self.__send_question(callback, state, notification="Ответ сохранён")


        @router.callback_query(F.data == "survey_stop")
        async def stop(callback: CallbackQuery, state: FSMContext):
            await self.__delete_messages(callback, state)
            await state.clear()
            await callback.answer('Опрос остановлен')
            return
        

        @router.callback_query(F.data == "survey_done")
        async def done(callback: CallbackQuery, state: FSMContext):
            await self.__delete_messages(callback, state)
            data = await state.get_data()
            self.data = data
            answers = data.get("answers")
            await state.clear()

            if self.on_complete:
                await self.on_complete(
                    callback=callback,
                    answers=answers
                )
            

        @router.message(SurveyFSM.active_survey)
        async def saving_answer(message: Msg, state: FSMContext):
            if not (message.text and message.text.strip()):
                return

            data = await state.get_data()

            question_index: int = data.get("question_index", 0)
            answers: dict = data.get("answers", {})

            question = self.questions[question_index]
            answer = message.text

            if question in answers:
                answers[question] += f"\n{answer}"
            else:
                answers.update({question: answer})

            await state.update_data(answers=answers)

            last_user_messages_id: list = data.get("last_user_messages_id", [])
            last_user_messages_id.append(message.message_id)
            await state.update_data(last_user_messages_id=last_user_messages_id)

