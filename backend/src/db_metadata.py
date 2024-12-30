from datetime import date
from typing import final

from sqlalchemy import Column, Date, Float, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# SQLAlchemy Models
@final
class ProductPrice(Base):
    __tablename__ = "product_prices"
    id = Column(Integer, primary_key=True, index=True)
    product = Column(String, index=True, nullable=False)
    seller = Column(String, nullable=False)
    link = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    date = Column(Date, default=date.today)
