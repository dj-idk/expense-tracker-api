from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from .database import Base

if TYPE_CHECKING:
    from .user import User


class ExpenseCategory(Base):
    """Database model for expense categories.

    Attributes:
        id (int): Primary key for the category.
        name (str): Name of the category.
        user_id (int): Foreign key linking the category to a specific user.
        expenses (List[Expense]): List of expenses under this category.
        user (User): The user who owns this category.
    """

    __tablename__ = "expense_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Relationship with Expense and User
    expenses: Mapped[List["Expense"]] = relationship(back_populates="category")
    user: Mapped["User"] = relationship(back_populates="expense_categories")


class Expense(Base):
    """Database model for expenses.

    Attributes:
        id (int): Primary key for the expense.
        description (str): Description of the expense.
        amount (float): Amount spent.
        category_id (int): Foreign key linking the expense to a category.
        user_id (int): Foreign key linking the expense to a user.
        user (User): The user who owns this expense.
        category (ExpenseCategory): The category under which this expense falls.
    """

    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("expense_categories.id", ondelete="SET NULL"),
        nullable=False,
        default=["Others"],
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Relationship with Category and User
    user: Mapped["User"] = relationship(back_populates="expenses")
    category: Mapped["ExpenseCategory"] = relationship(back_populates="expenses")
