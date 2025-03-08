from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from .database import Base

if TYPE_CHECKING:
    from .expense import Expense


class User(Base):
    """Database model for User"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    # Expenses - CASCADE to delete expenses when user is removed
    expenses: Mapped[List["Expense"]] = relationship(
        back_populates="user", cascade="all, delete"
    )
