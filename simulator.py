from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import random

from models import (
    AlertRecord,
    HiddenScenarioTarget,
    ModelProfile,
    ModelTier,
    ResponseAction,
    Severity,
    SocAction,
    SocObservation,
    SocState,
    SocStepInfo,
    SocStepResult,
    Stage,
    ToolName,
    ToolProfile,
    VisibleAlert,
)


@dataclass(frozen=True)
class TaskConfig:
    name: str
    benchmark: str
    max_steps: int
    compute_budget: float
    latency_budget_ms: int
    analyst_notes: List[str]


TOOL_PROFILES: Dict[ToolName, ToolProfile] = {
    ToolName.NONE: ToolProfile(
        name=ToolName.NONE,
        cost_units=0.0,
        latency_ms=0,
        accuracy=0.0,
        summary="No supporting tool used.",
    ),
    ToolName.LOG_ANALYZER: ToolProfile(
        name=ToolName.LOG_ANALYZER,
        cost_units=1.2,
        latency_ms=350,
        accuracy=0.72,
        summary="Expands alert context from host, auth, and audit logs.",
    ),
    ToolName.IDENTITY_VERIFIER: ToolProfile(
        name=ToolName.IDENTITY_VERIFIER,
        cost_units=0.9,
        latency_ms=280,
        accuracy=0.84,
        summary="Checks whether the claimed user identity matches verification artifacts.",
    ),
    ToolName.NETWORK_MONITOR: ToolProfile(
        name=ToolName.NETWORK_MONITOR,
        cost_units=1.5,
        latency_ms=420,
        accuracy=0.80,
        summary="Surfaces east-west traffic anomalies and spread patterns.",
    ),
}


MODEL_PROFILES: Dict[ModelTier, ModelProfile] = {
    ModelTier.CHEAP: ModelProfile(
        tier=ModelTier.CHEAP,
        cost_units=0.8,
        latency_ms=280,
        reasoning_quality=0.58,
    ),
    ModelTier.BALANCED: ModelProfile(
        tier=ModelTier.BALANCED,
        cost_units=1.8,
        latency_ms=620,
        reasoning_quality=0.78,
    ),
    ModelTier.DEEP: ModelProfile(
        tier=ModelTier.DEEP,
        cost_units=3.8,
        latency_ms=1200,
        reasoning_quality=0.93,
    ),
}


TASKS: Dict[str, TaskConfig] = {
    "helpdesk_takeover": TaskConfig(
        name="helpdesk_takeover",
        benchmark="soc_guardian",
        max_steps=5,
        compute_budget=14.0,
        latency_budget_ms=5000,
        analyst_notes=[
            "Early identity verification should be rewarded heavily.",
            "Missing the takeover path should trigger a strong penalty.",
        ],
    ),
    "privilege_spiral": TaskConfig(
        name="privilege_spiral",
        benchmark="soc_guardian",
        max_steps=6,
        compute_budget=16.0,
        latency_budget_ms=6200,
        analyst_notes=[
            "Multiple low-signal alerts need to be correlated.",
            "Opening an incident too late should cost score and reward.",
        ],
    ),
    "lateral_breach": TaskConfig(
        name="lateral_breach",
        benchmark="soc_guardian",
        max_steps=7,
        compute_budget=18.0,
        latency_budget_ms=7200,
        analyst_notes=[
            "Hard mode mixes decoy activity with real lateral movement.",
            "Containment timing matters as much as correct classification.",
        ],
    ),
}


