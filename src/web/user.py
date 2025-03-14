from fastapi import APIRouter, HTTPException, Depends, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from src.schema import UserDisplay, UserCreate
from src.service import UserService
from .dependencies.user_dependencies import (
    db_dependency,
    user_dependency,
    generate_token,
    revoke_token,
    api_key_cookie,
)

router = APIRouter(tags=["User Endpoints"])


@router.post(
    "/register", response_model=UserDisplay, status_code=status.HTTP_201_CREATED
)
async def register(register_form: UserCreate, db: db_dependency):
    try:
        return await UserService.register_user(db, register_form)
    except HTTPException as e:
        raise e


@router.post("/token", response_model=dict, status_code=status.HTTP_201_CREATED)
async def login(
    response: Response,
    db: db_dependency,
    login_form: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    try:
        return await generate_token(response, db, login_form)
    except HTTPException as e:
        raise e


@router.get("/users/me")
async def read_current_user(current_user: user_dependency):
    try:
        return current_user
    except HTTPException as e:
        raise e


@router.post("/logout")
async def logout(
    db: db_dependency,
    current_user: user_dependency,
):
    try:
        return await revoke_token(db, api_key_cookie)
    except HTTPException as e:
        raise e
