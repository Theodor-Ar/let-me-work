from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


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
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    blocked_at: datetime | None = None

    is_admin: bool = False

    model_config = ConfigDict(from_attributes=True)
