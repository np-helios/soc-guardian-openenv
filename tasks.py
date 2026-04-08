"""Explicit task registry for platform-side task discovery."""

TASKS = [
    {
        "id": "helpdesk_takeover",
        "difficulty": "easy",
        "description": "Social-engineering-led account takeover with suspicious password reset and login anomalies.",
        "has_grader": True,
        "grader_id": "helpdesk_takeover",
    },
    {
        "id": "privilege_spiral",
        "difficulty": "medium",
        "description": "Compromised identity reaches for admin tooling while benign alert noise competes for attention.",
        "has_grader": True,
        "grader_id": "privilege_spiral",
    },
    {
        "id": "lateral_breach",
        "difficulty": "hard",
        "description": "Multi-stage intrusion advances to lateral movement with cross-system traffic and a decoy alert.",
        "has_grader": True,
        "grader_id": "lateral_breach",
    },
]


def list_tasks() -> list[dict[str, object]]:
    return TASKS
