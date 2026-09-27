from collections.abc import Callable
from unittest.mock import AsyncMock, Mock

import pytest
from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from handlers.survey import Survey, SurveyFSM
from keyboards import (
    survey_base_kb,
    survey_done_button,
    survey_done_kb,
    survey_intro_kb,
    survey_start_kb,
)
from phrases import INTRODUCTION_TEXT
from tests.conftest import TEST_QUESTIONS
from tests.utils import TEST_USER_CHAT


@pytest.mark.asyncio
async def test_intro(survey: Survey, state: FSMContext):
    survey.bot.send_message = AsyncMock()
    survey.__init_state__ = AsyncMock()

    await survey.start(state=state, chat_id=TEST_USER_CHAT.id, questions=TEST_QUESTIONS)

    survey.__init_state__.assert_awaited_once()
    survey.bot.send_message.assert_awaited_once_with(
        chat_id=TEST_USER_CHAT.id,
        text=INTRODUCTION_TEXT,
        reply_markup=survey_intro_kb(),
    )


@pytest.mark.asyncio
async def test_init_state(survey: Survey, state: FSMContext):
    await survey.__init_state__(
        state=state, questions=TEST_QUESTIONS, survey_type='TEST'
    )

    assert await state.get_data() == {
        'questions': TEST_QUESTIONS,
        'question_index': 0,
        'answers': {},
        'user_last_messages_ids': [],
        'survey_type': 'TEST',
    }


def test_register_handlers(survey: Survey, router: Router):
    router.callback_query.register = Mock()
    router.message.register = Mock()

    survey.__register_handlers__(router=router)

    assert router.callback_query.register.call_count == 5
    router.callback_query.register.assert_any_call(
        survey._start_button_handler, F.data == 'survey_start'
    )
    router.callback_query.register.assert_any_call(
        survey._next_button_handler, F.data == 'survey_next'
    )
    router.callback_query.register.assert_any_call(
        survey._back_button_handler, F.data == 'survey_back'
    )
    router.callback_query.register.assert_any_call(
        survey._stop_button_handler, F.data == 'survey_stop'
    )
    router.callback_query.register.assert_any_call(
        survey._done_button_handler, F.data == 'survey_done'
    )
    router.message.register.assert_called_once_with(
        survey._saving_answer, SurveyFSM.active_survey, F.text
    )


@pytest.mark.asyncio
async def test_start_button_handler(
    survey: Survey, callback: CallbackQuery, state: FSMContext
):
    survey.__delete_previous_messages__ = AsyncMock()
    survey.__send_question__ = AsyncMock()

    await survey._start_button_handler(callback=callback, state=state)

    assert await state.get_state() == SurveyFSM.active_survey
    survey.__delete_previous_messages__.assert_awaited_once_with(callback, state)
    survey.__send_question__.assert_awaited_once_with(callback, state)


@pytest.mark.asyncio
async def test_next_button_handler_no_answer(
    survey: Survey, callback: CallbackQuery, state: FSMContext
):
    callback.answer = AsyncMock()
    await state.update_data(
        question_index=0,
        answers={},
    )

    await survey._next_button_handler(callback=callback, state=state)

    callback.answer.assert_awaited_once_with(
        text='Ответ не может быть пустым сообщением',
        show_alert=True,
    )


@pytest.mark.asyncio
async def test_next_button_handler_with_answer(
    survey: Survey, callback: CallbackQuery, state: FSMContext
):
    await state.update_data(
        question_index=0,
        answers={'Question 1': 'Answer 1'},
    )
    survey.__delete_previous_messages__ = AsyncMock()
    survey.__send_question__ = AsyncMock()

    await survey._next_button_handler(callback=callback, state=state)

    question_index = await survey._get_question_index(state=state)
    assert question_index == 1
    survey.__delete_previous_messages__.assert_awaited_once_with(callback, state)
    survey.__send_question__.assert_awaited_once_with(
        callback, state, notification='Ответ сохранён'
    )


