#!/bin/bash
# kafka-setup.sh
# This script creates all required topics for Axion AI

set -e

BROKER="kafka:29092"
REPLICATION=1
PARTITIONS=3

echo ">>> Waiting for Kafka to be ready..."
# Wait for Kafka to be ready using a more robust check
MAX_RETRIES=30
RETRY_INTERVAL=5

for i in $(seq 1 $MAX_RETRIES); do
    if timeout 5 kafka-topics --bootstrap-server $BROKER --list >/dev/null 2>&1; then
        echo "Kafka is ready!"
        break
    fi
    
    if [ $i -eq $MAX_RETRIES ]; then
        echo "Error: Kafka did not become ready in time"
        exit 1
    fi
    
    echo "Waiting for Kafka to be ready... (Attempt $i/$MAX_RETRIES)"
    sleep $RETRY_INTERVAL
done

echo ">>> Creating core topics..."
kafka-topics --create --if-not-exists \
  --bootstrap-server $BROKER \
  --replication-factor $REPLICATION \
  --partitions $PARTITIONS \
  --topic all-raw-events

echo ">>> Creating DSP topics..."
DOMAINS=("finance" "logistics" "healthcare")

for domain in "${DOMAINS[@]}"; do
  echo ">>> Creating topics for $domain"
  kafka-topics --create --if-not-exists \
    --bootstrap-server $BROKER \
    --replication-factor $REPLICATION \
    --partitions $PARTITIONS \
    --topic ${domain}-enriched-events

  kafka-topics --create --if-not-exists \
    --bootstrap-server $BROKER \
    --replication-factor $REPLICATION \
    --partitions $PARTITIONS \
    --topic ${domain}-decisions
done

echo ">>> Kafka topic setup complete."
