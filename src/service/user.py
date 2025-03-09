from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.data import User, Expense, ExpenseCategory
from src.schema import (
    UserCreate,
    UserLogin,
    UserDisplay,
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseDisplay,
    ExpenseCategoryDisplay,
    ExpenseCategoryInDB,
)
from src.utils import (
    hash_password,
    verify_password,
    seed_categories_for_user,
    Unauthorized,
    Conflict,
    InternalServerError,
    NotFound,
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
                .options(joinedload(User.expense_categories), joinedload(User.expenses))
                .filter(User.id == new_user.id)
            )
            result = await session.execute(query)
            user_with_relations = result.scalars().first()

            return UserDisplay.model_validate(user_with_relations)
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
                .options(joinedload(User.expense_categories), joinedload(User.expenses))
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

    @staticmethod
    async def add_expense(session: AsyncSession, expense: ExpenseCreate, user_id: int):
        try:
            user = await session.execute(select(User).filter_by(id=user_id))
            user = user.scalars().first()
            if not user:
                raise Unauthorized("Invalid User Credentials.")

            category = await UserService.create_category_if_none(
                session, expense.category, user_id
            )

            new_expense = Expense(
                description=expense.description,
                amount=expense.amount,
                user_id=user_id,
                category_id=category.id,
            )

            session.add(new_expense)
            await session.commit()
            await session.refresh(new_expense)

            return new_expense
        except SQLAlchemyError as e:
            await session.rollback()
            raise InternalServerError(f"{e}")
        except Exception as e:
            await session.rollback()
            raise InternalServerError(f"{e}")

    @staticmethod
    async def update_expense(
        session: AsyncSession, update_form: ExpenseUpdate, user_id: int, expense_id: int
    ):
        try:
            query = select(Expense).where(
                and_(Expense.id == expense_id, Expense.user_id == user_id)
            )
            result = await session.execute(query)
            expense = result.scalar_one_or_none()
            if not expense:
                raise NotFound(f"Expense {expense_id} was not found.")

            update_data = update_form.model_dump(exclude_unset=True)
            if "category" in update_data:
                category = await UserService.create_category_if_none(
                    session, update_data["category"], user_id
                )
                update_data["category"] = category

            for key, value in update_data.items():
                setattr(expense, key, value)

            await session.commit()
            await session.refresh(expense)

            return expense
        except NotFound as e:
            raise e
        except SQLAlchemyError as e:
            await session.rollback()
            raise InternalServerError(f"{e}")
        except Exception as e:
            await session.rollback()
            raise InternalServerError(f"{e}")

    @staticmethod
    async def delete_expense(session: AsyncSession, user_id: int, expense_id: int):
        try:
            query = select(Expense).where(
                and_(Expense.id == expense_id, Expense.user_id == user_id)
            )
            result = await session.execute(query)

            expense = result.scalar_one_or_none()
            if not expense:
                raise NotFound(f"Expense {expense_id} was not found.")

            await session.delete(expense)
            await session.commit()

            return {"message": f"Expense {expense_id} was deleted successfully."}
        except NotFound as e:
            raise e
        except SQLAlchemyError as e:
            await session.rollback()
            raise InternalServerError(f"{e}")
        except Exception as e:
            await session.rollback()
            raise InternalServerError(f"{e}")

    @staticmethod
    async def search_expenses_by_description(
        session: AsyncSession, user_id: int, description: str
    ):
        try:
            query = (
                select(Expense)
                .options(joinedload(Expense.category))
                .where(Expense.user_id == user_id)
                .filter(Expense.description.ilike(f"%{description}%"))
            )
            result = await session.execute(query)
            expenses = result.unique().scalars().all()

            expense_responses = [
                ExpenseDisplay.model_validate(expense) for expense in expenses
            ]

            return expense_responses
        except Exception as e:
            raise InternalServerError(f"{e}")

    @staticmethod
    async def get_all_expenses(
        session: AsyncSession, user_id: int, limit: int = 10, skip: int = 0
    ):
        try:
            if limit > 100:
                limit = 100

            total = await session.scalar(func.count(Expense.id))

            total_pages = (total // limit) + (1 if total % limit != 0 else 0)
            current_page = (skip // limit) + 1

            query = (
                select(Expense)
                .options(joinedload(Expense.category))
                .offset(skip)
                .limit(limit)
                .where(Expense.user_id == user_id)
            )
            result = await session.execute(query)
            expenses = result.unique().scalars().all()

            expense_responses = [
                ExpenseDisplay.model_validate(expense) for expense in expenses
            ]

            pagination = {
                "total": total,
                "limit": limit,
                "skip": skip,
                "current_page": current_page,
                "total_pages": total_pages,
                "has_previous": current_page > 1,
                "has_next": current_page < total_pages,
            }

            return {"expenses": expense_responses, "pagination": pagination}

        except Exception as e:
            raise InternalServerError(f"{e}")

    @staticmethod
    async def create_category_if_none(session: AsyncSession, name: str, user_id: int):
        try:
            category = await session.execute(
                select(ExpenseCategory).filter_by(name=name, user_id=user_id)
            )
            category = category.scalars().first()
            if not category:
                category = ExpenseCategory(name=name, user_id=user_id)
                session.add(category)
                await session.commit()
                await session.refresh(category)
            return category
        except Exception as e:
            await session.rollback()
            raise InternalServerError(f"{e}")

    @staticmethod
    async def update_expense_category(
        session: AsyncSession,
        user_id: int,
        category_id: int,
        name: str,
    ):
        try:
            query = select(ExpenseCategory).where(
                and_(
                    ExpenseCategory.id == category_id,
                    ExpenseCategory.user_id == user_id,
                )
            )
            result = await session.execute(query)

            category = result.scalar_one_or_none()
            if not category:
                raise NotFound(f"Category {category_id} was not found.")
            category.name = name
            session.add(category)
            await session.commit()
            await session.refresh(category)

            return ExpenseCategoryDisplay.model_validate(category)
        except Exception as e:
            await session.rollback()
            raise InternalServerError(f"{e}")

    @staticmethod
    async def delete_expense_category(
        session: AsyncSession,
        user_id: int,
        category_id: int,
    ):
        try:
            query = select(ExpenseCategory).where(
                and_(
                    ExpenseCategory.id == category_id,
                    ExpenseCategory.user_id == user_id,
                )
            )
            result = await session.execute(query)

            category = result.scalar_one_or_none()
            if not category:
                raise NotFound(f"Category {category_id} was not found.")

            await session.delete(category)
            await session.commit()

            return {"message": f"Expense {category_id} was deleted successfully."}
        except NotFound as e:
            raise e
        except SQLAlchemyError as e:
            await session.rollback()
            raise InternalServerError(f"{e}")
        except Exception as e:
            await session.rollback()
            raise InternalServerError(f"{e}")

    @staticmethod
    async def read_all_expense_categories(
        session: AsyncSession,
        user_id: int,
    ):
        try:
            query = select(ExpenseCategory).where(ExpenseCategory.user_id == user_id)
            result = await session.execute(query)

            categories = result.scalars().all()
            category_responses = [
                ExpenseCategoryDisplay.model_validate(category)
                for category in categories
            ]

            return category_responses
        except Exception as e:
            raise InternalServerError(f"{e}")

    @staticmethod
    async def filter_expenses_by_category(
        session: AsyncSession,
        user_id: int,
        category: str,
    ):
        try:
            query = (
                select(ExpenseCategory)
                .where(
                    and_(
                        ExpenseCategory.user_id == user_id,
                        ExpenseCategory.name.ilike(f"%{category}%"),
                    )
                )
                .options(joinedload(ExpenseCategory.expenses))
            )
            result = await session.execute(query)
            filtered_result = result.unique().scalar_one_or_none()
            if not filtered_result:
                raise NotFound(f"Category {category} was not found.")

            return ExpenseCategoryInDB.model_validate(filtered_result)

        except NotFound as e:
            raise e
        except SQLAlchemyError as e:
            raise InternalServerError(f"{e}")
        except Exception as e:
            raise InternalServerError(f"{e}")
