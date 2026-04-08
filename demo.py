from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from models import (
    ModelTier,
    ResponseAction,
    Severity,
    SocAction,
    ToolName,
)
from simulator import MODEL_PROFILES, TOOL_PROFILES


class DemoSocQueryRequest(BaseModel):
    query: str = Field(min_length=5)


class DemoSocDecision(BaseModel):
    action: SocAction
    rationale: List[str]


class DemoSocResponse(BaseModel):
    summary: str
    suggested_task: str
    decision: DemoSocDecision
    estimated_cost_units: float
    estimated_latency_ms: int


def _lowered(query: str) -> str:
    return query.lower().strip()


def route_demo_query(query: str) -> DemoSocResponse:
    text = _lowered(query)
    rationale: list[str] = []

    if any(word in text for word in ["password", "reset", "helpdesk", "caller", "verify"]):
        task = "helpdesk_takeover"
        tool = ToolName.IDENTITY_VERIFIER
        action_name = ResponseAction.REQUEST_VERIFICATION
        tier = ModelTier.BALANCED
        rationale.append("The query reads like a helpdesk-led identity problem.")
    elif any(word in text for word in ["admin", "permission", "privilege", "token", "access attempt"]):
        task = "privilege_spiral"
        tool = ToolName.LOG_ANALYZER
        action_name = ResponseAction.FLAG_ANOMALY
        tier = ModelTier.BALANCED
        rationale.append("The query hints at privilege misuse or suspicious admin access.")
    elif any(word in text for word in ["lateral", "multiple systems", "network", "spread", "east-west"]):
        task = "lateral_breach"
        tool = ToolName.NETWORK_MONITOR
        action_name = ResponseAction.TRIGGER_INCIDENT_RESPONSE
        tier = ModelTier.DEEP
        rationale.append("The query indicates spread across multiple internal systems.")
    elif any(word in text for word in ["compromise", "breach", "urgent", "cannot access"]):
        task = "lateral_breach"
        tool = ToolName.LOG_ANALYZER
        action_name = ResponseAction.OPEN_INCIDENT
        tier = ModelTier.DEEP
        rationale.append("The language implies a high-risk compromise that needs stronger reasoning.")
    else:
        task = "helpdesk_takeover"
        tool = ToolName.LOG_ANALYZER
        action_name = ResponseAction.INVESTIGATE
        tier = ModelTier.CHEAP
        rationale.append("The query appears low-context, so the demo starts with a cheap investigation path.")

    if any(word in text for word in ["urgent", "immediately", "critical", "blocked"]):
        rationale.append("Urgency terms push the route away from cheap deferral.")
        if tier == ModelTier.CHEAP:
            tier = ModelTier.BALANCED

    severity = Severity.CRITICAL if tier == ModelTier.DEEP else Severity.HIGH if tier == ModelTier.BALANCED else Severity.MEDIUM
    action = SocAction(
        response_action=action_name,
        target_alert_id=None,
        tool_name=tool,
        model_tier=tier,
        escalate_severity=severity,
        reasoning_note="demo_soc_router",
    )
    model = MODEL_PROFILES[tier]
    tool_profile = TOOL_PROFILES[tool]
    summary = (
        f"The demo would route this query into the {task} scenario, use the {tool.value} tool, "
        f"and ask the {tier.value} model tier to support a {action_name.value} decision."
    )
    return DemoSocResponse(
        summary=summary,
        suggested_task=task,
        decision=DemoSocDecision(action=action, rationale=rationale),
        estimated_cost_units=round(model.cost_units + tool_profile.cost_units, 3),
        estimated_latency_ms=model.latency_ms + tool_profile.latency_ms,
    )
