from typing import AsyncGenerator
import config

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

async_egn = create_async_engine(  # 创建异步ORM引擎
    url=config.MYSQL_URL_ASYNC,
    pool_size=config.POOL_SIZE,
    pool_recycle=config.POOL_RECYCLE,
    pool_timeout=config.POOL_TIMEOUT,
    max_overflow=config.MAX_OVERFLOW,
    pool_pre_ping=True,
    connect_args={'connect_timeout': config.CONNECT_TIMEOUT}
)

async_session = async_sessionmaker(  # 异步会话构建器
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=async_egn
)


async def db_session() -> AsyncGenerator[AsyncSession, None]:  # 异步会话生成器
    async with async_session() as session:
        yield session
