from abc import ABC, abstractmethod
from typing import final, override
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class Database(ABC):
    def __init__(self):
        self.async_sessionmaker: async_sessionmaker[AsyncSession] | None = None
        self.async_engine: AsyncEngine | None = None

    async def __call__(self) -> AsyncIterator[AsyncSession]:
        """For use with FastAPI Depends"""
        if not self.async_sessionmaker:
            raise ValueError("async_sessionmaker not available. Run setup() first.")
        if not self.async_engine:
            raise ValueError("async_engine not available. Run setup() first.")
        async with self.async_sessionmaker() as session:
            yield session

    async def __aenter__(self) -> AsyncSession:
        """Allow usage as an async context manager."""
        if not self.async_sessionmaker:
            raise ValueError("async_sessionmaker not available. Run setup() first.")
        if not self.async_engine:
            raise ValueError("async_engine not available. Run setup() first.")
        session = self.async_sessionmaker()
        return session

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """Ensure session cleanup."""
        if exc_type:
            # Log or handle exceptions if needed
            pass

    @abstractmethod
    def setup(self, db_url: str) -> None: ...

    @abstractmethod
    async def shutdown(self) -> None: ...


@final
class PostgresDatabase(Database):
    @override
    def setup(self, db_url: str) -> None:
        self.async_engine = create_async_engine(db_url, echo=False)
        self.async_sessionmaker = async_sessionmaker(
            self.async_engine, class_=AsyncSession
        )

    @override
    async def shutdown(self) -> None:
        if self.async_engine:
            await self.async_engine.dispose()


@final
class SqlLite3Database(Database):
    @override
    def setup(self, db_url: str) -> None:
        self.async_engine = create_async_engine(db_url, echo=False)
        self.async_sessionmaker = async_sessionmaker(
            self.async_engine, class_=AsyncSession
        )

    @override
    async def shutdown(self) -> None:
        if self.async_engine:
            await self.async_engine.dispose()


database = SqlLite3Database()
