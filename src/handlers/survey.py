import logging
from collections.abc import Callable

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from keyboards import (
    survey_base_kb,
    survey_done_button,
    survey_done_kb,
    survey_intro_kb,
    survey_start_kb,
)
from phrases import INTRODUCTION_TEXT

logger = logging.getLogger(__name__)


class SurveyFSM(StatesGroup):
    active_survey = State()


class Survey:
    def __init__(
        self,
        router: Router,
        bot: Bot | None = None,
        on_complete_func: Callable | None = None,
    ) -> None:
        self.router = router
        self.bot = bot
        self.on_complete_func = on_complete_func
        self._completion_handlers: dict[str, Callable] = {}

        self.__register_handlers__(router=router)

    def register_completion_handler(self, survey_type: str, func: Callable) -> None:
        self._completion_handlers[survey_type] = func

    async def start(
        self,
        state: FSMContext,
        questions: list[str],
        chat_id: int,
        survey_type: str | None = None,
    ) -> None:
        await self.__init_state__(
            state=state, questions=questions, survey_type=survey_type
        )
        await self.bot.send_message(
            chat_id=chat_id, text=INTRODUCTION_TEXT, reply_markup=survey_intro_kb()
        )
        logger.info("Survey has been launched.")

    def __register_handlers__(self, router: Router) -> None:
        router.callback_query.register(
            self._start_button_handler, F.data == 'survey_start'
        )
        logger.debug("The survey_start handler was registered in the router.")
        router.callback_query.register(
            self._next_button_handler, F.data == 'survey_next'
        )
        logger.debug("The survey_next handler was registered in the router.")
        router.callback_query.register(
            self._back_button_handler, F.data == 'survey_back'
        )
        logger.debug("The survey_back handler was registered in the router.")
        router.callback_query.register(
            self._stop_button_handler, F.data == 'survey_stop'
        )
        logger.debug("The survey_stop handler was registered in the router.")
        router.callback_query.register(
            self._done_button_handler, F.data == 'survey_done'
        )
        logger.debug("The survey_done handler was registered in the router.")
        router.message.register(self._saving_answer, SurveyFSM.active_survey, F.text)
        logger.debug("The answer-saving function was registered in the router.")

    async def __init_state__(
        self,
        state: FSMContext,
        questions: list[str],
        survey_type: str | None = None,
    ) -> None:
        await state.update_data(
            questions=questions,
            question_index=0,
            answers={},
            user_last_messages_ids=[],
            survey_type=survey_type,
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
        logger.info("Message sent to chat %s", callback.message.chat.id)

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
                logger.info(
                    "Message %s in chat %s was deleted.",
                    message_id or callback.message.message_id,
                    chat_id or callback.message.chat.id,
                )
        except TelegramBadRequest:
            logger.exception("Failed to delete the message.")

    async def __delete_previous_messages__(
        self, callback: CallbackQuery, state: FSMContext
    ) -> None:
        user_last_messages_ids = await self._get_user_last_messages_ids(state=state)

        if user_last_messages_ids:
            for id in user_last_messages_ids:
                await self.__delete_message__(callback=callback, message_id=id)
            await state.update_data(user_last_messages_ids=[])
            logger.debug("The list of sent message IDs has been cleared.")

        await self.__delete_message__(callback=callback)

    async def _get_questions(self, state: FSMContext) -> list[str]:
        data = await state.get_data()
        return data.get('questions', [])

    async def _get_answers(self, state: FSMContext) -> dict:
        data = await state.get_data()
        return data.get('answers', {})

    async def _get_question_index(self, state: FSMContext) -> int:
        data = await state.get_data()
        return data.get('question_index', 0)

    async def _get_user_last_messages_ids(self, state: FSMContext) -> list[int]:
        data = await state.get_data()
        return data.get('user_last_messages_ids', [])

    async def _get_survey_type(self, state: FSMContext) -> str | None:
        data = await state.get_data()
        return data.get('survey_type', None)

    async def _get_cur_question(self, state: FSMContext) -> str | None:
        questions = await self._get_questions(state=state)
        if questions is None:
            return
        question_index = await self._get_question_index(state=state)
        return questions[question_index]

    async def _get_question_message_text(self, state: FSMContext) -> str:
        progress_bar = await self._get_progress_bar(state) or ''
        question = await self._get_cur_question(state) or ''
        previous_answer = await self._get_previous_answer_label(state)

        return progress_bar + question + previous_answer

    async def _get_keyboard(self, state: FSMContext) -> InlineKeyboardMarkup:
        questions = await self._get_questions(state=state)
        question_index = await self._get_question_index(state=state)
        if len(questions) == 1:
            logger.debug("The keyboard received was of the type: survey_done_button")
            return survey_done_button()
        elif question_index == 0:
            logger.debug("The keyboard received was of the type: survey_start_kb")
            return survey_start_kb()
        elif question_index == len(questions) - 1:
            logger.debug("The keyboard received was of the type: survey_done_kb")
            return survey_done_kb()
        logger.debug("The keyboard received was of the type: survey_base_kb")
        return survey_base_kb()

    async def _get_previous_answer(self, state: FSMContext) -> str | None:
        answers = await self._get_answers(state=state)
        cur_question = await self._get_cur_question(state=state)

        if cur_question in answers:
            logger.debug("Request for previous response: response received.")
            return answers[cur_question]
        logger.debug("Request for previous response: response NOT received.")

    async def _get_progress_bar(self, state: FSMContext) -> str | None:
        questions = await self._get_questions(state=state)
        if questions is None:
            return
        cur_question_number = await self._get_question_index(state=state) + 1
        return f'Вопрос {cur_question_number} из {len(questions)}\n\n'

    async def _get_previous_answer_label(self, state: FSMContext) -> str:
        previous_answer = await self._get_previous_answer(state)
        if previous_answer:
            return f'\n\nВаш предыдущий ответ:\n{previous_answer}'
        return ''

    # -- Обработчики --

    async def _start_button_handler(
        self, callback: CallbackQuery, state: FSMContext
    ) -> None:
        logger.info("The start button was pressed.")
        await state.set_state(SurveyFSM.active_survey)
        logger.debug("The SurveyFSM.active_survey state is set")
        await self.__delete_previous_messages__(callback, state)
        await self.__send_question__(callback, state)

    async def _next_button_handler(
        self, callback: CallbackQuery, state: FSMContext
    ) -> None:
        logger.info("The next button was pressed.")
        question_index = await self._get_question_index(state=state)
        answers = await self._get_answers(state=state)

        if len(answers) <= question_index:
            await callback.answer(
                text='Ответ не может быть пустым сообщением',
                show_alert=True,
            )
            logger.warning("The user attempted to send an empty message.")
            return

        question_index += 1
        await state.update_data(question_index=question_index)
        logger.info("Move to the next question.")
        await self.__delete_previous_messages__(callback, state)
        await self.__send_question__(callback, state, notification='Ответ сохранён')

    async def _back_button_handler(
        self, callback: CallbackQuery, state: FSMContext
    ) -> None:
        logger.info("The back button was pressed.")
        previous_question_index = await self._get_question_index(state=state) - 1

        await state.update_data(question_index=max(0, previous_question_index))
        logger.info("Move to the previous question.")
        await self.__delete_previous_messages__(callback, state)
        await self.__send_question__(callback, state, notification='Ответ сохранён')

    async def _stop_button_handler(
        self, callback: CallbackQuery, state: FSMContext
    ) -> None:
        logger.info("The stop button was pressed.")
        await self.__delete_previous_messages__(callback, state)
        await state.clear()
        logger.debug("State has been cleared.")
        await callback.answer('Опрос остановлен')
        logger.info("Survey has been stopped.")

    async def _done_button_handler(
        self, callback: CallbackQuery, state: FSMContext
    ) -> None:
        logger.info("The done button was pressed.")
        question_index = await self._get_question_index(state=state)
        answers = await self._get_answers(state=state)

        if len(answers) <= question_index:
            await callback.answer(
                text='Ответ не может быть пустым сообщением',
                show_alert=True,
            )
            logger.warning("The user attempted to send an empty message.")
            return

        await self.__delete_previous_messages__(callback, state)
        answers = await self._get_answers(state=state)
        survey_type = await self._get_survey_type(state=state)

        await state.clear()
        logger.debug("State has been cleared.")
        await callback.answer()

        handler = (
            self._completion_handlers.get(survey_type)
            if self._completion_handlers
            else self.on_complete_func
        )
        if handler:
            await handler(callback=callback, answers=answers)
            logger.info("The survey results have been passed to the handler function.")

    async def _saving_answer(self, message: Message, state: FSMContext) -> None:
        if not (message.text and message.text.strip()):
            logger.info("The empty message was not saved.")
            return

        question_index = await self._get_question_index(state=state)
        answers = await self._get_answers(state=state)

        questions = await self._get_questions(state=state)
        question = questions[question_index]
        answer = message.text

        logger.debug("Answer: %s", answer)
        logger.debug("Answers: %s", answers)
        if question in answers:
            answers[question] += f'\n{answer}'
            logger.info("Another answer to the question has been saved.")
        else:
            answers.update({question: answer})
            logger.info("Answer to the question saved.")

        await state.update_data(answers=answers)
        logger.debug("Answers have been saved in the state.")

        user_last_messages_ids = await self._get_user_last_messages_ids(state=state)
        user_last_messages_ids.append(message.message_id)
        await state.update_data(user_last_messages_ids=user_last_messages_ids)
        logger.debug(
            "A message with ID %s was added to the list of recently sent messages.",
            message.message_id,
        )
