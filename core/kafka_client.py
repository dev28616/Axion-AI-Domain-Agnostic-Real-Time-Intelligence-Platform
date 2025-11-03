import asyncio
import os
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError, TopicAuthorizationFailedError
from typing import Union, List

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL", "kafka:29092")
MAX_RETRIES = 15
RETRY_DELAY = 5

async def connect_with_retry(client_factory, group_id_for_logging: str = "PRODUCER"):
    for attempt in range(MAX_RETRIES):
        try:
            client = client_factory()
            await client.start()
            print(f"[{group_id_for_logging}]: Successfully connected to Kafka on attempt {attempt + 1}.")
            return client
        except (KafkaConnectionError, TopicAuthorizationFailedError) as e:
            if attempt < MAX_RETRIES - 1:
                print(f"[{group_id_for_logging}]: Kafka connection failed. Retrying in {RETRY_DELAY}s... (Attempt {attempt + 2}/{MAX_RETRIES})")
                await asyncio.sleep(RETRY_DELAY)
            else:
                print(f"[{group_id_for_logging}]: Kafka connection failed after all retries. Exiting. Error: {e}")
                raise
    return None

async def get_kafka_producer():
    loop = asyncio.get_running_loop()
    def factory():
        return AIOKafkaProducer(loop=loop, bootstrap_servers=KAFKA_BROKER_URL)
    return await connect_with_retry(factory)

async def get_kafka_consumer(topics: Union[str, List[str]], group_id: str):
    loop = asyncio.get_running_loop()
    topic_list = [topics] if isinstance(topics, str) else topics
    def factory():
        return AIOKafkaConsumer(*topic_list, loop=loop, bootstrap_servers=KAFKA_BROKER_URL, group_id=group_id, request_timeout_ms=30000, auto_offset_reset='earliest')
    return await connect_with_retry(factory, group_id_for_logging=group_id)

