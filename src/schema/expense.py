from pydantic import BaseModel, Field, ConfigDict

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserDisplay


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
    user: "UserDisplay"
    category: "ExpenseCategoryInDB"

    model_config = ConfigDict(from_attributes=True)


class ExpenseDisplay(BaseModel):
    id: int
    description: str
    amount: float
    category: str

    model_config = ConfigDict(from_attributes=True)


class ExpenseCategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)


class ExpenseCategoryInDB(BaseModel):
    id: int
    name: str
    user_id: int
    expenses: List["ExpenseInDB"] = []

    model_config = ConfigDict(from_attributes=True)


class ExpenseCategoryDisplay(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)
