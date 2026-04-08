from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Stage(str, Enum):
    SOCIAL_ENGINEERING = "social_engineering"
    INITIAL_ACCESS = "initial_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    LATERAL_MOVEMENT = "lateral_movement"


class ResponseAction(str, Enum):
    IGNORE = "ignore"
    INVESTIGATE = "investigate"
    REQUEST_VERIFICATION = "request_verification"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    FLAG_ANOMALY = "flag_anomaly"
    BLOCK_USER = "block_user"
    ISOLATE_HOST = "isolate_host"
    TRIGGER_INCIDENT_RESPONSE = "trigger_incident_response"
    OPEN_INCIDENT = "open_incident"


class ToolName(str, Enum):
    NONE = "none"
    LOG_ANALYZER = "log_analyzer"
    IDENTITY_VERIFIER = "identity_verifier"
    NETWORK_MONITOR = "network_monitor"


class ModelTier(str, Enum):
    CHEAP = "cheap"
    BALANCED = "balanced"
    DEEP = "deep"


class AlertRecord(BaseModel):
    alert_id: str
    title: str
    stage_hint: Stage
    severity: Severity
    signal_strength: float = Field(ge=0.0, le=1.0)
    source: str
    description: str
    affected_identity: Optional[str] = None
    affected_host: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    observed_at: str


class VisibleAlert(BaseModel):
    alert_id: str
    title: str
    severity: Severity
    signal_strength: float = Field(ge=0.0, le=1.0)
    source: str
    description: str
    tags: List[str] = Field(default_factory=list)
    observed_at: str


class ToolProfile(BaseModel):
    name: ToolName
    cost_units: float = Field(ge=0.0)
    latency_ms: int = Field(ge=0)
    accuracy: float = Field(ge=0.0, le=1.0)
    summary: str


class ModelProfile(BaseModel):
    tier: ModelTier
    cost_units: float = Field(ge=0.0)
    latency_ms: int = Field(ge=0)
    reasoning_quality: float = Field(ge=0.0, le=1.0)


class HiddenScenarioTarget(BaseModel):
    true_stage: Stage
    recommended_action: ResponseAction
    recommended_tool: ToolName
    recommended_model: ModelTier
    expected_alert_ids: List[str]
    incident_worthy: bool = False
    breach_stops_on_success: bool = False


class SocObservation(BaseModel):
    benchmark: str
    task_name: str
    step_index: int
    max_steps: int
    visible_alerts: List[VisibleAlert]
    system_risk_level: float = Field(ge=0.0, le=1.0)
    attacker_progression_score: float = Field(ge=0.0, le=1.0)
    remaining_compute_budget: float
    remaining_latency_budget_ms: int
    incident_open: bool
    incident_severity: Optional[Severity] = None
    previous_actions: List[str] = Field(default_factory=list)
    available_tools: List[ToolProfile]
    available_models: List[ModelProfile]
    analyst_notes: List[str] = Field(default_factory=list)


class SocAction(BaseModel):
    response_action: ResponseAction
    target_alert_id: Optional[str] = None
    tool_name: ToolName = ToolName.NONE
    model_tier: ModelTier
    escalate_severity: Optional[Severity] = None
    reasoning_note: Optional[str] = None


class SocStepInfo(BaseModel):
    tool_used: ToolName
    model_used: ModelTier
    cost_incurred: float = Field(ge=0.0)
    latency_incurred_ms: int = Field(ge=0)
    detection_gain: float
    false_positive_penalty: float
    false_negative_penalty: float
    early_detection_bonus: float
    breach_prevented: bool
    incident_opened_correctly: bool
    grader_score: float = Field(ge=0.0, le=1.0)
    last_action_error: Optional[str] = None


class SocStepResult(BaseModel):
    observation: SocObservation
    reward: float
    done: bool
    info: SocStepInfo


class SocState(BaseModel):
    benchmark: str
    task_name: str
    seed: int
    step_index: int
    max_steps: int
    system_risk_level: float
    attacker_progression_score: float
    remaining_compute_budget: float
    remaining_latency_budget_ms: int
    incident_open: bool
    incident_severity: Optional[Severity] = None
    cumulative_reward: float
    cumulative_cost: float
    cumulative_latency_ms: int
    false_positive_count: int
    false_negative_count: int
    processed_alert_ids: List[str]
    remaining_alert_ids: List[str]
    previous_actions: List[str]
    hidden_targets: Dict[str, HiddenScenarioTarget]
    breach_prevented: bool = False
    breach_occurred: bool = False
    final_score: float = Field(ge=0.0, le=1.0)
    scenario_notes: Dict[str, str] = Field(default_factory=dict)
