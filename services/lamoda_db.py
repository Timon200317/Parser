import logging
from typing import List

from pydantic import TypeAdapter
from pymongo import MongoClient

from common.mongo_config import MONGO_URI, MONGO_INITDB_DATABASE
from models.lamoda_models import (
    CategoryModel,
    ItemModel, UpdateItemModel, UpdateCategoryModel,
)

logger = logging.getLogger()


class LamodaServiceDatabase:
    def __init__(self):
        self.mongo_client = MongoClient(MONGO_URI)
        self.database = self.mongo_client[MONGO_INITDB_DATABASE]

        try:
            self.mongo_client.admin.command("ping")
            logger.info(
                "Pinged your deployment. You successfully connected to MongoDB!"
            )
        except Exception as e:
            logger.info(
                "Mongo in not connected"
            )

    """CRUD Functions for work with MongoDB"""

    async def parse_lamoda_categories(self, categories: List[CategoryModel]):
        self.database["LamodaCategoryModels"].delete_many({})
        for category in categories:
            self.database["LamodaCategoryModels"].insert_one(category.model_dump())

    def list_lamoda_categories(self):
        categories_dict = self.database["LamodaCategoryModels"].find()
        type_adapter = TypeAdapter(List[CategoryModel])
        categories = type_adapter.validate_python(categories_dict)
        return categories

    def find_lamoda_category(self, query):
        category_dict = self.database["LamodaCategoryModels"].find_one(query)
        if category_dict is None:
            return None
        type_adapter = TypeAdapter(CategoryModel)
        category = type_adapter.validate_python(category_dict)
        return category

    def update_lamoda_category(self, query, update: UpdateCategoryModel):
        update_result = self.database["LamodaCategoryModels"].update_one(
            query, {"$set": update.model_dump()}
        )
        if update_result.modified_count == 0:
            return None
        existing_category_dict = self.database["LamodaCategoryModels"].find_one(
            update.model_dump()
        )
        type_adapter = TypeAdapter(CategoryModel)
        existing_category = type_adapter.validate_python(existing_category_dict)
        return existing_category

    def delete_lamoda_category(self, query):
        delete_result = self.database["LamodaCategoryModels"].delete_one(query)
        return delete_result.deleted_count

    async def parse_lamoda_items(self, items: List[ItemModel]):
        for item in items:
            if (
                    self.database["LamodaItemModels"].count_documents(
                        {"article": item.article}
                    )
                    > 0
            ):
                self.database["LamodaItemModels"].find_one_and_replace(
                    {"article": item.article}, item.model_dump()
                )
            else:
                self.database["LamodaItemModels"].insert_one(item.model_dump())

    def list_lamoda_items(self):
        items_dict = self.database["LamodaItemModels"].find()
        type_adapter = TypeAdapter(List[ItemModel])
        items = type_adapter.validate_python(items_dict)
        return items

    def find_lamoda_item(self, query):
        item_dict = self.database["LamodaItemModels"].find_one(query)
        if item_dict is None:
            return None
        type_adapter = TypeAdapter(ItemModel)
        item = type_adapter.validate_python(item_dict)
        return item

    def update_lamoda_item(self, query, update: UpdateItemModel):
        update = {
            key: value
            for key, value in update.model_dump().items()
            if value is not None
        }
        update_result = self.database["LamodaItemModels"].update_one(
            query, {"$set": update}
        )
        if update_result.modified_count == 0:
            return None
        existing_item_dict = self.database["LamodaItemModels"].find_one(update)
        type_adapter = TypeAdapter(ItemModel)
        existing_item = type_adapter.validate_python(existing_item_dict)
        return existing_item

    def delete_lamoda_item(self, query):
        delete_result = self.database["LamodaItemModels"].delete_one(query)
        return delete_result.deleted_count