@pytest.mark.asyncio
@pytest.mark.parametrize('question_index', [0, 1, 2])
async def test_back_button_handler(
    question_index, survey: Survey, callback: CallbackQuery, state: FSMContext
):
    await state.update_data(
        question_index=question_index,
        answers={},
    )
    survey.__delete_previous_messages__ = AsyncMock()
    survey.__send_question__ = AsyncMock()

    await survey._back_button_handler(callback=callback, state=state)

    final_question_index = await survey._get_question_index(state=state)
    assert final_question_index == max(0, question_index - 1)
    survey.__delete_previous_messages__.assert_awaited_once_with(callback, state)
    survey.__send_question__.assert_awaited_once_with(
        callback, state, notification='Ответ сохранён'
    )


@pytest.mark.asyncio
async def test_stop_button_handler(
    survey: Survey, callback: CallbackQuery, state: FSMContext
):
    survey.__delete_previous_messages__ = AsyncMock()
    state.clear = AsyncMock()
    callback.answer = AsyncMock()

    await survey._stop_button_handler(callback=callback, state=state)

    survey.__delete_previous_messages__.assert_awaited_once_with(callback, state)
    state.clear.assert_awaited_once()
    callback.answer.assert_awaited_once_with('Опрос остановлен')


@pytest.mark.asyncio
async def test_done_button_handler_no_answer(
    survey: Survey, callback: CallbackQuery, state: FSMContext
):
    callback.answer = AsyncMock()
    await state.update_data(
        question_index=0,
        answers={},
    )

    await survey._done_button_handler(callback=callback, state=state)

    callback.answer.assert_awaited_once_with(
        text='Ответ не может быть пустым сообщением',
        show_alert=True,
    )


@pytest.mark.parametrize(
    '_completion_handlers, on_complete_func',
    [
        ({'TEST': AsyncMock()}, AsyncMock()),
        ({'TEST': AsyncMock()}, None),
        (None, AsyncMock()),
        (None, None),
    ],
)
@pytest.mark.asyncio
async def test_done_button_handler_with_answer(
    _completion_handlers: dict[str, Callable],
    on_complete_func: Callable,
    survey: Survey,
    callback: CallbackQuery,
    state: FSMContext,
):
    survey.on_complete_func = on_complete_func
    survey._completion_handlers = _completion_handlers
    await state.update_data(
        question_index=0,
        answers={'Question 1': 'Answer 1'},
        survey_type='TEST',
    )
    survey.__delete_previous_messages__ = AsyncMock()
    state.clear = AsyncMock()

    await survey._done_button_handler(callback=callback, state=state)

    answers = await survey._get_answers(state=state)
    survey.__delete_previous_messages__.assert_awaited_once_with(callback, state)
    state.clear.assert_awaited_once()
    handler = (
        survey._completion_handlers.get('TEST')
        if survey._completion_handlers
        else survey.on_complete_func
    )
    if handler:
        handler.assert_awaited_once_with(callback=callback, answers=answers)


@pytest.mark.asyncio
async def test_saving_answer(message: Message, state: FSMContext, survey: Survey):
    await state.update_data(question_index=0, answers={})

    await survey._saving_answer(message=message, state=state)

    question_index = await survey._get_question_index(state=state)
    answers = await survey._get_answers(state=state)
    user_last_messages_ids = await survey._get_user_last_messages_ids(state=state)
    assert answers[TEST_QUESTIONS[question_index]] == message.text
    assert user_last_messages_ids[-1] == message.message_id


@pytest.mark.asyncio
@pytest.mark.parametrize('text', ['  ', '', None])
async def test_saving_answer_no_text(text, state: FSMContext, survey: Survey):
    message = AsyncMock(text=text)
    data_before = await state.get_data()

    await survey._saving_answer(message=message, state=state)

    data_after = await state.get_data()
    assert data_before == data_after


