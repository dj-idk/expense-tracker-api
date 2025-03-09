from __future__ import annotations

from datetime import datetime


from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .expense import ExpenseCategoryDisplay, ExpenseDisplay


class UserCreate(BaseModel):
    username: str = Field(..., max_length=100)
    email: EmailStr = Field(..., max_length=200)
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str = Field(..., max_length=100)
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = Field(None, max_length=200)
    password: Optional[str] = Field(None, min_length=8)


class UserDisplay(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    expense_categories: Optional[List["ExpenseCategoryDisplay"]] = []
    expenses: Optional[List["ExpenseDisplay"]]

    model_config = ConfigDict(
        from_attributes=True,
    )
