from sqlalchemy.ext.asyncio import AsyncSession

from src.data import ExpenseCategory
from .exceptions import InternalServerError

DEFAULT_CATEGORIES = [
    "Groceries",
    "Leisure",
    "Electronics",
    "Utilities",
    "Clothing",
    "Health",
    "Others",
]


async def seed_categories_for_user(session: AsyncSession, user_id: int):
    """Ensure default categories exist for a new user"""
    try:
        for category in DEFAULT_CATEGORIES:
            session.add(ExpenseCategory(name=category, user_id=user_id))

        await session.commit()
    except Exception as e:
        await session.rollback()
        raise InternalServerError()
