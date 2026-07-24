from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.networks import HttpUrl


class UserVacancyHistory(BaseModel):
    id: int
    user_id: int
    vacancy_external_id: str
    sent_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = ConfigDict(from_attributes=True)


class Vacancy(BaseModel):
    id: int
    external_id: str
    user_id: int

    title: str = Field(..., max_length=255)
    description: Description
    salary: Salary
    qualification: Qualification
    work_type: WorkType
    company_name: str
    contacts: Contacts

    model_config = ConfigDict(from_attributes=True)


class Description(BaseModel):
    full_description: str = Field(..., max_length=10_000)
    short_description: str = Field(..., max_length=1_000)


class Salary(BaseModel):
    salary_from: int | float | None = Field(default=None, ge=0)
    salary_to: int | float | None = Field(default=None, ge=0)
    currency: Currency
    is_gross: bool | None = None


class WorkType(BaseModel):
    work_format: WorkFormat
    employment_type: EmploymentType
    location: str


class Qualification(BaseModel):
    experience_level: ExperienceLevel
    education: Education
    total_experience_months: int = Field(0, ge=0)
    skills: list[str] = Field(default_factory=list)


class Contacts(BaseModel):
    contact_url: HttpUrl
    contact_telegram: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None


# -- Вспомогательные классы --


class Education(BaseModel):
    level: EducationLevel
    specialization: str


class WorkFormat(str, Enum):
    REMOTE = 'remote'
    OFFICE = 'office'
    HYBRID = 'hybrid'


class Currency(str, Enum):
    RUB = 'RUB'  # Российский рубль
    USD = 'USD'  # Доллар США
    EUR = 'EUR'  # Евро
    GBP = 'GBP'  # Фунт стерлингов
    CHF = 'CHF'  # Швейцарский франк
    JPY = 'JPY'  # Японская иена
    CNY = 'CNY'  # Китайский юань
    AUD = 'AUD'  # Австралийский доллар
    CAD = 'CAD'  # Канадский доллар
    AED = 'AED'  # Дирхам ОАЭ
    SGD = 'SGD'  # Сингапурский доллар


class EmploymentType(str, Enum):
    FULL_TIME = 'full_time'
    PART_TIME = 'part_time'
    PROJECT = 'project'
    INTERNSHIP = 'internship'


class ExperienceLevel(str, Enum):
    UNKNOWN = 'unknown'
    START = 'start'
    SPECIALIST = 'specialist'
    EXPERT = 'expert'
    MANAGEMENT = 'management'
    TOP_MANAGEMENT = 'top_management'


class EducationLevel(str, Enum):
    NOT_REQUIRED = 'not_required'
    HIGHER = 'higher'
    INCOMPLETE_HIGHER = 'incomplete_higher'
    BACHELOR = 'bachelor'
    MASTER = 'master'
    SPECIALIST = 'specialist'
    SECONDARY_SPECIAL = 'secondary_special'
    SECONDARY = 'secondary'
    UNKNOWN = 'unknown'
