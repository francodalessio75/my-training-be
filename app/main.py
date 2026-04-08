import logging
from contextlib import asynccontextmanager
from beanie import init_beanie
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import db
from app.models.exercise import Exercise
from app.models.muscle_group import MuscleGroup
from app.models.session import Session
from app.models.training_type import TrainingType
from app.models.user import User
from app.auth.router import router as auth_router
from app.routers.training_types import router as training_types_router
from app.routers.muscle_groups import router as muscle_groups_router
from app.routers.exercises import router as exercises_router
from app.routers.sessions import router as sessions_router
from app.routers.workout_units import router as workout_units_router
from app.routers.executed_sets import router as executed_sets_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("mytraining")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie(
        database=db,
        document_models=[User, Session, Exercise, TrainingType, MuscleGroup],
    )
    logger.info("Beanie initialized")
    yield


app = FastAPI(title="MyTraining", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

PREFIX = "/api/v1"
app.include_router(auth_router, prefix=PREFIX)
app.include_router(training_types_router, prefix=PREFIX)
app.include_router(muscle_groups_router, prefix=PREFIX)
app.include_router(exercises_router, prefix=PREFIX)
app.include_router(sessions_router, prefix=PREFIX)
app.include_router(workout_units_router, prefix=PREFIX)
app.include_router(executed_sets_router, prefix=PREFIX)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred. Please try again."})
