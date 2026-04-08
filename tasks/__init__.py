"""Per-task metadata for SOC Guardian benchmark discovery."""

from .helpdesk_takeover import TASK as HELPDESK_TAKEOVER_TASK
from .lateral_breach import TASK as LATERAL_BREACH_TASK
from .privilege_spiral import TASK as PRIVILEGE_SPIRAL_TASK

TASKS = [
    HELPDESK_TAKEOVER_TASK,
    PRIVILEGE_SPIRAL_TASK,
    LATERAL_BREACH_TASK,
]
