import json
import csv
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError
import sys
import os

# Ensure the script can find the project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- THE CRITICAL FIX IS HERE ---
# When running inside a Docker container, we must use the service name 'kafka'
# and the internal port '29092' that we defined in our docker-compose.yml.
# 'localhost' would refer to the 'axion_agents' container itself.
KAFKA_BROKER_URL = "kafka:29092"
# -------------------------------

INPUT_TOPIC = "user-input-events"
DATA_FILE = "dsps/finance/data/transactions.csv"
DOMAIN = "finance"

def main():
    """
    Reads mock data from a CSV and produces it to the user-input-events topic,
    simulating a UI submission for end-to-end backend testing.
    """
    print("--- Starting Backend Test Data Injector for Finance DSP ---")
    
    try:
        # We use the synchronous client here for a simple, one-off script
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER_URL,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Kafka Producer connected successfully.")
    except KafkaError as e:
        print(f"FATAL: Failed to connect to Kafka. Please ensure the environment is running. Error: {e}")
        return

    try:
        print(f"Reading data from '{DATA_FILE}'...")
        with open(DATA_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Construct the message in the format the IngestionAgent expects
                message = {
                    "domain": DOMAIN,
                    "data": row
                }
                
                # Send the message
                producer.send(INPUT_TOPIC, value=message)
                print(f"Sent event: {row['event_id']}")
                time.sleep(2) # Simulate a delay between events for observability
        
        # Ensure all messages are sent before exiting
        producer.flush()
        print("\nAll test events have been sent to the pipeline.")

    except FileNotFoundError:
        print(f"FATAL: Data file not found at '{DATA_FILE}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        producer.close()
        print("--- Test Data Injector finished ---")


if __name__ == "__main__":
    main()