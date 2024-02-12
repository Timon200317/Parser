
from typing import List
from fastapi import APIRouter, HTTPException, Body, Response, status
import logging
from fastapi_cache.decorator import cache
from models.lamoda_models import CategoryModel, ItemModel, UpdateItemModel, UpdateCategoryModel
from services.kafka import KafkaService
from services.lamoda_db import LamodaServiceDatabase

logger = logging.getLogger(__name__)
lamoda_mongo = LamodaServiceDatabase()
category_router = APIRouter()
item_router = APIRouter()

lamoda_url = "https://www.lamoda.by"

links = [
    {
        "gender": "Женщинам",
        "url": "https://www.lamoda.by/c/4153/default-women/?is_new=1&sitelink=topmenuW&l=1",
    },
    {
        "gender": "Мужчинам",
        "url": "https://www.lamoda.by/c/4152/default-men/?is_new=1&sitelink=topmenuM&l=1",
    },
    {
        "gender": "Детям",
        "url": "https://www.lamoda.by/c/4154/default-kids/?genders=boys%2Cgirls&is_new=1&sitelink=topmenuK&l=2",
    },
]


@category_router.get("/parse_categories", response_description="Parse all categories for lamoda")
async def parse_lamoda_items():
    kafka = KafkaService()
    await kafka.send_message("lamoda", b"parse lamoda categories", b"categories")
    return {"message": "Kafka message sent"}


@category_router.get(
    "/{gender}/{subcategory}",
    response_description="Retrieve a specific category by gender and subcategory",
    response_model=CategoryModel,
)
@cache(expire=15)
def get_lamoda_category(subcategory_name: str, gender: str):
    category = lamoda_mongo.find_lamoda_category(
        {"subcategory_name": subcategory_name, "gender": gender}
    )
    if category is not None:
        return category
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no category with a subcategory_name {subcategory_name} for gender {gender}",
        )


@category_router.put(
    "/{gender}/{subcategory}",
    response_description="Update a category",
    response_model=UpdateCategoryModel,
)
def update_lamoda_category(
    subcategory_name: str,
    gender: str,
    category: UpdateCategoryModel = Body(...),
):
    existing_category = lamoda_mongo.update_lamoda_category(
        {"subcategory_name": subcategory_name, "gender": gender}, category
    )
    if existing_category is not None:
        return existing_category
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no category with an subcategory_name {subcategory_name} for gender {gender}",
        )


@category_router.delete(
    "/{category}/{subcategory}", response_description="Delete a category"
)
def delete_lamoda_category(subcategory_name: str, gender: str, response: Response):
    delete_result = lamoda_mongo.delete_lamoda_category(
        {"subcategory_name": subcategory_name, "gender": gender}
    )

    if delete_result == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no category with an id subcategory_name {subcategory_name} for gender {gender}",
        )


@item_router.get("/parse_items", response_description="Parse all items for lamoda")
async def parse_lamoda_items():
    kafka = KafkaService()
    await kafka.send_message("lamoda", b"parse lamoda items", b"items")
    return {"message": "Kafka message sent"}


@category_router.get(
    "/lamoda_categories",
    response_description="List of all the categories in mongo",
    response_model=List[CategoryModel],
)
@cache(expire=15)
def list_lamoda_categories():
    categories = lamoda_mongo.list_lamoda_categories()
    return categories


@item_router.get(
    "/lamoda_items",
    response_description="List of all the items in mongo",
    response_model=List[ItemModel],
)
@cache(expire=15)
def list_lamoda_items():
    items = lamoda_mongo.list_lamoda_items()
    return items


@item_router.get(
    "/{article}",
    response_description="Retrieve a specific item by article",
    response_model=ItemModel,
)
@cache(expire=15)
def get_lamoda_item(article: str):
    item = lamoda_mongo.find_lamoda_item({"article": article})
    if item is not None:
        return item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"There is no item with an article {article}",
    )


@item_router.put(
    "/{article}",
    response_description="Update an item",
    response_model=UpdateItemModel,
)
def update_lamoda_item(
    article: str,
    item: UpdateItemModel = Body(...),
):
    existing_item = lamoda_mongo.update_lamoda_item({"article": article}, item)

    if existing_item is not None:
        return existing_item
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no item with an article {article}",
        )


@item_router.delete("/{article}", response_description="Delete an item")
def delete_lamoda_item(article: str, response: Response):
    delete_result = lamoda_mongo.delete_lamoda_item({"article": article})

    if delete_result == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"There is no item with an article {article}",
    )

