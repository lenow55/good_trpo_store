import asyncio
import os

from src.database import database
from src.db_metadata import Base


db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./prices.db")
database.setup(db_url=db_url)


async def main():
    if database.async_engine:
        async with database.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("Tables init success")
    else:
        raise RuntimeError("Init Database before")


# Main entry point
if __name__ == "__main__":
    asyncio.run(main())
