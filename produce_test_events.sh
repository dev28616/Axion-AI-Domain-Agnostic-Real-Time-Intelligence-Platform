#!/bin/bash

docker-compose exec -T kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic user-input-events <<EOF
{"domain": "finance", "data": {"event_id": "txn_101", "source_id": "atm-1", "event_value": "99.5", "source_name": "ATM", "description": "Withdrawal in Paris by John Doe", "timestamp": "2025-10-03T12:30:36+05:30"}}
{"domain": "logistics", "data": {"event_id": "ship_201", "source_id": "truck-9", "event_value": "1200", "source_name": "FleetTracker", "description": "Shipment from Delhi to Mumbai", "timestamp": "2025-10-03T12:45:00+05:30"}}
{"domain": "healthcare", "data": {"event_id": "pat_301", "source_id": "device-42", "event_value": "98.6", "source_name": "Thermometer", "description": "Patient Alice recorded fever", "timestamp": "2025-10-03T13:00:00+05:30"}}
EOF