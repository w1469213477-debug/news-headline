import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# 1.创建异步引擎
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
if not ASYNC_DATABASE_URL:
    raise RuntimeError("ASYNC_DATABASE_URL is not configured")
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true",
    pool_size=10,
    max_overflow=20,
)

# 2.创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 依赖项
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

