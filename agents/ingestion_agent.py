import asyncio
import json
import importlib
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.kafka_client import get_kafka_producer, get_kafka_consumer
from core.schemas import RawEvent

INPUT_TOPIC = "user-input-events"
CONSUMER_GROUP = "ingestion-agent-group"

async def main(config=None): 
    consumer = await get_kafka_consumer(INPUT_TOPIC, CONSUMER_GROUP)
    producer = await get_kafka_producer()
    dsp_configs = {}
    print("[INGESTION]: Running in UI Mode. Listening for user input.")
    try:
        async for msg in consumer:
            try:
                input_data = json.loads(msg.value.decode('utf-8'))
                domain = input_data.get("domain")
                event_data = input_data.get("data")
                if not domain or not event_data:
                    print(f"[INGESTION-WARN]: Skipping invalid message.")
                    continue
                if domain not in dsp_configs:
                    dsp_module = importlib.import_module(f"dsps.{domain}.config")
                    dsp_configs[domain] = getattr(dsp_module, f"{domain.capitalize()}DSPConfig")
                config = dsp_configs[domain]
                output_topic = config.TOPIC_RAW_EVENTS
                raw_event = RawEvent(**event_data)
                message = raw_event.model_dump()
                await producer.send_and_wait(output_topic, json.dumps(message).encode('utf-8'))
                print(f"[INGESTION]: Routed event {raw_event.event_id} to topic '{output_topic}'")
            except Exception as e:
                print(f"[INGESTION-ERROR]: Failed to process message. Error: {e}. Message: {msg.value.decode('utf-8')}")
    except Exception as e:
        print(f"[INGESTION-ERROR]: Critical error in consumer loop: {e}")
    finally:
        await consumer.stop()
        await producer.stop()
        print("[INGESTION]: Agent stopped.")

if __name__ == "__main__":
    asyncio.run(main())

