"""Схемы данных"""

from .database.user import User
from .database.vacancy import (
    Contacts,
    Currency,
    Description,
    Education,
    EducationLevel,
    EmploymentType,
    ExperienceLevel,
    Qualification,
    Salary,
    UserVacancyHistory,
    Vacancy,
    WorkFormat,
    WorkType,
)

__all__ = [
    "User",
    "UserVacancyHistory",
    "Vacancy",
    "Contacts",
    "Description",
    "Education",
    "Qualification",
    "Salary",
    "WorkType",
    "Currency",
    "EducationLevel",
    "EmploymentType",
    "ExperienceLevel",
    "WorkFormat",
]
