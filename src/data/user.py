from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import List, TYPE_CHECKING

from .database import Base

if TYPE_CHECKING:
    from .expense import Expense, ExpenseCategory


class User(Base):
    """Database model for users.

    Attributes:
        id (int): Primary key for the user.
        username (str): Unique username of the user.
        email (str): Unique email address of the user.
        password (str): Hashed password of the user.
        created_at (datetime): Timestamp when the user was created.
        updated_at (datetime): Timestamp when the user was last updated.
        expenses (List[Expense]): List of expenses associated with the user.
        categories (List[ExpenseCategory]): List of expense categories created by the user.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), onupdate=func.now()
    )

    # Relatuonship with Expense and ExpenseCategory
    expenses: Mapped[List["Expense"]] = relationship(
        back_populates="user", cascade="all, delete"
    )
    expense_categories: Mapped[List["ExpenseCategory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
