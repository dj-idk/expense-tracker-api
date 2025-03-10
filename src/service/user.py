from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.data import User
from src.schema import (
    UserCreate,
    UserLogin,
    UserDisplay,
)
from src.utils import (
    hash_password,
    verify_password,
    seed_categories_for_user,
    Conflict,
    InternalServerError,
)


class UserService:
    """A class for managing user services"""

    @staticmethod
    async def register_user(session: AsyncSession, register_form: UserCreate):
        """Registers a new user"""
        try:
            password_hash = hash_password(register_form.password)
            new_user = User(
                username=register_form.username,
                email=register_form.email,
                password=password_hash,
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            await seed_categories_for_user(session, new_user.id)
            query = (
                select(User)
                .options(selectinload(User.expense_categories))
                .filter(User.id == new_user.id)
            )
            result = await session.execute(query)
            user_with_relations = result.scalars().first()

            return user_with_relations
        except IntegrityError:
            await session.rollback()
            raise Conflict("User with the same credentials already exists.")
        except SQLAlchemyError as e:
            await session.rollback()
            raise InternalServerError(f"{e}")
        except Exception as e:
            await session.rollback()
            raise InternalServerError(f"{e}")

    @staticmethod
    async def authenticate_user(session: AsyncSession, login_form: UserLogin):
        try:
            query = select(User).where(
                (User.username == login_form.username)
                | (User.email == login_form.username)
            )
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if not user or not verify_password(login_form.password, user.password):
                return None

            return user
        except Exception as e:
            raise InternalServerError(f"{e}")

    @staticmethod
    async def read_user_by_username(session: AsyncSession, username: str):
        try:
            query = (
                select(User)
                .options(selectinload(User.expense_categories))
                .where(User.username == username)
            )
            result = await session.execute(query)

            user = result.unique().scalar_one_or_none()
            if not user:
                return None

            return user

        except SQLAlchemyError as e:
            raise InternalServerError(f"An error occurred: {str(e)}")
        except Exception as e:
            raise InternalServerError(f"An error occurred: {str(e)}")
