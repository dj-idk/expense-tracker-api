import uuid

from fastapi import Depends, Response
from typing import Annotated
from fastapi.security import APIKeyCookie
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.service import UserService
from src.schema import UserLogin, UserDisplay
from src.utils import settings, Unauthorized
from src.data import AccessToken, User, get_db


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
TOKEN_COOKIE_NAME = settings.TOKEN_COOKIE_NAME
CSRF_TOKEN_SECRET = settings.CSRF_TOKEN_SECRET

db_dependency = Annotated[AsyncSession, Depends(get_db)]

api_key_cookie = APIKeyCookie(name=TOKEN_COOKIE_NAME)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generates a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update(
        {
            "exp": expire,
            "iss": "tracker",
            "aud": "tracker-ui",
            "jti": str(uuid.uuid4()),
        }
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def generate_token(
    response: Response, session: AsyncSession, login_form: UserLogin
) -> dict:
    """Authenticates a user and returns a JWT token if successful."""
    try:
        user = await UserService.authenticate_user(session, login_form)
        if not user:
            raise Unauthorized("Invalid credentials")

        access_token = create_access_token({"sub": user.username})
        decoded_token = jwt.decode(
            access_token, SECRET_KEY, algorithms=[ALGORITHM], audience="tracker-ui"
        )
        jti = decoded_token.get("jti")
        new_token = AccessToken(
            id=jti,
            user_id=user.id,
            is_revoked=False,
            created_at=datetime.now(timezone.utc),
        )

        session.add(new_token)
        await session.commit()

        response.set_cookie(
            key=TOKEN_COOKIE_NAME,
            value=access_token,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=True,
            httponly=True,
            samesite="lax",
        )

        return {"access_token": access_token, "token_type": "bearer"}

    except Unauthorized as e:
        raise e
    except Exception as e:
        await session.rollback()
        raise e


async def get_current_user(
    session: db_dependency,
    token: str = Depends(api_key_cookie),
) -> UserDisplay:
    """Retrieves the current user from a JWT token."""
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM], audience="tracker-ui"
        )

        username: str = payload.get("sub")
        jti: str = payload.get("jti")
        if not username or not jti:
            raise Unauthorized("Could not validate credentials")

        query = select(AccessToken).where(AccessToken.id == jti)
        result = await session.execute(query)
        token: AccessToken | None = result.scalar_one_or_none()

        if not token and not token.is_revoked:
            raise Unauthorized("Token has been revoked")

        user: User = token.user
        if not user:
            raise Unauthorized("User not found")

        return UserDisplay.model_validate(user)
    except Unauthorized as e:
        raise e
    except JWTError:
        raise Unauthorized("Invalid token")


async def revoke_token(session: AsyncSession, token: str = Depends(api_key_cookie)):
    """Marks a token as revoked in the database."""
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM], audience="tracker-ui"
        )
        jti: str = payload.get("jti")

        query = select(AccessToken).where(AccessToken.id == jti)
        result = await session.execute(query)
        db_token = result.scalar_one_or_none()

        if db_token:
            db_token.is_revoked = True
            await session.commit()

        return {"message": "You've been successfully logged out"}
    except JWTError:
        raise Unauthorized("Invalid token")


user_dependency = Annotated[UserDisplay, Depends(get_current_user)]
