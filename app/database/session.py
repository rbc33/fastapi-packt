
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.config import db_settings

engine = create_async_engine(
    url=db_settings.DATABASE_URL,
    # url="sqlite:///sqlite.db",
    echo=True,
    # connect_args= {
    #     "check_same_thread": False
    # }
)

async def create_db_table():
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
        

async def get_session():
    async_session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session


