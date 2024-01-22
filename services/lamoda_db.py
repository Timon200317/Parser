import logging
import os
from typing import List

from pydantic import TypeAdapter
from pymongo import MongoClient

# from common.config import mongo_settings
from models.lamoda_models import (
    CategoryModel,
    ItemModel,
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

    def find_lamoda_category(self):
        return

    def update_lamoda_category(self):
        return

    def delete_lamoda_category(self):
        return

    async def parse_lamoda_items(self):
        return

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
