"""Flat task registry for submission checkers that scan a single file."""

TASKS = [
    {
        "id": "helpdesk_takeover",
        "difficulty": "easy",
        "description": "Social-engineering-led account takeover with suspicious password reset and login anomalies.",
        "grader": "helpdesk_takeover",
        "has_grader": True,
    },
    {
        "id": "privilege_spiral",
        "difficulty": "medium",
        "description": "Compromised identity reaches for admin tooling while benign alert noise competes for attention.",
        "grader": "privilege_spiral",
        "has_grader": True,
    },
    {
        "id": "lateral_breach",
        "difficulty": "hard",
        "description": "Multi-stage intrusion advances to lateral movement with cross-system traffic and a decoy alert.",
        "grader": "lateral_breach",
        "has_grader": True,
    },
]
