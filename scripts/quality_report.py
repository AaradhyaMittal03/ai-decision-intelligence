"""Generate a data-quality report from PostgreSQL."""

from decision_intelligence.streaming.database import get_connection

def calculate_rejection_rate(valid_events, rejected_events):
    """Calculate the percentage of events that were rejected."""
    total_events = valid_events + rejected_events

    if total_events == 0:
        return 0.0

    return rejected_events / total_events * 100

def main():
    valid_query = """
        SELECT
            COUNT(*) AS total_events,
            COUNT(DISTINCT event_id) AS unique_events,
            COUNT(*) FILTER (
                WHERE user_id IS NULL OR user_id = ''
            ) AS missing_user_ids,
            COUNT(*) FILTER (
                WHERE amount < 0
            ) AS negative_amounts
        FROM business_events
    """

    event_types_query = """
        SELECT event_type, COUNT(*) AS total
        FROM business_events
        GROUP BY event_type
        ORDER BY total DESC
    """

    rejected_query = """
        SELECT
            COUNT(*) AS total_rejected,
            COUNT(*) FILTER (
                WHERE rejection_reasons IS NOT NULL
            ) AS events_with_reasons
        FROM rejected_events
    """

    rejection_reasons_query = """
        SELECT reason, COUNT(*) AS total
        FROM rejected_events,
             UNNEST(rejection_reasons) AS reason
        GROUP BY reason
        ORDER BY total DESC
    """

    with get_connection() as connection:
        valid = connection.execute(valid_query).fetchone()
        event_types = connection.execute(event_types_query).fetchall()
        rejected = connection.execute(rejected_query).fetchone()
        rejection_reasons = connection.execute(
            rejection_reasons_query
        ).fetchall()

    total_valid = valid[0]
    total_rejected = rejected[0]
    total_processed = total_valid + total_rejected

    rejection_rate = calculate_rejection_rate(
    total_valid,
    total_rejected
    )

    print("\n=== DATA QUALITY REPORT ===")
    print(f"Valid events:              {total_valid}")
    print(f"Unique valid event IDs:    {valid[1]}")
    print(f"Missing user IDs:          {valid[2]}")
    print(f"Negative stored amounts:   {valid[3]}")
    print(f"Rejected events:           {total_rejected}")
    print(f"Rejected events with reasons: {rejected[1]}")
    print(f"Rejection rate:            {rejection_rate:.2f}%")

    print("\n=== VALID EVENTS BY TYPE ===")
    for event_type, total in event_types:
        print(f"{event_type}: {total}")

    print("\n=== REJECTION REASONS ===")
    if rejection_reasons:
        for reason, total in rejection_reasons:
            print(f"{reason}: {total}")
    else:
        print("No rejected events found.")

    print("\nReport complete.")


if __name__ == "__main__":
    main()
