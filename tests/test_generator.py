from decision_intelligence.generate import generate_events

def test_generator_is_reproducible():
    a = generate_events(500, seed=7, inject_issues=False)
    b = generate_events(500, seed=7, inject_issues=False)
    assert len(a) == 500
    assert list(a.columns) == list(b.columns)
    assert a["event_id"].equals(b["event_id"])
    assert a["event_type"].equals(b["event_type"])
