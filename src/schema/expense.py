from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Union


class ExpenseCategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)


class ExpenseCategoryInDB(BaseModel):
    id: int
    name: str
    user_id: int
    expenses: List["ExpenseDisplay"] = []

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


class ExpenseCategoryDisplay(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ExpenseCreate(BaseModel):
    description: str = Field(..., max_length=200)
    amount: float = Field(...)
    category: Optional[str] = Field(None)


class ExpenseUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=200)
    amount: Optional[float] = Field(None)
    category: Optional[str] = Field(None)


class ExpenseInDB(BaseModel):
    id: int
    description: str
    amount: float
    category_id: int
    user_id: int
    category: "ExpenseCategoryInDB"

    model_config = ConfigDict(from_attributes=True)


class ExpenseDisplay(BaseModel):
    id: int
    description: str
    amount: float
    category: "ExpenseCategoryDisplay"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FilterSummary(BaseModel):
    total_count: int
    total_amount: float


class FilteredExpenses(BaseModel):
    summary: FilterSummary
    result: Union[ExpenseDisplay, List[ExpenseDisplay]]


class FilteredExpenseCategory(BaseModel):
    summary: FilterSummary
    result: "ExpenseCategoryInDB"


class Pagination(BaseModel):
    total: int
    limit: int
    skip: int
    current_page: int
    total_pages: int
    has_previous: bool
    has_next: bool


class ExpenseListResponse(BaseModel):
    expenses: List[ExpenseDisplay]
    pagination: Pagination
