
"""Tests for rejected-event database operations."""

import json
from unittest.mock import MagicMock, patch

from decision_intelligence.streaming.database import save_rejected_event


def run_save(event, errors, result):
    mock_connection = MagicMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = result
    mock_connection.execute.return_value = mock_result

    with patch(
        "decision_intelligence.streaming.database.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value.__enter__.return_value = (
            mock_connection
        )
        inserted = save_rejected_event(event, errors)

    return inserted, mock_connection


def test_save_rejected_event_stores_payload_and_reasons():
    event = {"event_id": "invalid-test-001", "amount": -50}
    errors = ["amount cannot be negative."]

    inserted, connection = run_save(event, errors, (1,))

    assert inserted is True
    query, parameters = connection.execute.call_args.args
    assert "INSERT INTO rejected_events" in query
    assert parameters[0] == "invalid-test-001"
    assert json.loads(parameters[1]) == event
    assert parameters[2] == errors


def test_duplicate_rejected_event_returns_false():
    event = {"event_id": "invalid-test-002", "amount": -50}

    inserted, connection = run_save(
        event, ["amount cannot be negative."], None
    )

    assert inserted is False
    query, _ = connection.execute.call_args.args
    assert "ON CONFLICT" in query


def test_rejected_event_without_id_can_be_saved():
    event = {"amount": -50}

    inserted, connection = run_save(
        event, ["Missing event ID."], (2,)
    )

    assert inserted is True
    _, parameters = connection.execute.call_args.args
    assert parameters[0] is None
    assert json.loads(parameters[1]) == event
