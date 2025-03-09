from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.data import init_db
from .user import router as user_router
from src.utils import InternalServerError


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/healthy")
async def check_health():
    try:
        return {"status": "healthy"}
    except:
        raise InternalServerError()


app.include_router(user_router)
