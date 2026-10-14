
"""Database operations for business and rejected events."""

import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


# --------------------------------------------------
# ENVIRONMENT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection():
    """Create and return a PostgreSQL connection."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "decision_intelligence"),
        user=os.getenv("DB_USER", "analytics_user"),
        password=os.getenv("DB_PASSWORD", ""),
    )


# --------------------------------------------------
# VALID BUSINESS EVENTS
# --------------------------------------------------

def create_events_table():
    """Create the table for valid business events."""
    sql = """
        CREATE TABLE IF NOT EXISTS business_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            user_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),
            event_timestamp TIMESTAMPTZ NOT NULL,
            received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """

    with get_connection() as connection:
        connection.execute(sql)


def save_event(event: dict) -> bool:
    """
    Save a valid business event.

    Return True if inserted, or False if the event already exists.
    """
    sql = """
        INSERT INTO business_events (
            event_id,
            event_type,
            user_id,
            product_id,
            amount,
            event_timestamp
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (event_id) DO NOTHING
        RETURNING event_id
    """

    with get_connection() as connection:
        result = connection.execute(
            sql,
            (
                event["event_id"],
                event["event_type"],
                event["user_id"],
                event["product_id"],
                event["amount"],
                event["timestamp"],
            ),
        ).fetchone()

    return result is not None


# --------------------------------------------------
# REJECTED EVENTS
# --------------------------------------------------

def create_rejected_events_table():
    """
    Create or upgrade the rejected-events table.

    Existing records are preserved. A usable event ID can only
    appear once in the rejected-events table.
    """
    sql = """
        CREATE TABLE IF NOT EXISTS rejected_events (
            id BIGSERIAL PRIMARY KEY,
            event_id TEXT,
            event_payload JSONB NOT NULL,
            rejection_reasons TEXT[] NOT NULL,
            rejected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """

    with get_connection() as connection:
        # Create the table if it does not already exist.
        connection.execute(sql)

        # Add the event_id column to an existing table if necessary.
        connection.execute(
            """
            ALTER TABLE rejected_events
            ADD COLUMN IF NOT EXISTS event_id TEXT
            """
        )

        # Recover event IDs from previously saved JSON payloads.
        connection.execute(
            """
            UPDATE rejected_events
            SET event_id = NULLIF(
                BTRIM(event_payload->>'event_id'),
                ''
            )
            WHERE event_id IS NULL
            """
        )

        # Create a unique index for non-null event IDs.
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
                idx_rejected_events_event_id_unique
            ON rejected_events (event_id)
            WHERE event_id IS NOT NULL
            """
        )


def save_rejected_event(event: dict, errors: list[str]) -> bool:
    """
    Save a rejected event and its validation errors.

    Return True if inserted, or False if an event with the same
    usable event ID has already been recorded.
    """
    event_id = event.get("event_id") if isinstance(event, dict) else None

    if not isinstance(event_id, str) or not event_id.strip():
        event_id = None
    else:
        event_id = event_id.strip()

    sql = """
        INSERT INTO rejected_events (
            event_id,
            event_payload,
            rejection_reasons
        )
        VALUES (%s, %s::jsonb, %s)
        ON CONFLICT (event_id) WHERE event_id IS NOT NULL
        DO NOTHING
        RETURNING id
    """

    with get_connection() as connection:
        result = connection.execute(
            sql,
            (
                event_id,
                json.dumps(event),
                errors,
            ),
        ).fetchone()

    return result is not None
