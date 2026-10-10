from decision_intelligence.analyst import answer_question

def test_unsupported_question_returns_helpful_message():
    result = answer_question("tell me a joke")
    assert result["intent"] == "unsupported"
    assert "Try:" in result["answer"]
