
from pydantic import BaseModel


class User(BaseModel):
    id: int
    is_bot: bool
    refer_id: int | None = None
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    is_premium: bool
    added_to_attachment_menu: bool
    can_join_groups: bool
    can_read_all_group_messages: bool
    supports_inline_queries: bool
    created_at: int = 0
    updated_at: int = 0
    blocked_at: int | None = None
