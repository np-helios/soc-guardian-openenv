"""Explicit grader registry for platform-side task discovery."""

from simulator import HIDDEN_TARGETS


def _grader(task_name: str) -> dict[str, object]:
    targets = HIDDEN_TARGETS[task_name]
    return {
        "id": task_name,
        "type": "deterministic",
        "enabled": True,
        "score_range": [0.0, 1.0],
        "num_cases": len(targets),
    }


GRADERS = {
    "helpdesk_takeover": _grader("helpdesk_takeover"),
    "privilege_spiral": _grader("privilege_spiral"),
    "lateral_breach": _grader("lateral_breach"),
}


def list_graders() -> dict[str, dict[str, object]]:
    return GRADERS
