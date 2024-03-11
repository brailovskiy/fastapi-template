from asyncio import current_task
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from loguru import logger
from sqlalchemy import literal, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

PostgresBase = declarative_base()


@dataclass
class Database:
    CONNECT_KWARGS = {"max_overflow": 10, "pool_pre_ping": True, "pool_recycle": 3600, "echo_pool": True}

    def __init__(self, db_connect_url: str, db_alias: str, connect_kwargs: dict[str, Any], debug: bool = False) -> None:
        self.engine = create_async_engine(url=db_connect_url, **connect_kwargs, echo=debug)
        self._db_alias = db_alias
        self._async_session = async_scoped_session(
            async_sessionmaker(
                autocommit=False,
                autoflush=False,
                class_=AsyncSession,
                expire_on_commit=False,
                bind=self.engine,
            ),
            scopefunc=current_task,
        )

    async def create_tables_by_base(self, sqlalchemy_base: Any) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(sqlalchemy_base.metadata.create_all)

    async def drop_tables_by_base(self, sqlalchemy_base: Any) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(sqlalchemy_base.metadata.drop_all)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self._async_session()
        try:
            yield session
        except Exception as session_error:
            logger.exception("Session rollback because of exception")
            await session.rollback()
            raise session_error
        finally:
            await session.close()
            await self._async_session.remove()

    async def disconnect(self) -> None:
        await self.engine.dispose()

    async def get_status(self) -> dict[str, str]:
        async with self.session() as session:
            try:
                db_status = await session.execute(
                    select(
                        literal("ready").label("status"),
                        literal(self._db_alias).label("name"),
                    ),
                )
                return db_status.first()._asdict()  # type: ignore
            except Exception:
                return {"name": self._db_alias, "status": "unreachable"}
