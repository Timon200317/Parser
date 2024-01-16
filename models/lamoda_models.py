from datetime import datetime
from typing import Optional

from bson.decimal128 import Decimal128
from pydantic import BaseModel, Field


class CategoryModel(BaseModel):
    category_name: str = Field(max_length=50)
    subcategory_name: str = Field(max_length=80)
    link: str = Field(max_length=100)
    gender: str = Field(max_length=15)
    date_created: datetime = Field(datetime.today(), frozen=True, repr=False)


class ItemModel(BaseModel):
    name: str
    article: str = Field(max_length=15)
    category: CategoryModel
    price: Decimal128
    brand: str = Field(max_length=40)
    color: Optional[str]
    description: Optional[str]
    date_created: datetime = Field(datetime.today(), frozen=True, repr=False)

