from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from src.data import User, Expense, ExpenseCategory
from src.schema import (
    ExpenseCreate,
    ExpenseUpdate,
)
from src.utils import (
    Unauthorized,
    InternalServerError,
    NotFound,
)


class ExpenseService:
    @staticmethod
    async def add_expense(session: AsyncSession, expense: ExpenseCreate, user_id: int):
        try:
            user = await session.get(User, user_id)
            if not user:
                raise Unauthorized("Invalid User Credentials.")

            category = await ExpenseService.create_category_if_none(
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
            expense_with_relations = await session.get(
                Expense, new_expense.id, options=[selectinload(Expense.category)]
            )

            return expense_with_relations
        except SQLAlchemyError as e:
            await session.rollback()
            raise InternalServerError(f"{e}")

    @staticmethod
    async def update_expense(
        session: AsyncSession, update_form: ExpenseUpdate, user_id: int, expense_id: int
    ):
        try:
            query = (
                select(Expense)
                .where(and_(Expense.id == expense_id, Expense.user_id == user_id))
                .options(selectinload(Expense.category))
            )
            result = await session.execute(query)
            expense = result.scalar_one_or_none()
            if not expense:
                raise NotFound(f"Expense {expense_id} was not found.")

            update_data = update_form.model_dump(exclude_unset=True)
            if "category" in update_data:
                category = await ExpenseService.create_category_if_none(
                    session, update_data["category"], user_id
                )
                update_data["category_id"] = category.id
                del update_data["category"]

            for key, value in update_data.items():
                setattr(expense, key, value)

            await session.commit()
            await session.refresh(expense)

            return expense

        except SQLAlchemyError as e:
            await session.rollback()
            raise InternalServerError(f"{e}")

    @staticmethod
    async def delete_expense(session: AsyncSession, user_id: int, expense_id: int):
        try:
            expense = await session.get(Expense, expense_id)

            if not expense or expense.user_id != user_id:
                raise NotFound(f"Expense {expense_id} not found or unauthorized.")

            await session.delete(expense)
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise InternalServerError(f"Database error: {str(e)}") from e

    @staticmethod
    async def search_expenses_by_description(
        session: AsyncSession, user_id: int, description: str
    ):
        try:
            query = (
                select(Expense)
                .filter(Expense.description.ilike(f"%{description}%"))
                .options(joinedload(Expense.category))
                .where(Expense.user_id == user_id)
            )
            result = await session.execute(query)
            expenses = result.scalars().all()

            return expenses
        except SQLAlchemyError as e:
            await session.rollback()
            raise InternalServerError(f"Database error: {str(e)}") from e

    @staticmethod
    async def get_all_expenses(
        session: AsyncSession, user_id: int, limit: int = 10, skip: int = 0
    ):
        try:

            total = await session.scalar(func.count(Expense.id))

            total_pages = (total // limit) + (1 if total % limit != 0 else 0)
            current_page = (skip // limit) + 1

            query = (
                select(Expense)
                .where(Expense.user_id == user_id)
                .options(joinedload(Expense.category))
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(query)
            expenses = result.scalars().all()

            pagination = {
                "total": total,
                "limit": limit,
                "skip": skip,
                "current_page": current_page,
                "total_pages": total_pages,
                "has_previous": current_page > 1,
                "has_next": current_page < total_pages,
            }

            return {"expenses": expenses, "pagination": pagination}

        except SQLAlchemyError as e:
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
                .options(selectinload(ExpenseCategory.expenses))
            )
            result = await session.execute(query)
            filtered_result = result.unique().scalar_one_or_none()
            if not filtered_result:
                raise NotFound(f"Category {category} was not found.")

            expenses_count = len(filtered_result.expenses)
            total_amount = sum((expense.amount for expense in filtered_result.expenses))

            summary = {
                "total_count": expenses_count,
                "total_amount": total_amount,
            }

            return {
                "result": filtered_result,
                "summary": summary,
            }

        except SQLAlchemyError as e:
            raise InternalServerError(f"{e}")

    @staticmethod
    async def filter_expenses_by_last_weeks(
        session: AsyncSession,
        user_id: int,
        weeks: int = 1,
    ):

        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(weeks=weeks)

            query = (
                select(Expense)
                .where(
                    and_(
                        Expense.created_at >= cutoff_date,
                        Expense.user_id == user_id,
                    )
                )
                .options(joinedload(Expense.category))
            )

            result = await session.execute(query)
            expenses = result.scalars().all()

            expenses_count = len(expenses)
            total_amount = sum((expense.amount for expense in expenses))

            summary = {
                "total_count": expenses_count,
                "total_amount": total_amount,
            }

            return {
                "summary": summary,
                "result": expenses,
            }

        except SQLAlchemyError as e:
            raise InternalServerError(f"Database error: {e}")

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
        except SQLAlchemyError as e:
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

            return category
        except SQLAlchemyError as e:
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

        except SQLAlchemyError as e:
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

            return categories
        except SQLAlchemyError as e:
            raise InternalServerError(f"{e}")
