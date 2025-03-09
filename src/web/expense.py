from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from src.schema import ExpenseCreate, ExpenseUpdate
from src.service import UserService
from .dependencies.user_dependencies import db_dependency, user_dependency

router = APIRouter(prefix="/expense", tags=["Expense Management Endpoints"])


@router.post("/")
async def add_expense(db: db_dependency, user: user_dependency, expense: ExpenseCreate):
    try:
        return await UserService.add_expense(db, expense, user.id)
    except HTTPException as e:
        raise e


@router.put("/{expense_id}")
async def update_expense(
    db: db_dependency,
    user: user_dependency,
    update_form: ExpenseUpdate,
    expense_id: int,
):
    try:
        return await UserService.update_expense(db, update_form, user.id, expense_id)
    except HTTPException as e:
        raise e


@router.delete("/{expense_id}")
async def delete_expense(
    db: db_dependency,
    user: user_dependency,
    expense_id: int,
):
    try:
        return await UserService.delete_expense(db, user.id, expense_id)
    except HTTPException as e:
        raise e


@router.get("/")
async def read_all_expenses(
    db: db_dependency, user: user_dependency, limit: int = 10, skip: int = 0
):
    try:
        return await UserService.get_all_expenses(db, user.id, limit, skip)
    except HTTPException as e:
        raise e


@router.get("/search/{description}")
async def search_expenses_with_definition(
    db: db_dependency,
    user: user_dependency,
    description: str,
):
    try:
        return await UserService.search_expenses_by_description(
            db, user.id, description
        )
    except HTTPException as e:
        raise e


@router.post("/category")
async def create_expense_category(
    db: db_dependency,
    user: user_dependency,
    name: str,
):
    try:
        return await UserService.create_category_if_none(db, name, user.id)
    except HTTPException as e:
        raise e


@router.put("/category")
async def update_expense_category(
    db: db_dependency,
    user: user_dependency,
    category_id: int,
    new_name: str,
):
    try:
        return await UserService.update_expense_category(
            db, user.id, category_id, new_name
        )
    except HTTPException as e:
        raise e


@router.delete("/category/{category_id}")
async def delete_expense_category(
    db: db_dependency,
    user: user_dependency,
    category_id: int,
):
    try:
        return await UserService.delete_expense_category(db, user.id, category_id)
    except HTTPException as e:
        raise e


@router.get("/category")
async def read_all_categories(
    db: db_dependency,
    user: user_dependency,
):
    try:
        return await UserService.read_all_expense_categories(db, user.id)
    except HTTPException as e:
        raise e


@router.get("/category/{category}")
async def filter_expenses_by_category(
    db: db_dependency,
    user: user_dependency,
    category: str,
):
    try:
        return await UserService.filter_expenses_by_category(db, user.id, category)
    except HTTPException as e:
        raise e
