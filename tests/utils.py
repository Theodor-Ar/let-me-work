from aiogram.types import Chat, User

TEST_USER = User(
    id=123,
    is_bot=False,
    first_name="TestUser",
    last_name=None,
    username="TestUserName",
    language_code="ru-RU",
    is_premium=False,
)

TEST_USER_CHAT = Chat(
    id=456,
    type="private",
    title=None,
    username=TEST_USER.username,
    first_name=TEST_USER.first_name,
    last_name=TEST_USER.last_name,
)