@pytest.mark.asyncio
async def test_saving_answer_question_in_answers(
    message: Message, state: FSMContext, survey: Survey
):
    question, answer_before = TEST_QUESTIONS[0], "Answer"
    answers_before = {question: answer_before}
    await state.update_data(answers=answers_before)

    await survey._saving_answer(message=message, state=state)

    answer_after = message.text
    answers_after = await survey._get_answers(state=state)
    user_last_messages_ids = await survey._get_user_last_messages_ids(state=state)
    assert answers_after[question] == answer_before + '\n' + answer_after
    assert user_last_messages_ids[-1] == message.message_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'question_index, expected_keyboard',
    [
        (0, survey_start_kb()),
        (len(TEST_QUESTIONS) - 1, survey_done_kb()),
        (1, survey_base_kb()),
    ],
)
async def test_get_keyboard(
    question_index: int,
    expected_keyboard: InlineKeyboardMarkup,
    state: FSMContext,
    survey: Survey,
):
    await state.update_data(question_index=question_index)

    keyboard = await survey._get_keyboard(state=state)

    assert keyboard == expected_keyboard


@pytest.mark.asyncio
async def test_get_keyboard_one_question(state: FSMContext, survey: Survey):
    await state.update_data(questions=["Question"])

    keyboard = await survey._get_keyboard(state=state)

    assert keyboard == survey_done_button()


@pytest.mark.parametrize('index', [i for i in range(len(TEST_QUESTIONS))])
@pytest.mark.asyncio
async def test_get_progress_bar(index: int, state: FSMContext, survey: Survey):
    await state.update_data(question_index=index)

    progress_bar_text = await survey._get_progress_bar(state=state)

    assert progress_bar_text == f'Вопрос {index + 1} из {len(TEST_QUESTIONS)}\n\n'


@pytest.mark.parametrize('index', [i for i in range(len(TEST_QUESTIONS))])
@pytest.mark.asyncio
async def test_get_cur_question(index: int, state: FSMContext, survey: Survey):
    await state.update_data(question_index=index)

    cur_question = await survey._get_cur_question(state=state)

    assert cur_question == TEST_QUESTIONS[index]


@pytest.mark.parametrize('index', [i for i in range(len(TEST_QUESTIONS))])
@pytest.mark.asyncio
async def test_get_previous_answer_good(index: int, state: FSMContext, survey: Survey):
    question, answer = TEST_QUESTIONS[index], "Answer"
    await state.update_data(
        answers={question: answer},
        question_index=index,
    )

    previous_answer = await survey._get_previous_answer(state=state)

    assert previous_answer == answer


@pytest.mark.asyncio
async def test_get_previous_answer_bad(state: FSMContext, survey: Survey):
    previous_answer = await survey._get_previous_answer(state=state)

    assert previous_answer is None


@pytest.mark.parametrize('index', [i for i in range(len(TEST_QUESTIONS))])
@pytest.mark.asyncio
async def test_get_previous_answer_label_good(
    index: int, state: FSMContext, survey: Survey
):
    question, answer = TEST_QUESTIONS[index], "Answer"
    await state.update_data(
        answers={question: answer},
        question_index=index,
    )
    previous_answer = await survey._get_previous_answer(state=state)

    previous_answer_label = await survey._get_previous_answer_label(state=state)

    assert previous_answer_label == f"\n\nВаш предыдущий ответ:\n{previous_answer}"


@pytest.mark.asyncio
async def test_get_previous_answer_label_bad(state: FSMContext, survey: Survey):
    previous_answer_label = await survey._get_previous_answer_label(state=state)

    assert previous_answer_label == ''


@pytest.mark.parametrize(
    'callback, chat_id, message_id',
    [
        (AsyncMock(), 123, 456),
        (AsyncMock(), 123, None),
        (AsyncMock(), None, 456),
        (AsyncMock(), None, None),
        (None, 123, 456),
        (None, 123, None),
        (None, None, 456),
        (None, None, None),
    ],
)
@pytest.mark.asyncio
async def test_delete_message(
    survey: Survey,
    callback: CallbackQuery | None,
    chat_id: int | None,
    message_id: int | None,
):
    survey.bot.delete_message = AsyncMock()

    await survey.__delete_message__(
        callback=callback, chat_id=chat_id, message_id=message_id
    )

    cnt_requests = survey.bot.delete_message.await_count
    assert cnt_requests == (1 if callback or (chat_id and message_id) else 0)


