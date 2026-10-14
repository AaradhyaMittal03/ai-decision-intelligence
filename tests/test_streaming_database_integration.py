
import os
import uuid

import pytest

from decision_intelligence.streaming.database import (
    create_events_table,
    get_connection,
    save_event,
)


@pytest.fixture
def database_ready():
    if os.getenv("RUN_DB_INTEGRATION_TESTS") != "1":
        pytest.skip("Set RUN_DB_INTEGRATION_TESTS=1 to run live DB tests")

    create_events_table()


def test_event_is_saved_and_duplicate_is_ignored(database_ready):
    event_id = f"integration-{uuid.uuid4()}"
    event = {
        "event_id": event_id,
        "event_type": "purchase",
        "user_id": "integration_test_user",
        "product_id": "integration_test_product",
        "amount": 42.50,
        "timestamp": "2026-10-10T12:00:00Z",
    }

    try:
        assert save_event(event) is True
        assert save_event(event) is False

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT event_id, amount
                FROM business_events
                WHERE event_id = %s
                """,
                (event_id,),
            ).fetchone()

        assert row is not None
        assert row[0] == event_id
        assert float(row[1]) == 42.50

    finally:
        with get_connection() as connection:
            connection.execute(
                "DELETE FROM business_events WHERE event_id = %s",
                (event_id,),
            )
