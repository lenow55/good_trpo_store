import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import database
from src.db_metadata import ProductPrice
from src.schemas import PriceRecord, PriceRecordResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./prices.db")
    database.setup(db_url=db_url)
    yield
    await database.shutdown()


# FastAPI application
app = FastAPI(lifespan=lifespan)


# API Endpoints
@app.post("/prices/", response_model=PriceRecordResponse)
async def add_price(record: PriceRecord, db: AsyncSession = Depends(database)):
    db_record = ProductPrice(**record.dict())
    async with db.begin():
        db.add(db_record)
    await db.refresh(db_record)
    return db_record


@app.get("/prices/", response_model=list[PriceRecordResponse])
async def get_prices(
    product: str | None = None,
    seller: str | None = None,
    db: AsyncSession = Depends(database),
):
    query = select(ProductPrice)
    if product:
        query = query.filter(ProductPrice.product == product)
    if seller:
        query = query.filter(ProductPrice.seller == seller)
    result = await db.execute(query)
    return result.scalars().all()


@app.get("/prices/{price_id}", response_model=PriceRecordResponse)
async def get_price(price_id: int, db: AsyncSession = Depends(database)):
    query = select(ProductPrice).filter(ProductPrice.id == price_id)
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Price record not found")
    return record
