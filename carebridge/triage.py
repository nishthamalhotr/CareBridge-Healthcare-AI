"""Transparent, deliberately limited rules for a non-diagnostic demo."""

from collections.abc import Iterable, Sequence
from typing import TypedDict


URGENT_TERMS = (
    "Severe trouble breathing",
    "Chest pain or pressure",
    "Sudden weakness, facial droop, or trouble speaking",
    "Uncontrolled bleeding",
    "Loss of consciousness or new severe confusion",
    "Severe allergic reaction with breathing or throat symptoms",
)
UNSURE_OPTION = "None of these / unsure"


class IntakeAssessment(TypedDict):
    urgent: bool
    matched_flags: list[str]
    message: str


def assess_intake(red_flags: Iterable[str] | None) -> IntakeAssessment:
    """Return conservative escalation copy; this is not a clinical assessment."""
    selected = set(red_flags or [])
    matches = sorted(selected.intersection(URGENT_TERMS))
    if matches:
        return {
            "urgent": True,
            "matched_flags": matches,
            "message": (
                "A warning sign was selected. Please seek emergency medical help now "
                "or contact your local emergency number. Do not rely on this app to assess urgency."
            ),
        }
    return {
        "urgent": False,
        "matched_flags": [],
        "message": (
            "This prototype did not identify one of its listed warning signs. "
            "That does not rule out an emergency or mean symptoms are harmless. "
            "Contact a qualified healthcare professional for guidance, especially if symptoms "
            "are severe, worsening, persistent, or worrying."
        ),
    }


def make_visit_summary(
    name: str,
    age_band: str,
    symptoms: str,
    duration: str,
    severity: str,
    red_flags: Sequence[str],
    medications: str,
    result: IntakeAssessment,
    *,
    impact: str = "",
    context: str = "",
    questions: str = "",
) -> str:
    """Create a plain-text summary for the user to review and share if they choose."""
    flags = ", ".join(result["matched_flags"]) if result["matched_flags"] else "None selected / unsure"
    lines = [
        "CAREBRIDGE — VISIT PREPARATION SUMMARY",
        "Educational prototype; not a diagnosis or medical advice.",
        "",
        f"Preferred name / initials: {name or 'Not provided'}",
        f"Age group: {age_band}",
        f"Symptoms described: {symptoms or 'Not provided'}",
        f"Duration: {duration}",
        f"Self-described severity: {severity}",
        f"Impact on daily activities: {impact or 'Not provided'}",
        f"What helps or worsens it: {context or 'Not provided'}",
        f"Warning signs selected: {flags}",
        f"Medicines / allergies to discuss: {medications or 'Not provided'}",
        "",
        f"App message: {result['message']}",
        "",
        "Questions or concerns to discuss:",
        questions or "Not provided",
    ]
    return "\n".join(lines)
