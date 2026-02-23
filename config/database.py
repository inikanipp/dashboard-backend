import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL tidak ditemukan di file .env")

engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base

Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        # Ini akan membuat semua tabel yang terdaftar di model Anda
        await conn.run_sync(Base.metadata.create_all)