SCENARIO_ALERTS: Dict[str, List[AlertRecord]] = {
    "helpdesk_takeover": [
        AlertRecord(
            alert_id="hd-1",
            title="Unusual password reset request",
            stage_hint=Stage.SOCIAL_ENGINEERING,
            severity=Severity.MEDIUM,
            signal_strength=0.61,
            source="helpdesk",
            description="Caller requested urgent reset while failing one identity checkpoint.",
            affected_identity="amy.reed",
            tags=["password-reset", "verification-mismatch", "helpdesk"],
            observed_at="2026-04-07T09:00:00Z",
        ),
        AlertRecord(
            alert_id="hd-2",
            title="Login from unfamiliar geography",
            stage_hint=Stage.INITIAL_ACCESS,
            severity=Severity.HIGH,
            signal_strength=0.73,
            source="identity",
            description="Fresh login seen from a location not previously associated with the employee.",
            affected_identity="amy.reed",
            tags=["geo-anomaly", "new-ip", "identity"],
            observed_at="2026-04-07T09:08:00Z",
        ),
        AlertRecord(
            alert_id="hd-3",
            title="Access to unusual resort booking admin page",
            stage_hint=Stage.INITIAL_ACCESS,
            severity=Severity.MEDIUM,
            signal_strength=0.66,
            source="app-audit",
            description="Account navigated to privileged internal tooling not used in normal shifts.",
            affected_identity="amy.reed",
            tags=["unusual-app-access", "reservation-admin"],
            observed_at="2026-04-07T09:14:00Z",
        ),
    ],
    "privilege_spiral": [
        AlertRecord(
            alert_id="ps-1",
            title="Password reset request with voice mismatch",
            stage_hint=Stage.SOCIAL_ENGINEERING,
            severity=Severity.MEDIUM,
            signal_strength=0.58,
            source="helpdesk",
            description="Caller provided correct employee ID but failed verbal phrasing challenge.",
            affected_identity="jordan.kim",
            tags=["voice-mismatch", "password-reset"],
            observed_at="2026-04-07T10:01:00Z",
        ),
        AlertRecord(
            alert_id="ps-2",
            title="New privileged login from contractor subnet",
            stage_hint=Stage.INITIAL_ACCESS,
            severity=Severity.HIGH,
            signal_strength=0.74,
            source="identity",
            description="Successful login from an unmanaged subnet tied to a third-party vendor circuit.",
            affected_identity="jordan.kim",
            tags=["new-subnet", "identity"],
            observed_at="2026-04-07T10:11:00Z",
        ),
        AlertRecord(
            alert_id="ps-3",
            title="Repeated admin tool access attempts",
            stage_hint=Stage.PRIVILEGE_ESCALATION,
            severity=Severity.HIGH,
            signal_strength=0.79,
            source="iam",
            description="Three failed accesses to the hotel finance admin console followed by one success.",
            affected_identity="jordan.kim",
            affected_host="adm-bastion-2",
            tags=["admin-tools", "permission-misuse"],
            observed_at="2026-04-07T10:22:00Z",
        ),
        AlertRecord(
            alert_id="ps-4",
            title="Decoy: noisy slot telemetry jitter",
            stage_hint=Stage.INITIAL_ACCESS,
            severity=Severity.LOW,
            signal_strength=0.18,
            source="iot-monitor",
            description="Benign noise from a maintenance reboot on a gaming floor segment.",
            affected_host="slot-gw-9",
            tags=["noise", "iot"],
            observed_at="2026-04-07T10:24:00Z",
        ),
    ],
    "lateral_breach": [
        AlertRecord(
            alert_id="lb-1",
            title="Helpdesk override request outside policy",
            stage_hint=Stage.SOCIAL_ENGINEERING,
            severity=Severity.MEDIUM,
            signal_strength=0.62,
            source="helpdesk",
            description="Support override requested for an account whose manager is marked offline.",
            affected_identity="samir.patel",
            tags=["helpdesk", "override", "identity-check"],
            observed_at="2026-04-07T11:00:00Z",
        ),
        AlertRecord(
            alert_id="lb-2",
            title="Unusual login followed by reservation platform access",
            stage_hint=Stage.INITIAL_ACCESS,
            severity=Severity.HIGH,
            signal_strength=0.76,
            source="identity",
            description="New device login immediately pivoted into the reservations management plane.",
            affected_identity="samir.patel",
            affected_host="res-admin-1",
            tags=["new-device", "reservation-platform"],
            observed_at="2026-04-07T11:09:00Z",
        ),
        AlertRecord(
            alert_id="lb-3",
            title="Privileged service token request",
            stage_hint=Stage.PRIVILEGE_ESCALATION,
            severity=Severity.HIGH,
            signal_strength=0.82,
            source="iam",
            description="Service account token requested with scopes outside the employee's team profile.",
            affected_identity="samir.patel",
            affected_host="token-broker-1",
            tags=["service-token", "scope-drift"],
            observed_at="2026-04-07T11:20:00Z",
        ),
        AlertRecord(
            alert_id="lb-4",
            title="Rapid cross-system access burst",
            stage_hint=Stage.LATERAL_MOVEMENT,
            severity=Severity.CRITICAL,
            signal_strength=0.91,
            source="network",
            description="Identity touched billing, reservations, and loyalty systems within four minutes.",
            affected_identity="samir.patel",
            affected_host="east-west-core",
            tags=["lateral-movement", "cross-system", "network"],
            observed_at="2026-04-07T11:29:00Z",
        ),
        AlertRecord(
            alert_id="lb-5",
            title="Decoy: housekeeping tablet reconnect storm",
            stage_hint=Stage.INITIAL_ACCESS,
            severity=Severity.LOW,
            signal_strength=0.23,
            source="wifi",
            description="Benign reconnect burst caused by an AP firmware refresh.",
            affected_host="hk-tablet-pool",
            tags=["noise", "wifi", "iot"],
            observed_at="2026-04-07T11:31:00Z",
        ),
    ],
}


