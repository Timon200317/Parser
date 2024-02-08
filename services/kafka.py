import logging
import asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

from common.config import kafka_settings
from parsers.lamoda_parser import get_lamoda_categories, get_lamoda_items


class KafkaService:
    def __init__(self):
        try:
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=kafka_settings.bootstrap_servers
            )
            self.topics = [
                NewTopic(name="lamoda", num_partitions=3, replication_factor=1),
            ]
            self.admin_client.create_topics(self.topics)
        except Exception:
            pass
        self.consumer = AIOKafkaConsumer(
            bootstrap_servers=kafka_settings.bootstrap_servers
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=kafka_settings.bootstrap_servers
        )
        self.logger = logging.getLogger("uvicorn.error")

    async def send_message(self, topic, message, key):
        self.logger.info("Starting Kafka")
        await self.producer.start()
        try:
            self.logger.info(f"Sending a message: {message}")
            await self.producer.send(topic, message, key)
            self.logger.info("Message sent")
        except Exception as e:
            self.logger.error(f"Got an error {e} when sending a message {message}")
        finally:
            await self.producer.stop()

    async def process_lamoda_message(self, message, key):
        try:
            self.logger.info(f"Processing a message: {message}")
            if key == b"categories":
                await get_lamoda_categories()
            elif key == b"items":
                await get_lamoda_items()
        except Exception as e:
            self.logger.error(f"Got an error {e} when processing a message")

    async def consume_messages(self, topics):
        self.consumer.subscribe(topics)
        try:
            await self.consumer.start()
            async for message in self.consumer:
                self.logger.info(f"Received a message: {message}")
                if message.topic == "lamoda":
                    await self.process_lamoda_message(message.value, message.key)
        except Exception as e:
            self.logger.error(f"Got an error {e} when consuming a message")
        finally:
            await self.consumer.stop()
