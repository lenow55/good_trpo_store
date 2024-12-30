from datetime import date

from pydantic import BaseModel, HttpUrl, field_serializer


# Pydantic Models
class PriceRecord(BaseModel):
    product: str
    seller: str
    link: HttpUrl
    price: float
    date: date | None

    @field_serializer("link", when_used="always")
    def serialize_link(self, link: HttpUrl) -> str:
        return link.unicode_string()


class PriceRecordResponse(PriceRecord):
    id: int

    class Config:
        from_attributes: bool = True
