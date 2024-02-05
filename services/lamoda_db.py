import logging
import os
from typing import List

from pydantic import TypeAdapter
from pymongo import MongoClient

# from common.config import mongo_settings
from models.lamoda_models import (
    CategoryModel,
    ItemModel, UpdateCategoryModel,
)

logger = logging.getLogger()

MONGO_INITDB_DATABASE = os.getenv('MONGO_INITDB_DATABASE')
MONGO_INITDB_ROOT_USERNAME = os.getenv('MONGO_INITDB_ROOT_USERNAME')
MONGO_INITDB_ROOT_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
MONGO_INITDB_PORT = os.getenv('MONGO_INITDB_PORT')
MONGO_INITDB_HOST = os.getenv('MONGO_INITDB_HOST')

MONGO_URI = (f"{MONGO_INITDB_DATABASE}://"
             + f"{MONGO_INITDB_ROOT_USERNAME}:"
             + f"{MONGO_INITDB_ROOT_PASSWORD}"
             + f"@{MONGO_INITDB_DATABASE}:{MONGO_INITDB_PORT}")


class LamodaServiceDatabase:
    def __init__(self):
        print(MONGO_URI)
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

    def find_lamoda_item(self):
        return

    def update_lamoda_item(self):
        return

    def delete_lamoda_item(self):
        return
