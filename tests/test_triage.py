import pytest

from carebridge.triage import URGENT_TERMS, assess_intake, make_visit_summary


@pytest.mark.parametrize("warning_sign", sorted(URGENT_TERMS))
def test_each_listed_warning_sign_triggers_urgent_message(warning_sign):
    result = assess_intake([warning_sign])
    assert result["urgent"] is True
    assert "emergency" in result["message"].lower()
    assert result["matched_flags"] == [warning_sign]


def test_no_selection_does_not_claim_safe():
    result = assess_intake([])
    assert result["urgent"] is False
    assert "does not rule out an emergency" in result["message"]


def test_non_warning_selection_does_not_trigger_urgent_message():
    result = assess_intake(["None of these / unsure"])
    assert result["urgent"] is False
    assert result["matched_flags"] == []


def test_multiple_warning_signs_are_reported_in_stable_order():
    selected = ["Chest pain or pressure", "Severe trouble breathing"]
    result = assess_intake(selected)
    assert result["urgent"] is True
    assert result["matched_flags"] == sorted(selected)


def test_warning_sign_takes_precedence_over_unsure_selection():
    result = assess_intake(["None of these / unsure", "Chest pain or pressure"])
    assert result["urgent"] is True
    assert result["matched_flags"] == ["Chest pain or pressure"]


def test_summary_contains_core_fields():
    result = assess_intake([])
    summary = make_visit_summary(
        name="AB", age_band="18–39", symptoms="Headache",
        duration="Started today", severity="Moderate", red_flags=[],
        medications="None reported", result=result,
        impact="Made it hard to focus",
        context="Rest seemed to help",
        questions="What details should I track?",
    )
    assert "Symptoms described: Headache" in summary
    assert "Impact on daily activities: Made it hard to focus" in summary
    assert "What helps or worsens it: Rest seemed to help" in summary
    assert "Questions or concerns to discuss:\nWhat details should I track?" in summary
    assert "Medicines / allergies to discuss: None reported" in summary


def test_summary_does_not_invent_missing_context_or_questions():
    summary = make_visit_summary(
        name="", age_band="Prefer not to say", symptoms="", duration="Not specified",
        severity="Mild", red_flags=[], medications="", result=assess_intake([]),
    )
    assert "Impact on daily activities: Not provided" in summary
    assert "What helps or worsens it: Not provided" in summary
    assert "Questions or concerns to discuss:\nNot provided" in summary