SCENARIO_TARGETS: Dict[str, Dict[str, HiddenScenarioTarget]] = {
    "helpdesk_takeover": {
        "hd-1": HiddenScenarioTarget(
            true_stage=Stage.SOCIAL_ENGINEERING,
            recommended_action=ResponseAction.REQUEST_VERIFICATION,
            recommended_tool=ToolName.IDENTITY_VERIFIER,
            recommended_model=ModelTier.BALANCED,
            expected_alert_ids=["hd-1"],
            incident_worthy=False,
            breach_stops_on_success=False,
        ),
        "hd-2": HiddenScenarioTarget(
            true_stage=Stage.INITIAL_ACCESS,
            recommended_action=ResponseAction.OPEN_INCIDENT,
            recommended_tool=ToolName.LOG_ANALYZER,
            recommended_model=ModelTier.BALANCED,
            expected_alert_ids=["hd-1", "hd-2"],
            incident_worthy=True,
            breach_stops_on_success=False,
        ),
        "hd-3": HiddenScenarioTarget(
            true_stage=Stage.INITIAL_ACCESS,
            recommended_action=ResponseAction.BLOCK_USER,
            recommended_tool=ToolName.LOG_ANALYZER,
            recommended_model=ModelTier.DEEP,
            expected_alert_ids=["hd-1", "hd-2", "hd-3"],
            incident_worthy=True,
            breach_stops_on_success=True,
        ),
    },
    "privilege_spiral": {
        "ps-1": HiddenScenarioTarget(
            true_stage=Stage.SOCIAL_ENGINEERING,
            recommended_action=ResponseAction.REQUEST_VERIFICATION,
            recommended_tool=ToolName.IDENTITY_VERIFIER,
            recommended_model=ModelTier.BALANCED,
            expected_alert_ids=["ps-1"],
            incident_worthy=False,
            breach_stops_on_success=False,
        ),
        "ps-2": HiddenScenarioTarget(
            true_stage=Stage.INITIAL_ACCESS,
            recommended_action=ResponseAction.FLAG_ANOMALY,
            recommended_tool=ToolName.LOG_ANALYZER,
            recommended_model=ModelTier.BALANCED,
            expected_alert_ids=["ps-1", "ps-2"],
            incident_worthy=False,
            breach_stops_on_success=False,
        ),
        "ps-3": HiddenScenarioTarget(
            true_stage=Stage.PRIVILEGE_ESCALATION,
            recommended_action=ResponseAction.ISOLATE_HOST,
            recommended_tool=ToolName.LOG_ANALYZER,
            recommended_model=ModelTier.DEEP,
            expected_alert_ids=["ps-2", "ps-3"],
            incident_worthy=True,
            breach_stops_on_success=True,
        ),
        "ps-4": HiddenScenarioTarget(
            true_stage=Stage.INITIAL_ACCESS,
            recommended_action=ResponseAction.IGNORE,
            recommended_tool=ToolName.NONE,
            recommended_model=ModelTier.CHEAP,
            expected_alert_ids=["ps-4"],
            incident_worthy=False,
            breach_stops_on_success=False,
        ),
    },
    "lateral_breach": {
        "lb-1": HiddenScenarioTarget(
            true_stage=Stage.SOCIAL_ENGINEERING,
            recommended_action=ResponseAction.REQUEST_VERIFICATION,
            recommended_tool=ToolName.IDENTITY_VERIFIER,
            recommended_model=ModelTier.BALANCED,
            expected_alert_ids=["lb-1"],
            incident_worthy=False,
            breach_stops_on_success=False,
        ),
        "lb-2": HiddenScenarioTarget(
            true_stage=Stage.INITIAL_ACCESS,
            recommended_action=ResponseAction.OPEN_INCIDENT,
            recommended_tool=ToolName.LOG_ANALYZER,
            recommended_model=ModelTier.BALANCED,
            expected_alert_ids=["lb-1", "lb-2"],
            incident_worthy=True,
            breach_stops_on_success=False,
        ),
        "lb-3": HiddenScenarioTarget(
            true_stage=Stage.PRIVILEGE_ESCALATION,
            recommended_action=ResponseAction.ESCALATE_TO_HUMAN,
            recommended_tool=ToolName.LOG_ANALYZER,
            recommended_model=ModelTier.DEEP,
            expected_alert_ids=["lb-2", "lb-3"],
            incident_worthy=True,
            breach_stops_on_success=False,
        ),
        "lb-4": HiddenScenarioTarget(
            true_stage=Stage.LATERAL_MOVEMENT,
            recommended_action=ResponseAction.TRIGGER_INCIDENT_RESPONSE,
            recommended_tool=ToolName.NETWORK_MONITOR,
            recommended_model=ModelTier.DEEP,
            expected_alert_ids=["lb-2", "lb-3", "lb-4"],
            incident_worthy=True,
            breach_stops_on_success=True,
        ),
        "lb-5": HiddenScenarioTarget(
            true_stage=Stage.INITIAL_ACCESS,
            recommended_action=ResponseAction.IGNORE,
            recommended_tool=ToolName.NONE,
            recommended_model=ModelTier.CHEAP,
            expected_alert_ids=["lb-5"],
            incident_worthy=False,
            breach_stops_on_success=False,
        ),
    },
}


