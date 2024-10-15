from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.v1.api import api_router
from app.database import engine
from app import models





@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")
