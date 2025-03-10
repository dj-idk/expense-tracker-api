from datetime import datetime, timedelta, timezone
import random

from sqlalchemy.ext.asyncio import AsyncSession
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.data import Expense, User, ExpenseCategory
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


fake = Faker()


async def seed_categories_for_user(session: AsyncSession, user_id: int):
    """Ensure default categories exist for a new user"""
    try:
        for category in DEFAULT_CATEGORIES:
            session.add(ExpenseCategory(name=category, user_id=user_id))

        await session.commit()
    except Exception as e:
        await session.rollback()
        raise InternalServerError()


async def seed_expenses(session: AsyncSession, num_expenses: int = 1000):
    """
    Generate and insert fake expense data into the database for the past 4 years.
    """
    query = select(User)
    users = await session.execute(query)
    users = users.scalars().all()

    categories = await session.execute(select(ExpenseCategory))
    categories = categories.scalars().all()

    if not users or not categories:
        raise ValueError("No users or categories found in the database!")

    expenses = []

    for _ in range(num_expenses):
        days_ago = random.randint(0, 4 * 365)
        expense_date = datetime.now(timezone.utc) - timedelta(days=days_ago)

        new_expense = Expense(
            description=fake.sentence(),
            amount=round(random.uniform(5, 500), 2),
            user_id=random.choice(users).id,
            category_id=random.choice(categories).id,
            created_at=expense_date,
        )
        expenses.append(new_expense)

    session.add_all(expenses)
    await session.commit()
    print(f"Inserted {num_expenses} fake expenses.")
