from datetime import datetime
from typing import Optional

from bson import Decimal128
from pydantic import BaseModel, Field


class CategoryModel(BaseModel):
    """Model for Lamoda Category"""
    gender: str = Field(max_length=30)
    category_name: str = Field(max_length=30)
    subcategory_name: str = Field(max_length=60)
    link: str = Field(max_length=256)
    date_created: datetime = Field(datetime.today(), frozen=True, repr=False)


class ItemModel(BaseModel):
    """Model for Lamoda Item"""
    item_category: CategoryModel
    item_name:  str = Field(max_length=100)
    price: Decimal128
    brand: str = Field(max_length=100)
    color: Optional[str]
    size: Optional[dict]
    date_created: datetime = Field(datetime.today(), frozen=True, repr=False)


