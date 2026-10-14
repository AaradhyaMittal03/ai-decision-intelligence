
"""Validate business events before processing them."""

from datetime import datetime

ALLOWED_EVENT_TYPES = {
    "page_view",
    "add_to_cart",
    "purchase",
    "signup",
}

REQUIRED_FIELDS = {
    "event_id",
    "event_type",
    "user_id",
    "product_id",
    "amount",
    "timestamp",
}


def validate_event(event: dict) -> list[str]:
    """Return a list of validation errors; an empty list means valid."""
    if not isinstance(event, dict):
        return ["Event must be a dictionary."]

    errors = []

    missing_fields = REQUIRED_FIELDS - event.keys()
    if missing_fields:
        errors.append(
            f"Missing required fields: {', '.join(sorted(missing_fields))}"
        )

    if missing_fields:
        return errors

    if not isinstance(event["event_id"], str) or not event["event_id"].strip():
        errors.append("event_id must be a non-empty string.")

    if event["event_type"] not in ALLOWED_EVENT_TYPES:
        errors.append("event_type is not supported.")

    if not isinstance(event["user_id"], str) or not event["user_id"].strip():
        errors.append("user_id must be a non-empty string.")

    if not isinstance(event["product_id"], str) or not event["product_id"].strip():
        errors.append("product_id must be a non-empty string.")

    amount = event["amount"]
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        errors.append("amount must be a number.")
    elif amount < 0:
        errors.append("amount cannot be negative.")

    if not isinstance(event["timestamp"], str):
        errors.append("timestamp must be a string.")
    else:
        try:
            datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            errors.append("timestamp must be a valid ISO 8601 datetime.")

    return errors
