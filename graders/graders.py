"""Flat grader registry for submission checkers that scan a single file."""

GRADERS = [
    {
        "task_id": "helpdesk_takeover",
        "id": "helpdesk_takeover",
        "enabled": True,
        "type": "deterministic",
        "score_range": [0.0, 1.0],
    },
    {
        "task_id": "privilege_spiral",
        "id": "privilege_spiral",
        "enabled": True,
        "type": "deterministic",
        "score_range": [0.0, 1.0],
    },
    {
        "task_id": "lateral_breach",
        "id": "lateral_breach",
        "enabled": True,
        "type": "deterministic",
        "score_range": [0.0, 1.0],
    },
]
