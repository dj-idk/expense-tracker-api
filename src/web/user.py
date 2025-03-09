from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from src.schema import UserLogin, UserDisplay, UserCreate
from src.service import UserService
from .dependencies.user_dependencies import (
    db_dependency,
    user_dependency,
    generate_token,
)

router = APIRouter(tags=["User Endpoints"])


@router.post("/register", response_model=UserDisplay)
async def register(register_form: UserCreate, db: db_dependency):
    try:
        return await UserService.register_user(db, register_form)
    except HTTPException as e:
        raise e


@router.post("/token", response_model=dict)
async def login(
    db: db_dependency, login_form: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    try:
        return await generate_token(db, login_form)
    except HTTPException as e:
        raise e


@router.get("/users/me", response_model=UserDisplay)
async def read_current_user(current_user: user_dependency):
    try:
        return current_user
    except HTTPException as e:
        raise e
