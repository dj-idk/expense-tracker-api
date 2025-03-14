from datetime import datetime, timezone

from sqlalchemy import DateTime, String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import List, TYPE_CHECKING

from .database import Base

if TYPE_CHECKING:
    from .expense import Expense, ExpenseCategory


class AccessToken(Base):
    """Database model for user access tokens.

    Attributes:
        id (str)
        user_id (int)
        created_at (datetime)
        is_revoked (bool)
        user (User)

    """

    __tablename__ = "access_tokens"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=timezone.utc), server_default=func.now(), nullable=False
    )
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    user: Mapped["User"] = relationship("User", back_populates="tokens", lazy="joined")


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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    expenses: Mapped[List["Expense"]] = relationship(
        back_populates="user", cascade="all, delete"
    )
    expense_categories: Mapped[List["ExpenseCategory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    tokens = relationship(
        "AccessToken", back_populates="user", cascade="all, delete-orphan"
    )
