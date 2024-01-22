from decimal import Decimal
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class CategoryModel(BaseModel):
    """Model for Lamoda Category"""
    category_name: str = Field(max_length=50)
    subcategory_name: List[str]
    link: str
    gender: str = Field(max_length=15)
    date_created: datetime = Field(datetime.today(), frozen=True, repr=False)


class ItemModel(BaseModel):
    """Model for Lamoda Item"""
    name: str
    article: str = Field(max_length=15)
    category: CategoryModel
    price: Decimal
    brand: str = Field(max_length=40)
    color: Optional[str]
    date_created: datetime = Field(datetime.today(), frozen=True, repr=False)

    class Config:
        arbitrary_types_allowed = True

