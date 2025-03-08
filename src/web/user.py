from fastapi import APIRouter, HTTPException


from src.schema import UserLogin, UserDisplay, UserCreate
from src.service import UserService
from .dependencies.db_dependecy import db_dependency
from .dependencies.user_auth import generate_token, user_dependency

router = APIRouter(tags=["User Endpoints"])

user_service = UserService(db_dependency)


@router.post("/register", response_model=UserDisplay)
async def register(register_form: UserCreate):
    try:
        return await user_service.register_user(register_form)
    except HTTPException as e:
        raise e


@router.post("/token", response_model=dict)
async def login(login_form: UserLogin, db: db_dependency):
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
