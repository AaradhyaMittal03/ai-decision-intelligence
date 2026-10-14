from decision_intelligence.streaming.database import (
    create_events_table,
    get_connection,
)


def main():
    create_events_table()

    with get_connection() as connection:
        row = connection.execute(
            "SELECT current_database(), current_user"
        ).fetchone()

    print(f"Connected successfully: database={row[0]}, user={row[1]}")
    print("Table business_events is ready.")


if __name__ == "__main__":
    main()
