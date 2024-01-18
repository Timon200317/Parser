import logging
from typing import List

from pydantic import TypeAdapter
from pymongo import MongoClient

from common.config import mongo_settings
from models.lamoda_models import (
    CategoryModel,
    ItemModel,
)

logger = logging.getLogger()


class LamodaServiceDatabase:
    def __init__(self):
        self.mongo_client = MongoClient(mongo_settings.url)
        self.database = self.mongo_client[mongo_settings.name]

        try:
            self.mongo_client.admin.command("ping")
            logger.info(
                "Pinged your deployment. You successfully connected to MongoDB!"
            )
        except Exception as e:
            logger.error(e)

    """CRUD Functions for work with MongoDB"""

    async def parse_lamoda_categories(self):
        return

    def list_lamoda_categories(self):
        return

    def find_lamoda_category(self):
        return

    def update_lamoda_category(self):
        return

    def delete_lamoda_category(self):
        return

    async def parse_lamoda_items(self):
        return

    def list_lamoda_items(self):
        return

    def find_lamoda_item(self):
        return

    def update_lamoda_item(self):
        return

    def delete_lamoda_item(self):
        return
