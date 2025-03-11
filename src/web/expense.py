from fastapi import APIRouter, HTTPException, status, Path, Query, Form
from typing import List, Dict

from src.schema import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseDisplay,
    ExpenseListResponse,
    FilteredExpenses,
    FilteredExpenseCategory,
    ExpenseCategoryDisplay,
)
from src.service import ExpenseService
from .dependencies.user_dependencies import db_dependency, user_dependency

router = APIRouter(prefix="/expense", tags=["Expense Management Endpoints"])


@router.post("/", response_model=ExpenseDisplay, status_code=status.HTTP_201_CREATED)
async def add_expense(db: db_dependency, user: user_dependency, expense: ExpenseCreate):
    try:
        return await ExpenseService.add_expense(db, expense, user.id)
    except HTTPException as e:
        raise e


@router.put("/{expense_id}", response_model=ExpenseDisplay)
async def update_expense(
    db: db_dependency,
    user: user_dependency,
    update_form: ExpenseUpdate,
    expense_id: int = Path(..., ge=1),
):
    try:
        return await ExpenseService.update_expense(db, update_form, user.id, expense_id)
    except HTTPException as e:
        raise e


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    db: db_dependency,
    user: user_dependency,
    expense_id: int = Path(..., ge=1),
):
    try:
        return await ExpenseService.delete_expense(db, user.id, expense_id)
    except HTTPException as e:
        raise e


@router.get("/", response_model=ExpenseListResponse)
async def read_all_expenses(
    db: db_dependency,
    user: user_dependency,
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    try:
        return await ExpenseService.get_all_expenses(db, user.id, limit, skip)
    except HTTPException as e:
        raise e


@router.get("/search", response_model=List[ExpenseDisplay])
async def search_expenses_with_description(
    db: db_dependency,
    user: user_dependency,
    description: str = Query(None, max_length=50),
):
    try:
        return await ExpenseService.search_expenses_by_description(
            db, user.id, description
        )
    except HTTPException as e:
        raise e


@router.get("/weekly", response_model=FilteredExpenses)
async def filter_expenses_by_last_weeks(
    db: db_dependency,
    user: user_dependency,
    weeks: int = Query(1, ge=1),
):
    try:
        return await ExpenseService.filter_expenses_by_last_weeks(db, user.id, weeks)
    except HTTPException as e:
        raise e


@router.get("/category/{category}", response_model=FilteredExpenseCategory)
async def filter_expenses_by_category(
    db: db_dependency,
    user: user_dependency,
    category: str,
):
    try:
        return await ExpenseService.filter_expenses_by_category(db, user.id, category)
    except HTTPException as e:
        raise e


@router.post(
    "/category",
    response_model=ExpenseCategoryDisplay,
    status_code=status.HTTP_201_CREATED,
)
async def create_expense_category(
    db: db_dependency,
    user: user_dependency,
    name: str = Form(..., max_length=100),
):
    try:
        return await ExpenseService.create_category_if_none(db, name, user.id)
    except HTTPException as e:
        raise e


@router.put("/category/{category_id}", response_model=ExpenseCategoryDisplay)
async def update_expense_category(
    db: db_dependency,
    user: user_dependency,
    new_name: str = Form(..., max_length=100),
    category_id: int = Path(..., ge=1),
):
    try:
        return await ExpenseService.update_expense_category(
            db, user.id, category_id, new_name
        )
    except HTTPException as e:
        raise e


@router.delete("/category/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_category(
    db: db_dependency,
    user: user_dependency,
    category_id: int,
):
    try:
        return await ExpenseService.delete_expense_category(db, user.id, category_id)
    except HTTPException as e:
        raise e


@router.get("/category", response_model=List[ExpenseCategoryDisplay])
async def read_all_categories(
    db: db_dependency,
    user: user_dependency,
):
    try:
        return await ExpenseService.read_all_expense_categories(db, user.id)
    except HTTPException as e:
        raise e
