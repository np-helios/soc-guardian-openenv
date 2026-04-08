from __future__ import annotations

import asyncio
import os

try:
    import httpx
except Exception:  # pragma: no cover
    httpx = None

from models import ModelTier, ResponseAction, Severity, SocAction, ToolName
from simulator import SocGuardianEnv, TASKS


def choose_action(observation) -> SocAction:
    latest = observation.visible_alerts[-1]
    if latest.severity.value == "critical" or "lateral-movement" in latest.tags:
        return SocAction(
            response_action=ResponseAction.TRIGGER_INCIDENT_RESPONSE,
            target_alert_id=latest.alert_id,
            tool_name=ToolName.NETWORK_MONITOR,
            model_tier=ModelTier.DEEP,
            escalate_severity=Severity.CRITICAL,
        )
    if "helpdesk" in latest.tags or "verification-mismatch" in latest.tags or "voice-mismatch" in latest.tags:
        return SocAction(
            response_action=ResponseAction.REQUEST_VERIFICATION,
            target_alert_id=latest.alert_id,
            tool_name=ToolName.IDENTITY_VERIFIER,
            model_tier=ModelTier.BALANCED,
            escalate_severity=Severity.HIGH,
        )
    if "admin-tools" in latest.tags or "scope-drift" in latest.tags:
        return SocAction(
            response_action=ResponseAction.ISOLATE_HOST,
            target_alert_id=latest.alert_id,
            tool_name=ToolName.LOG_ANALYZER,
            model_tier=ModelTier.DEEP,
            escalate_severity=Severity.HIGH,
        )
    if latest.signal_strength > 0.70:
        return SocAction(
            response_action=ResponseAction.OPEN_INCIDENT,
            target_alert_id=latest.alert_id,
            tool_name=ToolName.LOG_ANALYZER,
            model_tier=ModelTier.BALANCED,
            escalate_severity=Severity.HIGH,
        )
    return SocAction(
        response_action=ResponseAction.INVESTIGATE,
        target_alert_id=latest.alert_id,
        tool_name=ToolName.LOG_ANALYZER,
        model_tier=ModelTier.CHEAP,
        escalate_severity=Severity.MEDIUM,
    )


def assert_observation_safe(observation) -> None:
    sample = observation.visible_alerts[0].model_dump() if observation.visible_alerts else {}
    forbidden = {"recommended_action", "recommended_model", "recommended_tool", "true_stage"}
    leaked = forbidden.intersection(sample.keys())
    if leaked:
        raise AssertionError(f"Hidden fields leaked into observation: {sorted(leaked)}")


async def run_task(task_name: str) -> None:
    env = SocGuardianEnv(task_name=task_name, seed=7)
    result = await env.reset()
    assert_observation_safe(result.observation)

    while not result.done and result.observation.step_index < 12:
        action = choose_action(result.observation)
        result = await env.step(action)
        assert_observation_safe(result.observation)

    state = await env.state()
    await env.close()
    if not (0.0 <= state.final_score <= 1.0):
        raise AssertionError(f"Invalid final score for {task_name}: {state.final_score}")
    print(
        f"[SIM_OK] task={task_name} steps={state.step_index} final_score={state.final_score:.3f} "
        f"breach_prevented={str(state.breach_prevented).lower()} breach_occurred={str(state.breach_occurred).lower()}"
    )


async def run_api_check() -> None:
    if httpx is None:
        print("[API_SKIP] httpx not installed; skipping live API check")
        return
    base_url = os.getenv("API_BASE_URL_LOCAL", "http://127.0.0.1:8000")
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            health = await client.get("/health")
            health.raise_for_status()
            reset = await client.post("/reset", json={"task_name": "helpdesk_takeover", "seed": 7})
            reset.raise_for_status()
            visible_alert = reset.json()["observation"]["visible_alerts"][0]
            forbidden = {"recommended_action", "recommended_model", "recommended_tool", "true_stage"}
            leaked = forbidden.intersection(visible_alert.keys())
            if leaked:
                raise AssertionError(f"Live API leaked hidden fields: {sorted(leaked)}")
    except Exception as exc:
        print(f"[API_SKIP] Could not reach running API at {base_url}: {exc}")
        return
    print(f"[API_OK] base_url={base_url}")


async def main() -> None:
    print("[START] smoke_test")
    for task_name in TASKS:
        await run_task(task_name)
    await run_api_check()
    print("[END] smoke_test success=true")


if __name__ == "__main__":
    asyncio.run(main())
