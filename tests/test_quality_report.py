
from scripts.quality_report import calculate_rejection_rate


def test_rejection_rate_with_rejected_events():
    assert calculate_rejection_rate(10, 2) == 16.666666666666664


def test_rejection_rate_with_no_rejected_events():
    assert calculate_rejection_rate(10, 0) == 0.0


def test_rejection_rate_with_no_events():
    assert calculate_rejection_rate(0, 0) == 0.0


def test_rejection_rate_with_only_rejected_events():
    assert calculate_rejection_rate(0, 5) == 100.0
