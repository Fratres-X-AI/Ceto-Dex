from cetodex.evidence_contract import validate_gate_report, wrap_gate_report


def test_wrap_gate_report_minimal():
    report = wrap_gate_report(gate="test", passed=True, known_limits=["fixture"])
    assert report["passed"] is True
    assert validate_gate_report(report) == []


def test_invalid_confidence_rejected():
    try:
        wrap_gate_report(gate="test", passed=False, confidence=1.5)
        raised = False
    except ValueError:
        raised = True
    assert raised
