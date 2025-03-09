from fastapi import Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.service import UserService
from src.schema import UserLogin, UserDisplay
from src.utils import settings, Unauthorized
from src.data import User, get_db

# Dependency for database session
db_dependency = Annotated[AsyncSession, Depends(get_db)]

# OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Security settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generates a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def generate_token(session: AsyncSession, login_form: UserLogin) -> dict:
    """Authenticates a user and returns a JWT token if successful."""
    try:
        user = await UserService.authenticate_user(session, login_form)
        if not user:
            raise Unauthorized("Invalid credentials")

        access_token = create_access_token({"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}

    except Unauthorized as e:
        raise e
    except Exception as e:
        raise e


async def get_current_user(
    db: db_dependency,
    token: str = Depends(oauth2_scheme),
) -> UserDisplay:
    """Retrieves the current user from a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise Unauthorized("Could not validate credentials")

        user = await UserService.read_user_by_username(db, username)
        if not user:
            raise Unauthorized("User not found")

        return UserDisplay.model_validate(user)
    except Unauthorized as e:
        raise e
    except JWTError:
        raise Unauthorized("Invalid token")


# Current user dependency
user_dependency = Annotated[UserDisplay, Depends(get_current_user)]