@pytest.mark.parametrize(
    'side_effect, user_last_messages_ids',
    [
        (None, []),
        (
            TelegramBadRequest(
                method=AsyncMock(), message="Message cannot be deleted."
            ),
            [101, 102],
        ),
    ],
)
@pytest.mark.asyncio
async def test_delete_previous_messages(
    side_effect,
    user_last_messages_ids,
    callback: CallbackQuery,
    state: FSMContext,
    survey: Survey,
):
    survey.bot.delete_message = AsyncMock(side_effect=side_effect)
    await state.update_data(user_last_messages_ids=user_last_messages_ids)

    await survey.__delete_previous_messages__(callback=callback, state=state)

    assert survey.bot.delete_message.await_count == len(user_last_messages_ids) + 1
    assert await survey._get_user_last_messages_ids(state=state) == []


@pytest.mark.parametrize(
    'question_index, answers',
    [
        (0, {TEST_QUESTIONS[0]: "Answer 1"}),
        (1, {TEST_QUESTIONS[0]: "Answer 1"}),
    ],
)
@pytest.mark.asyncio
async def test_get_question_message_text(
    question_index: int, answers, state: FSMContext, survey: Survey
):
    await state.update_data(
        question_index=question_index,
        answers=answers,
    )
    question_text = TEST_QUESTIONS[question_index]
    previous_answer = (
        f"\n\nВаш предыдущий ответ:\n{answers[question_text]}"
        if question_text in answers
        else ''
    )
    expected_text = (
        f"Вопрос {question_index + 1} из {len(TEST_QUESTIONS)}\n\n"
        f"{question_text}"
        f"{previous_answer}"
    )

    question_message_text = await survey._get_question_message_text(state=state)

    assert question_message_text == expected_text


@pytest.mark.parametrize('notification', [None, "notification"])
@pytest.mark.asyncio
async def test_send_question(
    notification, callback: CallbackQuery, state: FSMContext, survey: Survey
):
    survey.bot.send_message = AsyncMock()
    callback.answer = AsyncMock()
    text = await survey._get_question_message_text(state=state)
    keyboard = await survey._get_keyboard(state)

    await survey.__send_question__(
        callback=callback, state=state, notification=notification
    )

    survey.bot.send_message.assert_awaited_once_with(
        chat_id=callback.message.chat.id, text=text, reply_markup=keyboard
    )
    callback.answer.assert_awaited_with(notification)


@pytest.mark.asyncio
async def test_get_questions(survey: Survey, state: FSMContext):
    questions = await survey._get_questions(state=state)

    data = await state.get_data()
    assert data.get('questions', []) == questions


@pytest.mark.asyncio
async def test_get_answers(survey: Survey, state: FSMContext):
    answers = await survey._get_answers(state=state)

    data = await state.get_data()
    assert data.get('answers', {}) == answers


@pytest.mark.asyncio
async def test_get_question_index(survey: Survey, state: FSMContext):
    question_index = await survey._get_question_index(state=state)

    data = await state.get_data()
    assert data.get('question_index', 0) == question_index


@pytest.mark.asyncio
async def test_get_user_last_messages_ids(survey: Survey, state: FSMContext):
    user_last_messages_ids = await survey._get_user_last_messages_ids(state=state)

    data = await state.get_data()
    assert data.get('user_last_messages_ids', []) == user_last_messages_ids


@pytest.mark.asyncio
async def test_get_survey_type(survey: Survey, state: FSMContext):
    survey_type = await survey._get_survey_type(state=state)

    data = await state.get_data()
    assert data.get('survey_type', None) == survey_type


def test_register_completion_handler(survey: Survey):
    survey_type, func = "TEST", AsyncMock()

    survey.register_completion_handler(survey_type, func)

    assert survey._completion_handlers[survey_type] == func
