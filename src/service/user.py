from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.data import ExpenseCategory, User
from src.schema import UserCreate, UserLogin, UserUpdate, UserDisplay
from src.utils import (
    hash_password,
    verify_password,
    seed_categories_for_user,
    Unauthorized,
)


class UserService:
    """A class for managing user services"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, register_form: UserCreate):
        """Registers a new user"""
        try:
            new_user = User(
                username=register_form.username,
                email=register_form.email,
                password=hash_password(register_form),
            )
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)

            await seed_categories_for_user(self.db, new_user.id)

            return UserDisplay.model_validate(new_user)
        except Exception as e:
            await self.db.rollback()
            raise e

    async def authenticate_user(self, login_form: UserLogin):
        try:
            query = select(User).where(
                (User.username == login_form.username_or_email)
                | (User.email == login_form.username_or_email)
            )
            result = await self.db.execute(query)
            user = result.scalars().first()

            if not user or not verify_password(login_form.password, user.password):
                return Unauthorized("Invalid Username/Email or Password.")

            return UserDisplay.model_validate(user)
        except Exception as e:
            raise e
