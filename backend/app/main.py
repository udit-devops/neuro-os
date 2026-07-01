from fastapi import FastAPI
from app.api.health.routes import router as health_router
from app.core.config import settings
from contextlib import asynccontextmanager
from app.db.init_db import init_db
from app.api.users.routes import router as users_router
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)
app.include_router(health_router)
app.include_router(users_router)

@app.get("/")
def root():
    return {"message": "welcome boiss"}