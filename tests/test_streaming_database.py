
from unittest.mock import MagicMock, patch

from decision_intelligence.streaming.database import save_event


def sample_event():
    return {
        "event_id": "event-test-001",
        "event_type": "purchase",
        "user_id": "user_123",
        "product_id": "product_456",
        "amount": 99.99,
        "timestamp": "2026-10-10T12:00:00Z",
    }


@patch("decision_intelligence.streaming.database.get_connection")
def test_save_event_returns_true_when_inserted(mock_get_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("event-test-001",)

    mock_connection.execute.return_value = mock_cursor
    mock_get_connection.return_value.__enter__.return_value = mock_connection

    result = save_event(sample_event())

    assert result is True
    mock_connection.execute.assert_called_once()


@patch("decision_intelligence.streaming.database.get_connection")
def test_save_event_returns_false_for_duplicate(mock_get_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None

    mock_connection.execute.return_value = mock_cursor
    mock_get_connection.return_value.__enter__.return_value = mock_connection

    result = save_event(sample_event())

    assert result is False
    mock_connection.execute.assert_called_once()
