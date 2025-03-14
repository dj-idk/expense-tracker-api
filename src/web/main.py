from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette_csrf import CSRFMiddleware
from contextlib import asynccontextmanager

from src.data import init_db, engine
from .user import router as user_router
from .expense import router as expense_router
from src.utils import InternalServerError, settings, get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_settings.cache_clear()
    await init_db()
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CSRFMiddleware,
    secret=settings.CSRF_TOKEN_SECRET,
    sensitive_cookies="Authorization",
    cookie_domain="localhost",
)


@app.get("/healthy")
async def check_health():
    try:
        return {"status": "healthy"}
    except:
        raise InternalServerError()


app.include_router(user_router)
app.include_router(expense_router)
