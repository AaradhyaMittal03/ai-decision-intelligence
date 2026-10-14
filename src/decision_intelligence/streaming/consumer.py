
"""Consume Kafka events and store valid and rejected events."""

import json
import os

from kafka import KafkaConsumer

from decision_intelligence.streaming.database import (
    create_events_table,
    create_rejected_events_table,
    save_event,
    save_rejected_event,
)
from decision_intelligence.streaming.validation import validate_event

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "business-events")


def main():
    # Create both database tables before consuming messages.
    create_events_table()
    create_rejected_events_table()

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id="decision-intelligence-consumer",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )

    accepted = 0
    rejected = 0
    stored = 0
    duplicates = 0

    print(f"Consuming events from Kafka topic: {TOPIC}")
    print("Valid events -> business_events")
    print("Invalid events -> rejected_events")
    print("Press Ctrl+C to stop.")

    try:
        for message in consumer:
            event = message.value
            errors = validate_event(event)

            if errors:
                # Save the rejected event and its validation errors.
                save_rejected_event(event, errors)
                rejected += 1

                print(
                    f"REJECTED | partition={message.partition} "
                    f"offset={message.offset} | errors={errors}"
                )
            else:
                # Save valid events before committing the Kafka offset.
                was_inserted = save_event(event)
                accepted += 1

                if was_inserted:
                    stored += 1
                    print(
                        f"STORED | type={event['event_type']} "
                        f"user={event['user_id']} "
                        f"amount={event['amount']}"
                    )
                else:
                    duplicates += 1
                    print(f"DUPLICATE | event_id={event['event_id']}")

            print(
                f"Summary: accepted={accepted}, rejected={rejected}, "
                f"stored={stored}, duplicates={duplicates}"
            )

            # Commit only after the event has been handled successfully.
            consumer.commit()

    except KeyboardInterrupt:
        print("\nConsumer stopped.")
        print(
            f"Final summary: accepted={accepted}, rejected={rejected}, "
            f"stored={stored}, duplicates={duplicates}"
        )
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
