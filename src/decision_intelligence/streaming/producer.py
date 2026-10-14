
"""Generate simulated business events and publish them to Kafka."""

import json
import os
import random
import time
import uuid
from datetime import datetime, timezone

from kafka import KafkaProducer

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "business-events")


def create_event():
    """Create one synthetic product analytics event."""
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": random.choice(
            ["page_view", "add_to_cart", "purchase", "signup"]
        ),
        "user_id": f"user_{random.randint(1, 1000)}",
        "product_id": f"product_{random.randint(1, 100)}",
        "amount": round(random.uniform(5, 500), 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        acks="all",
        retries=5,
    )

    try:
        for number in range(10):
            event = create_event()
            metadata = producer.send(TOPIC, value=event).get(timeout=10)
            print(
                f"Sent event {number + 1}/10: "
                f"type={event['event_type']}, "
                f"partition={metadata.partition}, "
                f"offset={metadata.offset}"
            )
            time.sleep(0.5)
    finally:
        producer.flush()
        producer.close()


if __name__ == "__main__":
    main()
