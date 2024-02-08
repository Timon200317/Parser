import logging
from pymongo import MongoClient

from common.mongo_config import MONGO_URI, MONGO_INITDB_DATABASE


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
