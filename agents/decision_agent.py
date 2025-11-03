# decision_agent.py
import asyncio
import json
import os
import time
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:29092")
GROUP_ID = os.getenv("DECISION_GROUP", "axion-decision-group")
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "0.5"))

async def process_message(producer, msg_value):
    """
    msg_value is expected to be a dict with:
      {"domain": "<domain>", "data": { ... enriched event ... }}
    enriched event should contain at least: event_id, score
    """
    try:
        domain = msg_value.get("domain") or "generic"
        data = msg_value.get("data", {})
        event_id = data.get("event_id", "unknown")
        score = float(data.get("score", 0))

        # Simple decision rule — customize per domain if needed later
        if score >= SCORE_THRESHOLD:
            decision = "ALERT"
            reason = f"score >= {SCORE_THRESHOLD}"
        else:
            decision = "APPROVED"
            reason = f"score < {SCORE_THRESHOLD}"

        decision_message = {
            "event_id": event_id,
            "domain": domain,
            "decision": decision,
            "score": score,
            "reason": reason,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

        topic_out = f"{domain}-decisions"
        await producer.send_and_wait(topic_out, json.dumps(decision_message).encode("utf-8"))
        print(f"[DECISION-{domain}]: Produced decision for {event_id} -> {decision} (score={score})")
    except Exception as e:
        print(f"[DECISION-ERROR]: Failed to process message: {e}", flush=True)


async def consume_loop():
    # subscribe to any topic that ends with "-enriched-events"
    # aiokafka Consumer supports subscribe(pattern=...), so we use regex
    consumer = AIOKafkaConsumer(
        bootstrap_servers=KAFKA_BROKER,
        group_id=GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
    )
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BROKER)

    await consumer.start()
    await producer.start()
    try:
        # use a regex to capture "<domain>-enriched-events"
        await consumer.subscribe(pattern=r".*-enriched-events")
        print("[DECISION]: Subscribed to pattern '.*-enriched-events' and waiting for messages.")
        async for msg in consumer:
            try:
                payload = msg.value
            except Exception as e:
                print(f"[DECISION-ERROR]: invalid message: {e}")
                continue
            await process_message(producer, payload)
    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(consume_loop())
