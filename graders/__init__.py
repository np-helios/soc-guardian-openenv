"""Per-task deterministic grader metadata for SOC Guardian benchmark discovery."""

from .helpdesk_takeover import GRADER as HELPDESK_TAKEOVER_GRADER
from .lateral_breach import GRADER as LATERAL_BREACH_GRADER
from .privilege_spiral import GRADER as PRIVILEGE_SPIRAL_GRADER

GRADERS = {
    "helpdesk_takeover": HELPDESK_TAKEOVER_GRADER,
    "privilege_spiral": PRIVILEGE_SPIRAL_GRADER,
    "lateral_breach": LATERAL_BREACH_GRADER,
}
