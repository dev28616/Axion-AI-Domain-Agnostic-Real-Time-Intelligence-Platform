import asyncio
import json
import joblib
import numpy as np
import aiohttp
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.kafka_client import get_kafka_producer, get_kafka_consumer
from core.schemas import RawEvent, CleanedEvent, AnalyticsResult

MODEL_SERVER_URL = "http://model_server:8000"
domain_model = None

async def enrich_event(session, event: RawEvent, log_prefix: str) -> tuple:
    text_for_embedding = f"Value: {event.event_value}. Source: {event.source_name}. Description: {event.description}"
    mask_task = session.post(f"{MODEL_SERVER_URL}/mask_pii", json={"text": event.description})
    vector_task = session.post(f"{MODEL_SERVER_URL}/vectorize", json={"text": text_for_embedding})
    responses = await asyncio.gather(mask_task, vector_task)
    for response in responses:
        if not response.ok:
            error_text = await response.text()
            print(f"[{log_prefix}-ERROR]: API call to Model Server failed with status {response.status}. Response: {error_text}")
            response.raise_for_status()
    mask_result = await responses[0].json()
    vector_result = await responses[1].json()
    return mask_result["masked_text"], vector_result["vector"]

def get_prediction(event: CleanedEvent) -> float:
    if domain_model is None: raise Exception("Domain model is not loaded.")
    hour = int(event.timestamp.split("T")[1].split(":")[0])
    features = np.array([[event.event_value, hour]])
    if hasattr(domain_model, 'predict_proba'):
        score = domain_model.predict_proba(features)[0, 1]
    else:
        raw_score = domain_model.decision_function(features)[0]
        score = 1 - (max(raw_score, 0))
    return round(score, 4)

async def main(config):
    global domain_model
    consumer, producer, session = None, None, None
    log_prefix = config.GROUP_ENRICHMENT
    try:
        raw_topic = config.TOPIC_RAW_EVENTS
        analytics_topic = config.TOPIC_ANALYTICS_RESULTS
        model_path = config.MODEL_PATH
        domain_model = joblib.load(model_path)
        consumer = await get_kafka_consumer(raw_topic, log_prefix)
        producer = await get_kafka_producer()
        session = aiohttp.ClientSession()
        print(f"[{log_prefix}]: Unified Enrichment Agent is running. Listening to topic '{raw_topic}'.")
        async for msg in consumer:
            raw_data = json.loads(msg.value.decode('utf-8'))
            raw_event = RawEvent(**raw_data)
            masked_description, vector_embedding = await enrich_event(session, raw_event, log_prefix)
            cleaned_event = CleanedEvent(event_id=raw_event.event_id, source_id=raw_event.source_id, event_value=float(raw_event.event_value), source_name=raw_event.source_name, description=masked_description, timestamp=raw_event.timestamp)
            score = get_prediction(cleaned_event)
            analytics_result = AnalyticsResult(event=cleaned_event, score=score, vector_embedding=vector_embedding)
            result_message = analytics_result.model_dump()
            await producer.send_and_wait(analytics_topic, json.dumps(result_message).encode('utf-8'))
            print(f"[{log_prefix}]: Enriched event: {cleaned_event.event_id} -> Score: {score}")
    except Exception as e:
        print(f"[{log_prefix}-ERROR]: A critical error occurred: {e}")
    finally:
        if session: await session.close()
        if consumer: await consumer.stop()
        if producer: await producer.stop()
        print(f"[{log_prefix}]: Enrichment Agent stopped.")

if __name__ == "__main__":
    class DummyConfig: pass
    asyncio.run(main(DummyConfig()))

