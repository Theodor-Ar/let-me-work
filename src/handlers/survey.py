from collections.abc import Callable

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from config import settings
from keyboards import (
    survey_base_kb,
    survey_done_buttom,
    survey_done_kb,
    survey_intro_kb,
    survey_start_kb,
)
from phrases import INTRODUCTION_TEXT


class SurveyFSM(StatesGroup):
    active_survey = State()


class Survey:
    def __init__(
        self,
        router: Router,
        questions: list,
        chat_id: int,
        bot: Bot | None = None,
        on_complete_func: Callable | None = None,
    ) -> None:
        self.router = router
        self.questions = questions
        self.chat_id = chat_id
        self.bot = bot or Bot(token=settings.bot_token.get_secret_value())
        self.data: dict | None = None
        self.on_complete_func = on_complete_func

        self.__register_handlers__()

    async def start(self):
        await self.bot.send_message(
            chat_id=self.chat_id, text=INTRODUCTION_TEXT, reply_markup=survey_intro_kb()
        )

    def __register_handlers__(self):
        self.router.callback_query.register(
            self._start_button_handler, F.data == 'survey_start'
        )
        self.router.callback_query.register(
            self._next_button_handler, F.data == 'survey_next'
        )
        self.router.callback_query.register(
            self._back_button_handler, F.data == 'survey_back'
        )
        self.router.callback_query.register(
            self._stop_button_handler, F.data == 'survey_stop'
        )
        self.router.callback_query.register(
            self._done_button_handler, F.data == 'survey_done'
        )
        self.router.callback_query.register(
            self._saving_answer, SurveyFSM.active_survey
        )

    async def __send_question__(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        notification: str | None = None,
    ) -> None:
        text = await self._get_question_message_text(state=state)
        keyboard = await self._get_keyboard(state)

        await self.bot.send_message(
            chat_id=callback.message.chat.id, text=text, reply_markup=keyboard
        )
        await callback.answer(notification)

    async def __delete_message__(
        self,
        callback: CallbackQuery | None = None,
        chat_id: int | None = None,
        message_id: int | None = None,
    ) -> None:
        try:
            if callback or (chat_id and message_id):
                await self.bot.delete_message(
                    chat_id=chat_id or callback.message.chat.id,
                    message_id=message_id or callback.message.message_id,
                )
        except TelegramBadRequest:
            pass

    async def __delete_previous_messages__(
        self, callback: CallbackQuery, state: FSMContext
    ) -> None:
        data = await state.get_data()
        last_user_messages_id = data.get('last_user_messages_id')

        if last_user_messages_id:
            for id in last_user_messages_id:
                await self.__delete_message__(callback=callback, message_id=id)
            await state.update_data(last_user_messages_id=[])

        await self.__delete_message__(callback=callback)

    async def _get_question_message_text(self, state: FSMContext) -> str:
        progress_bar = await self._get_progress_bar(state)
        question = await self._get_cur_question(state)
        previous_answer = await self._get_previous_answer_label(state)

        return progress_bar + question + previous_answer

    async def _get_keyboard(self, state: FSMContext):
        data = await state.get_data()
        question_index = data.get('question_index', 0)
        if len(self.questions) == 1:
            return survey_done_buttom()
        elif question_index == 0:
            return survey_start_kb()
        elif question_index == len(self.questions) - 1:
            return survey_done_kb()
        return survey_base_kb()

    async def _get_cur_question(self, state: FSMContext) -> str:
        data = await state.get_data()
        question_index = data.get('question_index', 0)
        question = self.questions[question_index]
        return question

    async def _get_previous_answer(self, state: FSMContext) -> str | None:
        data = await state.get_data()
        answers: dict = data.get('answers', {})
        cur_question = await self._get_cur_question(state)

        if cur_question in answers:
            return answers[cur_question]

    async def _get_progress_bar(self, state: FSMContext) -> str:
        data = await state.get_data()
        cur_question_index = data.get('question_index', 0) + 1
        all_questions = len(self.questions)
        text = f'Вопрос {cur_question_index} из {all_questions}\n\n'
        return text

    async def _get_previous_answer_label(self, state: FSMContext) -> str:
        previous_answer = await self._get_previous_answer(state)
        if previous_answer:
            return f'\n\nВаш предыдущий ответ:\n{previous_answer}'
        return ''

    # -- Обработчики --

    async def _start_button_handler(self, callback: CallbackQuery, state: FSMContext):
        await state.set_state(SurveyFSM.active_survey)
        await state.update_data(
            question_index=0,
            answers={},
        )
        await self.__delete_previous_messages__(callback, state)
        await self.__send_question__(callback, state)

    async def _next_button_handler(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        question_index = data.get('question_index', 0)
        answers = data.get('answers')

        if len(answers) <= question_index:
            await callback.answer(
                text='Ответ не может быть пустым сообщением',
                show_alert=True,
            )
            return

        question_index += 1
        await state.update_data(question_index=question_index)
        await self.__delete_previous_messages__(callback, state)
        await self.__send_question__(callback, state, notification='Ответ сохранён')

    async def _back_button_handler(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        question_index = data.get('question_index', 0) - 1

        await state.update_data(question_index=max(0, question_index))
        await self.__delete_previous_messages__(callback, state)
        await self.__send_question__(callback, state, notification='Ответ сохранён')

    async def _stop_button_handler(self, callback: CallbackQuery, state: FSMContext):
        await self.__delete_previous_messages__(callback, state)
        await state.clear()
        await callback.answer('Опрос остановлен')

    async def _done_button_handler(self, callback: CallbackQuery, state: FSMContext):
        await self.__delete_previous_messages__(callback, state)
        data = await state.get_data()
        self.data = data
        answers = data.get('answers')
        await state.clear()

        if self.on_complete_func:
            await self.on_complete_func(callback=callback, answers=answers)

    async def _saving_answer(self, message: Message, state: FSMContext):
        if not (message.text and message.text.strip()):
            return

        data = await state.get_data()

        question_index: int = data.get('question_index', 0)
        answers: dict = data.get('answers', {})

        question = self.questions[question_index]
        answer = message.text

        if question in answers:
            answers[question] += f'\n{answer}'
        else:
            answers.update({question: answer})

        await state.update_data(answers=answers)

        last_user_messages_id: list = data.get('last_user_messages_id', [])
        last_user_messages_id.append(message.message_id)
        await state.update_data(last_user_messages_id=last_user_messages_id)
