from unittest.mock import AsyncMock

import pytest
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from handlers.survey import Survey, SurveyFSM
from keyboards import (
    survey_base_kb,
    survey_done_buttom,
    survey_done_kb,
    survey_intro_kb,
    survey_start_kb,
)
from phrases import INTRODUCTION_TEXT
from tests.conftest import TEST_QUESTIONS
from tests.utils import TEST_USER_CHAT


@pytest.mark.asyncio
async def test_intro(bot: Bot, survey: Survey):
    bot.send_message = AsyncMock()
    await survey.start()
    bot.send_message.assert_awaited_once_with(
        chat_id=TEST_USER_CHAT.id,
        text=INTRODUCTION_TEXT,
        reply_markup=survey_intro_kb(),
    )


@pytest.mark.asyncio
async def test_start_button_handler(
    survey: Survey, callback: CallbackQuery, state: FSMContext
):
    survey.__delete_previous_messages__ = AsyncMock()
    survey.__send_question__ = AsyncMock()

    await survey._start_button_handler(callback=callback, state=state)

    assert await state.get_state() == SurveyFSM.active_survey
    assert await state.get_data() == {'question_index': 0, 'answers': {}}
    survey.__delete_previous_messages__.assert_awaited_once_with(callback, state)
    survey.__send_question__.assert_awaited_once_with(callback, state)


@pytest.mark.asyncio
async def test_next_button_handler_no_answer(
    survey: Survey, callback: CallbackQuery, state: FSMContext
):
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

    data = await state.get_data()
    question_index = data.get('question_index')
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

    data = await state.get_data()
    final_question_index = data.get('question_index')
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
async def test_done_button_handler(
    survey: Survey, callback: CallbackQuery, state: FSMContext
):
    await state.update_data(
        question_index=0,
        answers={'Question 1': 'Answer 1'},
    )
    survey.__delete_previous_messages__ = AsyncMock()
    state.clear = AsyncMock()
    survey.on_complete_func = AsyncMock()

    await survey._done_button_handler(callback=callback, state=state)

    data = await state.get_data()
    answers = data.get('answers')
    survey.__delete_previous_messages__.assert_awaited_once_with(callback, state)
    state.clear.assert_awaited_once()
    survey.on_complete_func.assert_awaited_once_with(callback=callback, answers=answers)


@pytest.mark.asyncio
async def test_saving_answer(message, state: FSMContext, survey: Survey):
    await state.update_data(
        question_index=0,
        answers={},
    )

    await survey._saving_answer(
        message=message,
        state=state,
    )

    data = await state.get_data()

    question_index = data.get('question_index')
    answers = data.get('answers')

    assert answers[survey.questions[question_index]] == message.text


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
    message, state: FSMContext, survey: Survey
):
    question, answer_before = TEST_QUESTIONS[0], "Answer"
    answers_before = {question: answer_before}
    await state.update_data(answers=answers_before)

    await survey._saving_answer(message=message, state=state)

    data = await state.get_data()
    answer_after = message.text
    answers_after = data.get('answers')
    assert answers_after[question] == answer_before + '\n' + answer_after


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
    question_index, expected_keyboard, state: FSMContext, survey: Survey
):
    await state.update_data(question_index=question_index)

    keyboard = await survey._get_keyboard(state=state)

    assert keyboard == expected_keyboard


@pytest.mark.asyncio
async def test_get_keyboard_one_question(state: FSMContext, survey: Survey):
    survey.questions = ["Question"]

    keyboard = await survey._get_keyboard(state=state)

    assert keyboard == survey_done_buttom()


@pytest.mark.parametrize('index', [i for i in range(len(TEST_QUESTIONS))])
@pytest.mark.asyncio
async def test_get_progress_bar(index, state: FSMContext, survey: Survey):
    await state.update_data(question_index=index)

    progress_bar_text = await survey._get_progress_bar(state=state)

    assert progress_bar_text == f'Вопрос {index + 1} из {len(TEST_QUESTIONS)}\n\n'


@pytest.mark.parametrize('index', [i for i in range(len(TEST_QUESTIONS))])
@pytest.mark.asyncio
async def test_get_cur_question(index, state: FSMContext, survey: Survey):
    await state.update_data(question_index=index)

    cur_question = await survey._get_cur_question(state=state)

    assert cur_question == TEST_QUESTIONS[index]


@pytest.mark.parametrize('index', [i for i in range(len(TEST_QUESTIONS))])
@pytest.mark.asyncio
async def test_get_previous_answer_good(index, state: FSMContext, survey: Survey):
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
async def test_get_previous_answer_label_good(index, state: FSMContext, survey: Survey):
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
    'side_effect',
    [
        None,
        TelegramBadRequest(method=AsyncMock(), message="Message cannot be deleted."),
    ],
)
@pytest.mark.asyncio
async def test_delete_previous_messages(
    side_effect, callback: CallbackQuery, state: FSMContext, survey: Survey
):
    survey.bot.delete_message = AsyncMock(side_effect=side_effect)
    await state.update_data(last_user_messages_id=[101, 102])

    await survey.__delete_previous_messages__(callback=callback, state=state)

    assert survey.bot.delete_message.await_count == 3
    data = await state.get_data()
    assert data.get('last_user_messages_id') == []


@pytest.mark.parametrize(
    'question_index, answers',
    [
        (0, {TEST_QUESTIONS[0]: "Answer 1"}),
        (1, {TEST_QUESTIONS[0]: "Answer 1"}),
    ],
)
@pytest.mark.asyncio
async def test_get_question_message_text(
    question_index, answers, state: FSMContext, survey: Survey
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
