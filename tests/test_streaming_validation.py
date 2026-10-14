
from decision_intelligence.streaming.validation import validate_event


def valid_event():
    return {
        "event_id": "event-001",
        "event_type": "purchase",
        "user_id": "user_42",
        "product_id": "product_7",
        "amount": 149.99,
        "timestamp": "2026-10-10T08:30:00+00:00",
    }


def test_valid_event_passes():
    assert validate_event(valid_event()) == []


def test_missing_field_is_rejected():
    event = valid_event()
    del event["user_id"]

    errors = validate_event(event)

    assert any("Missing required fields" in error for error in errors)


def test_negative_amount_is_rejected():
    event = valid_event()
    event["amount"] = -10

    errors = validate_event(event)

    assert "amount cannot be negative." in errors


def test_unknown_event_type_is_rejected():
    event = valid_event()
    event["event_type"] = "unknown_event"

    errors = validate_event(event)

    assert "event_type is not supported." in errors


def test_invalid_timestamp_is_rejected():
    event = valid_event()
    event["timestamp"] = "not-a-date"

    errors = validate_event(event)

    assert "timestamp must be a valid ISO 8601 datetime." in errors
