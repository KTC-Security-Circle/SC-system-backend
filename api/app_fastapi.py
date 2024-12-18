import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from api.app.database.engine import get_engine
from api.app.routers.auth import router as auth_app_router
from api.app.routers.chats import router as chat_app_router
from api.app.routers.sessions import router as session_app_router
from api.app.routers.users import router as user_app_router
from api.app.routers.school_info import router as school_info_app_router

# from api.demo.routers.chats import router as chatlog_demo_router
# from api.demo.routers.sessions import router as session_demo_router
# from api.demo.routers.users import router as user_demo_router
from api.logger import getLogger

logger = getLogger("azure_functions.fastapi")
logger.setLevel(logging.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()

    # # 既存のテーブルを削除してから再作成する(sqliteでテストする用)
    # SQLModel.metadata.drop_all(engine)

    SQLModel.metadata.create_all(engine)
    logger.info("Database connected and tables created.")
    yield
    engine.dispose()
    logger.info("Database connection closed.")

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:7071",
    "https://sc-test-api.azurewebsites.net",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_app_router, prefix="/auth")
app.include_router(user_app_router, prefix="/api")
app.include_router(session_app_router, prefix="/api")
app.include_router(chat_app_router, prefix="/api")
app.include_router(school_info_app_router, prefix="/api")
# app.include_router(user_demo_router, prefix="/api")
# app.include_router(session_demo_router, prefix="/api")
# app.include_router(chatlog_demo_router, prefix="/api")
