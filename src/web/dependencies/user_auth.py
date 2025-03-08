from fastapi import Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.service import UserService
from src.schema import UserLogin
from src.utils import settings
from src.utils import Unauthorized
from src.data import User
from .db_dependecy import db_dependency
from src.schema import UserDisplay

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Generates a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def generate_token(db: AsyncSession, login_form: UserLogin):
    """Authenticates a user and returns a JWT token if successful."""
    user_service = UserService(db)
    user = await user_service.authenticate_user(login_form)

    if not user:
        raise Unauthorized()

    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(
    db: db_dependency,
    token: str = Depends(oauth2_scheme),
):
    """Retrieves the current user from a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise Unauthorized("Could not validate credentials")

        query = select(User).where(User.username == username)
        result = await db.execute(query)
        user = result.scalars().first()

        if not user:
            raise Unauthorized("User not found")

        return UserDisplay.model_validate(user)

    except JWTError:
        raise Unauthorized("Invalid token")


user_dependency = Annotated[UserDisplay, Depends(get_current_user)]