class SocGuardianEnv:
    def __init__(self, task_name: str = "helpdesk_takeover", seed: int = 7):
        if task_name not in TASKS:
            raise ValueError(f"Unknown task: {task_name}")
        self.task_name = task_name
        self.seed = seed
        self._rng = random.Random(seed)
        self._config = TASKS[task_name]
        self._alerts = [alert.model_copy(deep=True) for alert in SCENARIO_ALERTS[task_name]]
        self._visible_count = 1
        self._current_alert: Optional[AlertRecord] = None
        self._state: Optional[SocState] = None

    async def reset(self) -> SocStepResult:
        self._config = TASKS[self.task_name]
        self._alerts = [alert.model_copy(deep=True) for alert in SCENARIO_ALERTS[self.task_name]]
        self._visible_count = 1
        self._current_alert = self._alerts[0]
        self._state = SocState(
            benchmark=self._config.benchmark,
            task_name=self.task_name,
            seed=self.seed,
            step_index=0,
            max_steps=self._config.max_steps,
            system_risk_level=0.30,
            attacker_progression_score=0.15,
            remaining_compute_budget=self._config.compute_budget,
            remaining_latency_budget_ms=self._config.latency_budget_ms,
            incident_open=False,
            incident_severity=None,
            cumulative_reward=0.0,
            cumulative_cost=0.0,
            cumulative_latency_ms=0,
            false_positive_count=0,
            false_negative_count=0,
            processed_alert_ids=[],
            remaining_alert_ids=[alert.alert_id for alert in self._alerts],
            previous_actions=[],
            hidden_targets={k: v.model_copy(deep=True) for k, v in SCENARIO_TARGETS[self.task_name].items()},
            breach_prevented=False,
            breach_occurred=False,
            final_score=0.0,
            scenario_notes={
                "setting": "hospitality_soc",
                "inspiration": "social-engineering-led enterprise intrusion",
            },
        )
        return SocStepResult(
            observation=self._make_observation(),
            reward=0.0,
            done=False,
            info=SocStepInfo(
                tool_used=ToolName.NONE,
                model_used=ModelTier.CHEAP,
                cost_incurred=0.0,
                latency_incurred_ms=0,
                detection_gain=0.0,
                false_positive_penalty=0.0,
                false_negative_penalty=0.0,
                early_detection_bonus=0.0,
                breach_prevented=False,
                incident_opened_correctly=False,
                grader_score=0.0,
                last_action_error=None,
            ),
        )

    async def step(self, action: SocAction) -> SocStepResult:
        if self._state is None or self._current_alert is None:
            raise RuntimeError("Environment must be reset before stepping.")

        alert = self._current_alert
        target = self._state.hidden_targets[alert.alert_id]
        tool = TOOL_PROFILES[action.tool_name]
        model = MODEL_PROFILES[action.model_tier]

        action_error: Optional[str] = None
        if action.tool_name != ToolName.NONE and action.response_action == ResponseAction.IGNORE:
            action_error = "Tool use is usually unnecessary when ignoring an alert."

        cost = tool.cost_units + model.cost_units
        latency = tool.latency_ms + model.latency_ms

        action_match = action.response_action == target.recommended_action
        tool_match = action.tool_name == target.recommended_tool
        model_match = action.model_tier == target.recommended_model
        target_in_scope = action.target_alert_id in {None, alert.alert_id}
        severity_match = (
            target.incident_worthy is False
            or action.escalate_severity in {Severity.HIGH, Severity.CRITICAL, None}
        )

        detection_gain = 0.0
        if action_match:
            detection_gain += 0.35
        if tool_match:
            detection_gain += 0.20
        if model_match:
            detection_gain += 0.15
        if target_in_scope:
            detection_gain += 0.08
        if severity_match:
            detection_gain += 0.05

        false_positive_penalty = 0.0
        false_negative_penalty = 0.0
        early_detection_bonus = 0.0
        incident_opened_correctly = False
        breach_prevented = False

        if target.incident_worthy and action.response_action == ResponseAction.IGNORE:
            false_negative_penalty += 1.10
            self._state.false_negative_count += 1
        if not target.incident_worthy and action.response_action in {
            ResponseAction.BLOCK_USER,
            ResponseAction.ISOLATE_HOST,
            ResponseAction.TRIGGER_INCIDENT_RESPONSE,
            ResponseAction.OPEN_INCIDENT,
        }:
            false_positive_penalty += 0.40
            self._state.false_positive_count += 1

        if action.response_action == ResponseAction.OPEN_INCIDENT and target.incident_worthy:
            incident_opened_correctly = True
            self._state.incident_open = True
            self._state.incident_severity = action.escalate_severity or alert.severity
            early_detection_bonus += max(0.0, 0.35 - (self._state.step_index * 0.05))
        elif action.response_action == ResponseAction.OPEN_INCIDENT:
            self._state.incident_open = True
            self._state.incident_severity = action.escalate_severity or Severity.MEDIUM

        if target.breach_stops_on_success and action_match and tool_match and model_match:
            breach_prevented = True
            self._state.breach_prevented = True
            early_detection_bonus += 0.90

        progression_delta = 0.12
        if action_match:
            progression_delta -= 0.10
        if tool_match:
            progression_delta -= 0.05
        if model_match:
            progression_delta -= 0.03
        if false_negative_penalty > 0:
            progression_delta += 0.18
        if action.response_action in {ResponseAction.BLOCK_USER, ResponseAction.ISOLATE_HOST, ResponseAction.TRIGGER_INCIDENT_RESPONSE} and not action_match:
            progression_delta += 0.08
        self._state.attacker_progression_score = min(max(self._state.attacker_progression_score + progression_delta, 0.0), 1.0)
        self._state.system_risk_level = min(max(self._state.system_risk_level + progression_delta * 0.85, 0.0), 1.0)

        reward = (
            (detection_gain * 1.2)
            + early_detection_bonus
            - false_positive_penalty
            - false_negative_penalty
            - (cost * 0.18)
            - (latency / 5000.0)
        )
        if action_error:
            reward -= 0.08

        grader_score = min(
            max(
                (0.40 * detection_gain)
                + (0.25 if incident_opened_correctly else 0.0)
                + (0.30 if breach_prevented else 0.0)
                - (0.20 * false_positive_penalty)
                - (0.30 * false_negative_penalty),
                0.0,
            ),
            1.0,
        )

        self._state.step_index += 1
        self._state.remaining_compute_budget -= cost
        self._state.remaining_latency_budget_ms -= latency
        self._state.cumulative_reward += reward
        self._state.cumulative_cost += cost
        self._state.cumulative_latency_ms += latency
        self._state.previous_actions.append(
            f"{action.response_action.value}:{alert.alert_id}:{action.tool_name.value}:{action.model_tier.value}"
        )
        self._state.processed_alert_ids.append(alert.alert_id)
        self._state.remaining_alert_ids = [a.alert_id for a in self._alerts[self._state.step_index :]]

        if self._state.step_index < len(self._alerts):
            self._visible_count = min(self._visible_count + 1, len(self._alerts))
            self._current_alert = self._alerts[self._state.step_index]

        breach_occurs = (
            self._state.attacker_progression_score >= 0.92
            or self._state.step_index >= self._config.max_steps
            or self._state.remaining_latency_budget_ms <= 0
            or self._state.remaining_compute_budget <= 0
        ) and not self._state.breach_prevented

        self._state.breach_occurred = breach_occurs

        done = breach_occurs or self._state.breach_prevented or self._state.step_index >= len(self._alerts)

        final_score = (
            0.45 * max(0.0, 1.0 - self._state.attacker_progression_score)
            + 0.20 * (1.0 if self._state.breach_prevented else 0.0)
            + 0.15 * max(0.0, self._state.remaining_compute_budget / self._config.compute_budget)
            + 0.10 * max(0.0, self._state.remaining_latency_budget_ms / self._config.latency_budget_ms)
            + 0.10 * grader_score
            - 0.10 * self._state.false_positive_count
            - 0.18 * self._state.false_negative_count
        )
        self._state.final_score = min(max(final_score, 0.0), 1.0)

        info = SocStepInfo(
            tool_used=action.tool_name,
            model_used=action.model_tier,
            cost_incurred=round(cost, 4),
            latency_incurred_ms=latency,
            detection_gain=round(detection_gain, 4),
            false_positive_penalty=round(false_positive_penalty, 4),
            false_negative_penalty=round(false_negative_penalty, 4),
            early_detection_bonus=round(early_detection_bonus, 4),
            breach_prevented=breach_prevented,
            incident_opened_correctly=incident_opened_correctly,
            grader_score=round(grader_score, 4),
            last_action_error=action_error,
        )
        return SocStepResult(
            observation=self._make_observation(),
            reward=round(reward, 4),
            done=done,
            info=info,
        )

    async def state(self) -> SocState:
        if self._state is None:
            raise RuntimeError("Environment must be reset before reading state.")
        return self._state.model_copy(deep=True)

    async def close(self) -> None:
        self._state = None
        self._current_alert = None
        self._visible_count = 1

    def _make_observation(self) -> SocObservation:
        if self._state is None:
            raise RuntimeError("Environment is not initialized.")
        visible_alerts = [self._to_visible(alert) for alert in self._alerts[: self._visible_count]]
        return SocObservation(
            benchmark=self._state.benchmark,
            task_name=self._state.task_name,
            step_index=self._state.step_index,
            max_steps=self._state.max_steps,
            visible_alerts=visible_alerts,
            system_risk_level=round(self._state.system_risk_level, 4),
            attacker_progression_score=round(self._state.attacker_progression_score, 4),
            remaining_compute_budget=round(self._state.remaining_compute_budget, 4),
            remaining_latency_budget_ms=self._state.remaining_latency_budget_ms,
            incident_open=self._state.incident_open,
            incident_severity=self._state.incident_severity,
            previous_actions=self._state.previous_actions[-5:],
            available_tools=[tool.model_copy(deep=True) for tool in TOOL_PROFILES.values()],
            available_models=[model.model_copy(deep=True) for model in MODEL_PROFILES.values()],
            analyst_notes=self._config.analyst_notes,
        )

    @staticmethod
    def _to_visible(alert: AlertRecord) -> VisibleAlert:
        return VisibleAlert(
            alert_id=alert.alert_id,
            title=alert.title,
            severity=alert.severity,
            signal_strength=alert.signal_strength,
            source=alert.source,
            description=alert.description,
            tags=alert.tags,
            observed_at=alert.observed_at,
        )
